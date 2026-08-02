#!/usr/bin/env python3
"""Wikipedia infobox parser for Q-series label enrichment.
Parses markdown (from fetch_page tool) to extract: children, spouse, net_worth, occupation"""
import re, json, sys

def parse_infobox(markdown_text):
    """Extract structured data from Wikipedia markdown infobox."""
    result = {'children_count': None, 'spouse': None, 'net_worth': None, 'occupation': None, 'known_for': None}
    
    # Wikipedia infoboxes in markdown come as tables with key-value rows
    # Pattern: | Key | Value | or | Key |
    #                            | Value |
    
    lines = markdown_text.split('\n')
    
    # Find infobox table (starts with title line, then | --- | --- | separator)
    in_infobox = False
    infobox_lines = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('| ') and '---' in stripped:
            in_infobox = True
            continue
        if in_infobox:
            if stripped.startswith('| ') and not stripped.startswith('| ---'):
                infobox_lines.append(stripped)
            elif not stripped.startswith('|') and len(infobox_lines) > 0:
                break  # end of infobox
    
    # Parse key-value pairs
    # Format: | **Key** | Value |  or  | Key | Value |
    for i, line in enumerate(infobox_lines):
        # Remove leading | and split
        parts = [p.strip() for p in line.split('|') if p.strip()]
        if len(parts) >= 2:
            key = re.sub(r'\*\*|\[|\]|\(|\)', '', parts[0]).strip()
            val = re.sub(r'<[^>]+>', '', parts[1]).strip()
            val = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', val)  # links to text
            val = re.sub(r'\\[a-z]+', '', val)
            
            # Children extraction
            if key.lower() in ('children', 'issue'):
                # Count names/entries
                names = re.split(r'<br\s*/?>|,|and|&', val)
                names = [n.strip() for n in names if n.strip() and not n.strip().startswith('(')]
                result['children_count'] = len(names)
                if result['children_count'] == 0:
                    result['children_count'] = None  # ambiguous
            
            # Spouse
            if key.lower() in ('spouse', 'spouses', 'husband', 'wife'):
                # Check if contains dates (married) vs "none"
                if 'none' not in val.lower() and 'never married' not in val.lower():
                    result['spouse'] = 1 if val.strip() else None
                else:
                    result['spouse'] = 0
            
            # Net worth
            if 'net worth' in key.lower() or 'networth' in key.lower():
                # Try to extract numeric value
                nums = re.findall(r'\$?[\d,]+\.?\d*\s*(million|billion|trillion)?', val, re.IGNORECASE)
                if nums:
                    result['net_worth'] = val[:80]
            
            # Occupation
            if key.lower() == 'occupation' or key.lower() == 'occupations':
                result['occupation'] = val[:120]
            
            # Known for
            if key.lower() in ('known for', 'knownfor'):
                result['known_for'] = val[:120]
    
    # Also try opening paragraph for occupation clues if infobox didn't yield
    if not result['occupation']:
        for line in lines[:20]:
            if line.startswith('**') and 'was a' in line.lower():
                m = re.search(r'was an?\s+(.+?)(?:\.|,| who)', line)
                if m:
                    result['occupation'] = m.group(1)[:120]
                break
    
    return result


def extract_from_markdown(md):
    """Full extraction pipeline."""
    result = parse_infobox(md)
    
    # Additional: check for "had X children" in text
    if result['children_count'] is None:
        children_patterns = [
            r'had\s+(\w+)\s+children', r'had\s+(\d+)\s+child',
            r'father\s+of\s+(\w+)', r'mother\s+of\s+(\w+)',
        ]
        for pat in children_patterns:
            m = re.search(pat, md, re.IGNORECASE)
            if m:
                word = m.group(1)
                word_to_num = {'no': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10}
                if word.isdigit():
                    result['children_count'] = int(word)
                elif word.lower() in word_to_num:
                    result['children_count'] = word_to_num[word.lower()]
                break
    
    return result


if __name__ == '__main__':
    # Test with sample markdown
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            md = f.read()
        result = extract_from_markdown(md)
        print(json.dumps(result, indent=2))
    else:
        # Self-test
        test_md = """
| **Ludovic Halévy** |
| --- |
| Born | (1834-01-01)1 January 1834 |
| Occupation | Author, librettist |
| Children | Élie and Daniel |
        """
        result = parse_infobox(test_md)
        print("Test result:", json.dumps(result, indent=2))
        assert result['children_count'] == 2, f"Expected 2, got {result['children_count']}"
        assert result['occupation'] == 'Author, librettist'
        print("✅ Parser self-test passed!")

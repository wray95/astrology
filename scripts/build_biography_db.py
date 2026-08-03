#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════
BIOGRAPHY DATABASE BUILDER — All CSVs → JSON biographies
Saves every person as a structured JSON file in biographies/
═══════════════════════════════════════════════════════════════
"""
import csv, json, os, time, hashlib
from collections import Counter, defaultdict

BIO_DIR = 'biographies'
os.makedirs(BIO_DIR, exist_ok=True)

# ── CSV registry with column mappings ──
CSV_FILES = [
    {
        'path': '/home/user/uploads/academic_researcher_system_builder_600.csv',
        'sector': 'Academic/Research',
        'format': 'industry',
        'cols': {'name': 'Full Name', 'dob': 'Birth Date (YYYY-MM-DD)',
                 'city': 'Birth City', 'state': 'Birth State/Province (if applicable)',
                 'country': 'Birth Country', 'profession': 'Primary Profession',
                 'area': 'Primary Research Area', 'contrib': 'Major Contribution'}
    },
    {
        'path': '/home/user/uploads/writers_comics_books_movies_poems_600.csv',
        'sector': 'Creative/Writing',
        'format': 'industry',
        'cols': {'name': 'Full Name', 'dob': 'Birth Date (YYYY-MM-DD)',
                 'city': 'Birth City', 'state': 'Birth State/Province (if applicable)',
                 'country': 'Birth Country', 'profession': 'Primary Profession',
                 'area': 'Primary Research Area', 'contrib': 'Major Contribution'}
    },
    {
        'path': '/home/user/uploads/it_gaming_ai_tech_600.csv',
        'sector': 'Technology/Gaming/AI',
        'format': 'industry',
        'cols': {'name': 'Full Name', 'dob': 'Birth Date (YYYY-MM-DD)',
                 'city': 'Birth City', 'state': 'Birth State/Province (if applicable)',
                 'country': 'Birth Country', 'profession': 'Primary Profession',
                 'area': 'Primary Research Area', 'contrib': 'Major Contribution'}
    },
    {
        'path': '/home/user/uploads/hotels_shops_printing_press_600.csv',
        'sector': 'Hospitality/Retail',
        'format': 'industry',
        'cols': {'name': 'Full Name', 'dob': 'Birth Date (YYYY-MM-DD)',
                 'city': 'Birth City', 'state': 'Birth State/Province (if applicable)',
                 'country': 'Birth Country', 'profession': 'Primary Profession',
                 'area': 'Primary Research Area', 'contrib': 'Major Contribution'}
    },
    {
        'path': '/home/user/uploads/transport_export_cab_sales_delivery_600.csv',
        'sector': 'Transport/Logistics',
        'format': 'industry',
        'cols': {'name': 'Full Name', 'dob': 'Birth Date (YYYY-MM-DD)',
                 'city': 'Birth City', 'state': 'Birth State/Province (if applicable)',
                 'country': 'Birth Country', 'profession': 'Primary Profession',
                 'area': 'Primary Research Area', 'contrib': 'Major Contribution'}
    },
    {
        'path': '/home/user/uploads/academic_luxury_marketing_experts_600.csv',
        'sector': 'Marketing/Luxury',
        'format': 'industry',
        'cols': {'name': 'Full Name', 'dob': 'Birth Date (YYYY-MM-DD)',
                 'city': 'Birth City', 'state': 'Birth State/Province (if applicable)',
                 'country': 'Birth Country', 'profession': 'Primary Profession',
                 'area': 'Primary Research Area', 'contrib': 'Major Contribution'}
    },
    {
        'path': '/home/user/uploads/famous_consumer_researchers_brand_strategists_600.csv',
        'sector': 'Marketing/Consumer',
        'format': 'consumer',
        'cols': {'name': 'Name', 'dob': 'BirthDate',
                 'city': 'BirthCity', 'state': 'BirthStateProvince',
                 'country': 'BirthCountry', 'profession': 'PrimaryField',
                 'area': None, 'contrib': 'MainContribution'}
    },
    {
        'path': '/home/user/uploads/eminent_scholars_1900_onward.csv',
        'sector': 'Academic/Eminent Scholars',
        'format': 'scholars',
        'cols': {'name': 'Name', 'dob': 'BirthDate',
                 'city': 'BirthCity', 'state': 'BirthStateProvince',
                 'country': 'BirthCountry', 'profession': None,
                 'area': None, 'contrib': None}
    },
    {
        'path': '/home/user/uploads/q series every_career_in_the_world_150k.csv',
        'sector': 'Various',
        'format': 'careers',
        'cols': {'name': 'Full Name', 'dob': 'Birth Date (YYYY-MM-DD)',
                 'city': None, 'state': None,
                 'country': 'Country', 'profession': 'Profession',
                 'area': 'Career Sector', 'contrib': 'Key Contribution'}
    },
]

print("=" * 75)
print("  BIOGRAPHY DATABASE BUILDER")
print(f"  Target: {BIO_DIR}/")
print("=" * 75)

total = 0
errors = 0
index_rows = []
sector_counts = Counter()
t0 = time.time()

for csv_cfg in CSV_FILES:
    path = csv_cfg['path']
    basename = os.path.basename(path)
    cols = csv_cfg['cols']
    sector = csv_cfg['sector']
    
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception as e:
        print(f"  ❌ {basename}: {e}")
        continue
    
    batch_count = 0
    for row in rows:
        try:
            # Extract fields
            name = row.get(cols['name'], '').strip()
            dob = row.get(cols['dob'], '').strip()
            city = (row.get(cols['city'], '').strip() if cols.get('city') and row.get(cols['city']) else '')
            state = (row.get(cols['state'], '').strip() if cols.get('state') and row.get(cols['state']) else '')
            country = (row.get(cols['country'], '').strip() if cols.get('country') and row.get(cols['country']) else '')
            profession = (row.get(cols['profession'], '').strip() if cols.get('profession') and row.get(cols['profession']) else '')
            area = (row.get(cols['area'], '').strip() if cols.get('area') and row.get(cols['area']) else '')
            contrib = (row.get(cols['contrib'], '').strip() if cols.get('contrib') and row.get(cols['contrib']) else '')
            
            if not name or len(name) < 3:
                continue
            
            # Create unique filename: sector/ / first_letter / hash.json
            safe_name = ''.join(c if c.isalnum() or c in ' _-' else '_' for c in name)[:60]
            name_hash = hashlib.md5(name.encode()).hexdigest()[:8]
            first_letter = name[0].upper() if name[0].isalpha() else 'X'
            
            # Subdirectory by sector
            sector_dir = sector.replace('/', '_').replace(' ', '_')
            sub_dir = os.path.join(BIO_DIR, sector_dir, first_letter)
            os.makedirs(sub_dir, exist_ok=True)
            
            filename = f"{name_hash}_{safe_name[:40]}.json"
            filepath = os.path.join(sub_dir, filename)
            
            # Parse birth date
            dob_parsed = dob
            try:
                if '-' in dob:
                    parts = dob.split('-')
                    if len(parts) == 3:
                        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
                        dob_parsed = f"{y:04d}-{m:02d}-{d:02d}"
                elif '/' in dob:
                    parts = dob.split('/')
                    if len(parts) == 3 and len(parts[2]) == 4:
                        d, m, y = int(parts[0]), int(parts[1]), int(parts[2])
                        dob_parsed = f"{y:04d}-{m:02d}-{d:02d}"
            except:
                pass
            
            # Build biography
            bio = {
                'name': name,
                'birth_date': dob_parsed,
                'birth_place': {
                    'city': city,
                    'state': state,
                    'country': country,
                },
                'profession': profession,
                'research_area': area,
                'contribution': contrib,
                'career_sector': sector,
                'source': basename,
                'confidence': 'Synthetic' if any(c.isdigit() and int(c) > 0 for c in name.split()[-1:]) else 'Medium',
            }
            
            with open(filepath, 'w') as f:
                json.dump(bio, f, indent=2)
            
            # Index entry
            index_rows.append({
                'file': filepath,
                'name': name,
                'dob': dob_parsed,
                'sector': sector,
                'profession': profession,
                'source': basename,
            })
            
            batch_count += 1
            sector_counts[sector] += 1
            
        except Exception as e:
            errors += 1
    
    total += batch_count
    print(f"  ✅ {basename}: {batch_count} bios ({len(rows)} rows)")

t1 = time.time()

# ── SAVE MASTER INDEX ──
index_path = os.path.join(BIO_DIR, 'master_index.json')
with open(index_path, 'w') as f:
    json.dump({
        'total_biographies': total,
        'sectors': dict(sector_counts),
        'created': time.strftime('%Y-%m-%dT%H:%M:%S'),
        'entries': index_rows,
    }, f, indent=1)

# ── SAVE CSV VERSION ──
csv_path = os.path.join(BIO_DIR, 'master_index.csv')
with open(csv_path, 'w') as f:
    f.write('name,birth_date,career_sector,profession,source,file_path\n')
    for r in index_rows:
        f.write(f'"{r["name"]}","{r["dob"]}","{r["sector"]}","{r["profession"]}","{r["source"]}","{r["file"]}"\n')

# ── STATS ──
dir_count = 0; file_count = 0
for root, dirs, files in os.walk(BIO_DIR):
    file_count += len(files)
    dir_count += len(dirs)
file_count -= 2  # subtract index files

print(f"\n{'─'*75}")
print(f"  ✅ BIOGRAPHY DATABASE COMPLETE")
print(f"  Total biographies: {total:,}")
print(f"  Errors: {errors}")
print(f"  Time: {t1-t0:.0f}s")
print(f"  Directories: {dir_count}")
print(f"  JSON files: {file_count:,}")
print(f"  Sectors: {dict(sector_counts.most_common())}")
print(f"  📄 Master index: {index_path}")
print(f"  📄 CSV index: {csv_path}")
print(f"  Disk: {sum(os.path.getsize(os.path.join(r,f)) for r,_,fs in os.walk(BIO_DIR) for f in fs)/1024/1024:.0f} MB")

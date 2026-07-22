#!/usr/bin/env python3
"""
Vedic Astrology Chart Parser & Wealth/Career Analyzer
Extracts data from drikpanchang.com and generates comprehensive birth chart reports
Designed for use with Arena.ai
"""

import json
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict

@dataclass
class DegreeData:
    degrees: int
    minutes: int = 0
    seconds: int = 0
    
    @property
    def decimal(self) -> float:
        return self.degrees + (self.minutes / 60) + (self.seconds / 3600)
    
    @property
    def raw(self) -> str:
        return f"{self.degrees}°"

class PlanetaryDataParser:
    """Parse planetary position data from drikpanchang tables"""
    
    ZODIAC_SYMBOLS = {
        'Aries': '♈', 'Taurus': '♉', 'Gemini': '♊', 'Cancer': '♋',
        'Leo': '♌', 'Virgo': '♍', 'Libra': '♎', 'Scorpio': '♏',
        'Sagittarius': '♐', 'Capricorn': '♑', 'Aquarius': '♒', 'Pisces': '♓'
    }
    
    ZODIAC_SHORT = {
        'Aries': 'Ari', 'Taurus': 'Tau', 'Gemini': 'Gem', 'Cancer': 'Can',
        'Leo': 'Leo', 'Virgo': 'Vir', 'Libra': 'Lib', 'Scorpio': 'Sco',
        'Sagittarius': 'Sag', 'Capricorn': 'Cap', 'Aquarius': 'Aqu', 'Pisces': 'Pis'
    }
    
    PLANETS_SYMBOLS = {
        'Sun': '☉', 'Moon': '☽', 'Mars': '♂', 'Mercury': '☿',
        'Jupiter': '♃', 'Venus': '♀', 'Saturn': '♄', 'Rahu': '☬', 'Ketu': '☭'
    }
    
    # Vedic dignity data
    EXALTATION = {
        'Sun': ('Aries', 10), 'Moon': ('Taurus', 3), 'Mars': ('Capricorn', 28),
        'Mercury': ('Virgo', 15), 'Jupiter': ('Cancer', 5), 'Venus': ('Pisces', 27),
        'Saturn': ('Libra', 20)
    }
    
    DOMICILE = {
        'Sun': 'Leo', 'Moon': 'Cancer',
        'Mars': ['Aries', 'Scorpio'], 'Mercury': ['Gemini', 'Virgo'],
        'Jupiter': ['Sagittarius', 'Pisces'], 'Venus': ['Taurus', 'Libra'],
        'Saturn': ['Capricorn', 'Aquarius']
    }
    
    DEBILITATION = {
        'Sun': 'Libra', 'Moon': 'Scorpio', 'Mars': 'Cancer',
        'Mercury': 'Pisces', 'Jupiter': 'Capricorn', 'Venus': 'Virgo',
        'Saturn': 'Aries'
    }
    
    PLANETS = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn', 'Rahu', 'Ketu']
    HOUSES = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th', '11th', '12th']

    def __init__(self):
        pass

    def parse_degrees(self, degree_str: str) -> Optional[DegreeData]:
        """Parse degree string format: 4°, 17°, 2°"""
        if not degree_str:
            return None
        match = re.search(r'(\d+)°', degree_str)
        if match:
            return DegreeData(degrees=int(match.group(1)))
        return None

    def assess_strength(self, planet: str, sign: str, degree: Optional[DegreeData] = None) -> Dict:
        """Assess planetary dignity (strength) in Vedic astrology"""
        status, level, notes = 'neutral', 0, []
        
        # Check exaltation
        if planet in self.EXALTATION:
            ex_sign, ex_deg = self.EXALTATION[planet]
            if sign == ex_sign:
                status, level = 'exalted', 2
                notes.append(f'Exalted in {sign}')
                if degree and abs(degree.degrees - ex_deg) <= 2:
                    notes.append('⚡ Near exact exaltation!')
        
        # Check domicile (own sign)
        if planet in self.DOMICILE:
            dom_signs = self.DOMICILE[planet]
            if isinstance(dom_signs, list):
                if sign in dom_signs and level < 1:
                    status, level = 'strong', 1
                    notes.append(f'Own sign ({sign})')
            else:
                if sign == dom_signs and level < 1:
                    status, level = 'strong', 1
                    notes.append(f'Own sign ({sign})')
        
        # Check debilitation
        if planet in self.DEBILITATION:
            deb_sign = self.DEBILITATION[planet]
            if sign == deb_sign:
                status, level = 'debilitated', -2
                notes.append(f'⚠️ Debilitated in {sign}')
        
        return {'status': status, 'level': level, 'notes': notes}

    def determine_house(self, asc_sign: str, planet_sign: str) -> str:
        """Determine house position based on ascendant"""
        asc_idx = list(self.ZODIAC_SYMBOLS.keys()).index(asc_sign)
        planet_idx = list(self.ZODIAC_SYMBOLS.keys()).index(planet_sign)
        house_idx = (planet_idx - asc_idx) % 12
        return self.HOUSES[house_idx]

    def parse_chart_data(self, data: Dict) -> Dict:
        """Parse the verified birth chart JSON data"""
        result = {
            'birth_info': data['birth_details'],
            'ascendant': data['ascendant']['sign'],
            'navamsa': data.get('chart_summary', {}).get('navamsa', 'Unknown'),
            'planets': {},
            'strengths': {},
            'houses': {}
        }
        
        # Parse each planet
        for planet, planet_data in data.get('planets', {}).items():
            sign = planet_data.get('sign', 'Unknown')
            degrees = self.parse_degrees(planet_data.get('degrees', ''))
            house = planet_data.get('house') or self.determine_house(data['ascendant']['sign'], sign)
            
            result['planets'][planet] = {
                'sign': sign,
                'symbol': self.PLANETS_SYMBOLS.get(planet, '?'),
                'degrees': planet_data.get('degrees'),
                'degree_obj': degrees,
                'house': house
            }
            
            # Assess strength
            strength = self.assess_strength(planet, sign, degrees)
            result['strengths'][planet] = strength
            
            # Track house placements
            if house not in result['houses']:
                result['houses'][house] = []
            result['houses'][house].append(planet)
        
        return result

    def analyze_wealth_career(self, chart: Dict) -> Dict:
        """Analyze wealth and career indicators"""
        planets = chart['planets']
        strengths = chart['strengths']
        houses = chart['houses']
        
        # Key houses for wealth/career
        # 2nd = wealth, savings, family
        # 6th = service, debts, enemies
        # 10th = career, reputation, authority
        # 11th = income, gains, network
        
        analysis = {
            'wealth_indicators': [],
            'career_indicators': [],
            'positive_factors': [],
            'challenging_factors': [],
            'final_verdict': {}
        }
        
        # Check 2nd house (wealth)
        if '2nd' in houses:
            for planet in houses['2nd']:
                analysis['wealth_indicators'].append(f"{planets[planet]['symbol']} {planet} in 2nd house")
                if strengths[planet]['level'] > 0:
                    analysis['positive_factors'].append(f"{planet} ({strengths[planet]['status']}) = wealth potential")
        
        # Check 10th house (career)
        if '10th' in houses:
            for planet in houses['10th']:
                analysis['career_indicators'].append(f"{planets[planet]['symbol']} {planet} in 10th house")
                if strengths[planet]['level'] > 0:
                    analysis['positive_factors'].append(f"{planet} ({strengths[planet]['status']}) = career success")
                elif strengths[planet]['level'] < 0:
                    analysis['challenging_factors'].append(f"{planet} ({strengths[planet]['status']}) = career challenges")
        
        # Check 11th house (income)
        if '11th' in houses:
            for planet in houses['11th']:
                analysis['wealth_indicators'].append(f"{planets[planet]['symbol']} {planet} in 11th house")
                if strengths[planet]['level'] > 0:
                    analysis['positive_factors'].append(f"{planet} ({strengths[planet]['status']}) = income potential")
        
        # Check for key yogas
        # Mars + Rahu in 10th = strong entrepreneurship
        if '10th' in houses:
            has_mars = 'Mars' in houses['10th']
            has_rahu = 'Rahu' in houses['10th']
            if has_mars and has_rahu:
                analysis['positive_factors'].append("🔥 Mars + Rahu conjunction in 10th = ENTREPRENEURIAL ENERGY")
        
        # Moon + Venus = wealth through art/luxury
        moon_sign = planets.get('Moon', {}).get('sign', '')
        if moon_sign == 'Taurus':
            analysis['positive_factors'].append("🌙 Moon in Taurus = EXALTED = emotional intelligence, attraction, beauty")
        
        # Saturn in 11th = steady income
        saturn_house = planets.get('Saturn', {}).get('house', '')
        if saturn_house == '11th':
            analysis['positive_factors'].append("♄ Saturn in 11th = disciplined income, steady earnings")
        
        # Final verdict
        positive_count = len(analysis['positive_factors'])
        negative_count = len(analysis['challenging_factors'])
        
        if positive_count >= 4 and negative_count <= 1:
            analysis['final_verdict'] = {
                'wealth': 'COMFORTABLE',
                'status': 'BUSINESS MAN',
                'unemployed': False,
                'confidence': 'HIGH'
            }
        elif positive_count >= 2 and negative_count <= 2:
            analysis['final_verdict'] = {
                'wealth': 'MODERATE',
                'status': 'BUSINESS MAN or EMPLOYED',
                'unemployed': False,
                'confidence': 'MEDIUM'
            }
        else:
            analysis['final_verdict'] = {
                'wealth': 'UNCERTAIN',
                'status': 'NEEDS MORE ANALYSIS',
                'unemployed': None,
                'confidence': 'LOW'
            }
        
        return analysis

    def generate_report(self, data: Dict) -> Dict:
        """Generate complete birth chart report"""
        chart = self.parse_chart_data(data)
        wealth_career = self.analyze_wealth_career(chart)
        
        return {
            'birth_info': chart['birth_info'],
            'ascendant': chart['ascendant'],
            'navamsa': chart['navamsa'],
            'planetary_positions': chart['planets'],
            'planetary_strengths': chart['strengths'],
            'house_placements': chart['houses'],
            'wealth_career_analysis': wealth_career
        }

    def print_report(self, report: Dict):
        """Print formatted report"""
        print("=" * 80)
        print(f"🌟 VEDIC BIRTH CHART ANALYSIS")
        print("=" * 80)
        
        # Birth info
        bi = report['birth_info']
        print(f"\n📅 Date: {bi['date']}")
        print(f"⏰ Time: {bi['time']}")
        print(f"📍 Location: {bi['location']}")
        print(f"🌅 Ascendant: {report['ascendant']} ♈")
        print(f"🌙 Navamsa: {report['navamsa']}")
        
        # Planetary positions
        print("\n" + "=" * 80)
        print("🪐 PLANETARY POSITIONS")
        print("=" * 80)
        print(f"{'Planet':<10} {'Sign':<12} {'House':<6} {'Strength':<15} {'Notes'}")
        print("-" * 80)
        
        for planet, data in report['planetary_positions'].items():
            strength = report['planetary_strengths'].get(planet, {})
            strength_str = f"{strength.get('status', '?')} ({strength.get('level', 0)})"
            notes = ', '.join(strength.get('notes', [])[:2])
            print(f"{data['symbol']} {planet:<8} {data['sign']:<12} {data['house']:<6} {strength_str:<15} {notes}")
        
        # Wealth/Career Analysis
        wc = report['wealth_career_analysis']
        print("\n" + "=" * 80)
        print("💰 WEALTH & CAREER ANALYSIS")
        print("=" * 80)
        
        print("\n✅ POSITIVE FACTORS:")
        for factor in wc['positive_factors']:
            print(f"   • {factor}")
        
        if wc['challenging_factors']:
            print("\n⚠️ CHALLENGING FACTORS:")
            for factor in wc['challenging_factors']:
                print(f"   • {factor}")
        
        print("\n" + "-" * 40)
        verdict = wc['final_verdict']
        print(f"\n🎯 FINAL VERDICT:")
        print(f"   💼 Status: {verdict['status']}")
        print(f"   💰 Wealth: {verdict['wealth']}")
        print(f"   ❓ Unemployed: {'NO ✓' if not verdict.get('unemployed') else 'YES ⚠️'}")
        print(f"   📊 Confidence: {verdict['confidence']}")
        print("=" * 80)


def main():
    """Main execution"""
    # Load the verified birth chart data
    with open('verified_birth_chart_1997.json', 'r') as f:
        data = json.load(f)
    
    # Initialize parser
    parser = PlanetaryDataParser()
    
    # Generate report
    report = parser.generate_report(data)
    
    # Print formatted report
    parser.print_report(report)
    
    # Save report to file
    with open('final_analysis_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n✅ Report saved to: final_analysis_report.json")


if __name__ == "__main__":
    main()

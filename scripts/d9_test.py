#!/usr/bin/env python3
"""D9 Navamsa Calculator — Sidereal (Lahiri)"""
import math

SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo',
         'Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']

def navamsa_sign(sidereal_degree):
    """Convert sidereal degree to Navamsa sign.
    Each sign (30°) has 9 navamsas of 3°20' each.
    Navamsa 1 of any sign corresponds to the sign itself if it's a fiery sign
    (Aries, Leo, Sagittarius), then cycles through the trine signs."""
    sign_idx = int(sidereal_degree // 30)
    pos_in_sign = sidereal_degree % 30
    navamsa_num = int(pos_in_sign // (30.0/9))  # 0-8
    # Navamsa mapping: start from the sign's element group
    # Fire signs (0,4,8): Aries, Leo, Sag
    # Earth signs (1,5,9): Taurus, Virgo, Capricorn  
    # Air signs (2,6,10): Gemini, Libra, Aquarius
    # Water signs (3,7,11): Cancer, Scorpio, Pisces
    element_start = sign_idx % 3  # 0=fiery, 1=earthy, 2=airy (for first 4 signs)
    # Actually the standard rule: 1st navamsa = fiery sign, then cycle
    base = (sign_idx // 3) * 3  # which triplicity group
    # Navamsa counting from the appropriate cardinal sign
    nav_sign = (base + navamsa_num) % 12
    return nav_sign, navamsa_num

def compute_d9_from_signs_degrees(signs, degrees):
    """Given D1 signs and approximate degrees, compute D9 signs."""
    sign_bases = {
        'Aries':0,'Taurus':30,'Gemini':60,'Cancer':90,'Leo':120,'Virgo':150,
        'Libra':180,'Scorpio':210,'Sagittarius':240,'Capricorn':270,'Aquarius':300,'Pisces':330
    }
    d9 = {}
    vargottama = {}
    for planet, sign in signs.items():
        deg = degrees.get(planet, 15)  # default to midpoint if unknown
        sidereal = sign_bases.get(sign, 0) + deg
        d9_sign_idx, nav_num = navamsa_sign(sidereal)
        d9_sign = SIGNS[d9_sign_idx]
        d9[planet] = d9_sign
        vargottama[planet] = (sign == d9_sign)
    return d9, vargottama

def check_d9_parivartana(d1_signs, d9_signs):
    """Check if any two planets exchange signs in D9."""
    exchanges = []
    planets = list(d9_signs.keys())
    for i in range(len(planets)):
        for j in range(i+1, len(planets)):
            p1, p2 = planets[i], planets[j]
            s1, s2 = d9_signs.get(p1), d9_signs.get(p2)
            if s1 and s2 and s1 == d9_signs.get(p2) and s2 == d9_signs.get(p1):
                # Need: p1 is in sign ruled by p2, and p2 in sign ruled by p1
                # This requires sign rulership check
                pass  # Complex — skip for now, mark UNRESOLVED
    return exchanges

# ============================================================
# MAIN ANALYSIS
# ============================================================
if __name__ == '__main__':
    sign_bases = {
        'Aries':0,'Taurus':30,'Gemini':60,'Cancer':90,'Leo':120,'Virgo':150,
        'Libra':180,'Scorpio':210,'Sagittarius':240,'Capricorn':270,'Aquarius':300,'Pisces':330
    }
    
    # Test cases
    test_cases = [
        {
            'name': 'Shakira (5-loop)', 'ach': 9,
            'signs': {'Sun':'Capricorn','Moon':'Gemini','Mars':'Capricorn','Mercury':'Sagittarius',
                      'Jupiter':'Aries','Venus':'Pisces','Saturn':'Cancer','Rahu':'Libra','Ketu':'Aries'},
            'degrees': {'Sun':19,'Moon':26,'Mars':0,'Mercury':25,'Jupiter':28,'Venus':6,'Saturn':19,'Rahu':4,'Ketu':4},
            'loops': [['Saturn','Moon','Mercury','Jupiter','Mars']]
        },
        {
            'name': 'Stan Lee (5-loop)', 'ach': 8,
            'signs': {'Sun':'Sagittarius','Moon':'Aries','Mars':'Aquarius','Mercury':'Sagittarius',
                      'Jupiter':'Libra','Venus':'Scorpio','Saturn':'Virgo','Rahu':'Virgo','Ketu':'Pisces'},
            'degrees': {'Sun':13,'Moon':10,'Mars':19,'Mercury':25,'Jupiter':19,'Venus':4,'Saturn':26,'Rahu':1,'Ketu':1},
            'loops': [['Jupiter','Venus','Mars','Saturn','Mercury']]
        },
        {
            'name': 'Senith (5-loop)', 'ach': 4,
            'signs': {'Sun':'Cancer','Moon':'Sagittarius','Mars':'Virgo','Mercury':'Leo',
                      'Jupiter':'Scorpio','Venus':'Cancer','Saturn':'Pisces','Rahu':'Libra','Ketu':'Aries'},
            'degrees': {'Sun':21,'Moon':13,'Mars':16,'Mercury':2,'Jupiter':11,'Venus':17,'Saturn':0,'Rahu':6,'Ketu':6},
            'loops': [['Sun','Moon','Jupiter','Mars','Mercury']]
        },
        # Comparison: 2-loop successes
        {
            'name': 'Taylor Swift (2-loop, bond=100)', 'ach': 9,
            'signs': {'Sun':'Sagittarius','Moon':'Cancer','Mars':'Scorpio','Mercury':'Sagittarius',
                      'Jupiter':'Cancer','Venus':'Aquarius','Saturn':'Sagittarius','Rahu':'Aries','Ketu':'Libra'},
            'degrees': {'Sun':21,'Moon':15,'Mars':5,'Mercury':10,'Jupiter':20,'Venus':25,'Saturn':15,'Rahu':10,'Ketu':10},
            'loops': [['Mercury','Jupiter']]
        },
        # Comparison: no-loop success
        {
            'name': 'Leonardo DiCaprio (0-loop)', 'ach': 9,
            'signs': {'Sun':'Scorpio','Moon':'Libra','Mars':'Leo','Mercury':'Scorpio',
                      'Jupiter':'Sagittarius','Venus':'Scorpio','Saturn':'Gemini','Rahu':'Capricorn','Ketu':'Cancer'},
            'degrees': {'Sun':18,'Moon':3,'Mars':25,'Mercury':22,'Jupiter':8,'Venus':5,'Saturn':12,'Rahu':20,'Ketu':20},
            'loops': []
        },
    ]
    
    print("=" * 85)
    print("D9 (NAVAMSA) COMPUTATION — Shrinkala v1.0 Test")
    print("=" * 85)
    
    rulers = {
        'Aries':'Mars','Taurus':'Venus','Gemini':'Mercury','Cancer':'Moon',
        'Leo':'Sun','Virgo':'Mercury','Libra':'Venus','Scorpio':'Mars',
        'Sagittarius':'Jupiter','Capricorn':'Saturn','Aquarius':'Saturn','Pisces':'Jupiter'
    }
    
    for tc in test_cases:
        d9, varg = compute_d9_from_signs_degrees(tc['signs'], tc['degrees'])
        n_varg = sum(1 for v in varg.values() if v)
        
        print(f"\n{tc['name']} (ach={tc['ach']})")
        print(f"  {'Planet':10s} {'D1 Sign':14s} {'Deg':>5s} → {'D9 Sign':12s} {'Vargottama':>10s}")
        print(f"  {'-'*55}")
        for planet in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu']:
            d1 = tc['signs'].get(planet,'?')
            deg = tc['degrees'].get(planet,0)
            d9s = d9.get(planet,'?')
            v = 'YES' if varg.get(planet,False) else 'no'
            print(f"  {planet:10s} {d1:14s} {deg:4.0f}° → {d9s:12s} {v:>10s}")
        
        print(f"  Vargottama count: {n_varg}/9")
        print(f"  D1 loops: {tc['loops']}")
        
        # Check if D9 has Parivartana among the loop planets
        print(f"  D9 analysis: {'Needs full sign-rulership parivartana check' if tc['loops'] else 'No D1 loop'}")

    # Summary
    print(f"\n{'='*85}")
    print("PRELIMINARY FINDINGS")
    print(f"{'='*85}")
    print("""
1. D9 computation from approximate degrees uses mid-sign defaults.
   PRECISE D9 requires exact sidereal longitudes, not rounded degrees.

2. Vargottama count visible — can indicate whether D9 supports D1 strength.

3. Full D9 Parivartana check requires sign rulership mapping,
   which is complex for 5-planet chains.

4. The 5-loop cases show lower achievement but n=3 is insufficient.

LIMITATION: This dataset uses rounded degrees from astrodb_loops.json.
For proper D9 computation, we need exact planetary longitudes.
""")

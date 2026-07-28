#!/usr/bin/env python3
import io

def patch(path, repls):
    s = open(path, encoding="utf-8").read()
    for old, new in repls:
        assert old in s, f"NOT FOUND in {path}: {old[:60]}"
        s = s.replace(old, new, 1)
    open(path, "w", encoding="utf-8").write(s)
    print("patched", path)

# ---- matrix_dashboard.html ----
patch("/home/user/astrology/matrix_dashboard.html", [
    ('<tr><td class="dim">NRY</td><td class="a">none needed</td><td class="g">CONFIRMED (Rule 3)</td><td class="a">Pending (Venus)</td><td class="a">none needed</td></tr>',
     '<tr><td class="dim">NRY</td><td class="a">none needed</td><td class="a">Framework-dependent (bavishyavani R3 vs indastro/Reddit)</td><td class="a">Pending: Venus COMBUST blocks (indastro)</td><td class="a">none needed</td></tr>'),
    ('<span class="pill" style="background:#143d27;color:#9CFFBf;">NRY CONFIRMED</span>',
     '<span class="pill" style="background:#3d3414;color:#ffd86b;">NRY framework-dependent</span>'),
])

# ---- shrinkala_dashboard.html ----
patch("/home/user/astrology/shrinkala_dashboard.html", [
    ('<td class="a">NRY (bavishyavani R3); Reddit \u2260 neecha bhanga</td>',
     '<td class="a">NRY: bavishyavani R3 YES; indastro NO (dispositor not Kendra from Moon); Reddit \u2260 neecha bhanga</td>'),
    ('Jupiter debilitated; NRY via bavishyavani Rule 3. Peak Jupiter MD 2032.9+.',
     'Jupiter debilitated; NRY via bavishyavani Rule 3 (classical Parivartana) but indastro/Reddit do NOT confirm (dispositor Saturn not Kendra from Moon; exchange \u2260 cancellation). Peak Jupiter MD 2032.9+.'),
])
print("dashboards NRY-patched OK")

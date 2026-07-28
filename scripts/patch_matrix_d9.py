#!/usr/bin/env python3
p = "/home/user/astrology/matrix_dashboard.html"
s = open(p, encoding="utf-8").read()

# 1) Add D9 rows to the matrix table (after the "Foreign rank" row)
anchor = '<tr><td class="dim">Foreign rank</td><td>3</td><td>2 (job)</td><td>4</td><td>1 (settlement)</td></tr>'
assert anchor in s, "foreign rank row not found"
new_rows = anchor + '''
      <tr><td class="dim">D9 exchange (D1+D9)</td><td class="r">none (Venus&#8211;Mer BREAKS)</td><td class="g">Jup&#8211;Sat REPEATS + NEW Mars&#8211;Mer</td><td class="a">NEW Mer&#8211;Sun (Dharma&#8211;Karma)</td><td class="r">none</td></tr>
      <tr><td class="dim">D9 dignity / strength</td><td class="a">Strong (2 EX+2 OWN; Venus DEB)</td><td class="r">Weakest (Sun/Ven DEB; Sat VARG)</td><td class="a">Clean (Mars/Mer VARG; 0 DEB)</td><td class="g">STRONGEST (Mars EX+Mer/Jup/Sat OWN; Lagna VARG)</td></tr>
      <tr><td class="dim">Combined exchange rank</td><td class="a">3</td><td class="g">1 (repeats)</td><td class="a">2 (empowered)</td><td class="r">4 (none)</td></tr>'''
s = s.replace(anchor, new_rows, 1)

# 2) Add a D9 dignity bar chart after the Astrology-aptitude group
anchor2 = '''    <div class="metric"><div class="mlabel">Astrology aptitude</div>
      <div class="mrow"><span class="mname">P1 Bappa</span><div class="barwrap"><div class="bar" style="width:40%;background:var(--a)"></div></div></div>
      <div class="mrow"><span class="mname">P2 Upulakshi</span><div class="barwrap"><div class="bar" style="width:20%;background:var(--r)"></div></div></div>
      <div class="mrow"><span class="mname">P3 Senith</span><div class="barwrap"><div class="bar" style="width:100%;background:var(--g)"></div></div></div>
      <div class="mrow"><span class="mname">P4 Niromi</span><div class="barwrap"><div class="bar" style="width:60%;background:var(--a)"></div></div></div>
    </div>'''
d9_chart = anchor2 + '''
    <div class="metric"><div class="mlabel">D9 (navamsa) dignity / strength</div>
      <div class="mrow"><span class="mname">P1 Bappa</span><div class="barwrap"><div class="bar" style="width:80%;background:var(--a)"></div></div></div>
      <div class="mrow"><span class="mname">P2 Upulakshi</span><div class="barwrap"><div class="bar" style="width:40%;background:var(--r)"></div></div></div>
      <div class="mrow"><span class="mname">P3 Senith</span><div class="barwrap"><div class="bar" style="width:60%;background:var(--a)"></div></div></div>
      <div class="mrow"><span class="mname">P4 Niromi</span><div class="barwrap"><div class="bar" style="width:100%;background:var(--g)"></div></div></div>
    </div>
    <div class="metric"><div class="mlabel">Combined D1+D9 exchange-network rank</div>
      <div class="mrow"><span class="mname">P1 Bappa</span><div class="barwrap"><div class="bar" style="width:60%;background:var(--a)"></div></div></div>
      <div class="mrow"><span class="mname">P2 Upulakshi</span><div class="barwrap"><div class="bar" style="width:100%;background:var(--g)"></div></div></div>
      <div class="mrow"><span class="mname">P3 Senith</span><div class="barwrap"><div class="bar" style="width:80%;background:var(--a)"></div></div></div>
      <div class="mrow"><span class="mname">P4 Niromi</span><div class="barwrap"><div class="bar" style="width:20%;background:var(--r)"></div></div></div>
    </div>'''
s = s.replace(anchor2, d9_chart, 1)

# 3) Add a D1+D9 Parivartana/Shrinkala summary before "Order summaries"
anchor3 = '<h2>Order summaries</h2>'
d9_summary = '''  <h2>D1 + D9 Parivartana / Shrinkala (combined)</h2>
  <div class="cards">
    <div class="card"><div class="t">Exchange-network: P2 &gt; P3 &gt; P1 &gt; P4</div><div class="d">
      <span class="pill" style="background:#143d27;color:#9CFFBf;">P2 #1</span> only exchange that REPEATS in both charts (Jupiter&#8211;Saturn) + new Mars&#8211;Mercury.<br>
      <span class="pill" style="background:#3d3414;color:#ffd86b;">P3 #2</span> largest latent 5-loop + Mars/Mercury Vargottama + new Mer&#8211;Sun (9th/10th) D9 exchange.<br>
      <span class="pill" style="background:#3d3414;color:#ffd86b;">P1 #3</span> D1 Venus&#8211;Mercury BREAKS in D9 (Venus debilitated).<br>
      <span class="pill" style="background:#3d1a1a;color:#ff9a9a;">P4 #4</span> no exchange (wealth via dignity/yogas).</div></div>
    <div class="card"><div class="t">D9 dignity: P4 &gt; P1 &gt; P3 &gt; P2</div><div class="d">
      <span class="pill" style="background:#143d27;color:#9CFFBf;">P4 #1</span> Mars EX + Mer/Jup/Sat OWN + Vargottama Lagna (strongest navamsa).<br>
      <span class="pill" style="background:#143d27;color:#9CFFBf;">P1 #2</span> Sun/Jup EX + Mer/Sat OWN; Venus DEB.<br>
      <span class="pill" style="background:#3d3414;color:#ffd86b;">P3 #3</span> Mars/Mercury Vargottama; 0 DEB.<br>
      <span class="pill" style="background:#3d1a1a;color:#ff9a9a;">P2 #4</span> Sun/Venus DEB; only Saturn Vargottama.</div></div>
  </div>

'''
s = s.replace(anchor3, d9_summary + anchor3, 1)

open(p, "w", encoding="utf-8").write(s)
print("matrix_dashboard.html patched OK; length", len(s))

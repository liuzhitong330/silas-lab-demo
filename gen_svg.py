"""Generate PCA and Volcano inline SVGs for the Silas Lab AG screen demo."""
import math

def lcg(seed=42):
    s = seed & 0xFFFFFFFF
    while True:
        s = (1664525 * s + 1013904223) & 0xFFFFFFFF
        yield s / 0xFFFFFFFF

def norm(rng, mu=0, sigma=1):
    u1 = max(next(rng), 1e-9); u2 = next(rng)
    return mu + sigma * math.sqrt(-2*math.log(u1)) * math.cos(2*math.pi*u2)

# ─── PCA: wild strains clustered by anti-virus defense repertoire ─────────
W, H = 560, 330
L, R, T, B = 60, 542, 22, 250

def px(v): return L + (v+42)/80*(R-L)
def py(v): return B - (v+27)/52*(B-T)

rng = lcg(42)
# "susceptible" strains: sparse defense repertoire, tight cluster
susceptible = [(norm(rng,-24,5), norm(rng,2,7)) for _ in range(34)]
# "resistant" strains: redundant CRISPR+R-M+CBASS+PCD repertoire, broader spread
resistant = [(norm(rng,18,10), norm(rng,-2,12)) for _ in range(91)]

def in_pca(x,y): return L<=px(x)<=R and T<=py(y)<=B

r_circles = " ".join(
    f'<circle cx="{px(x):.1f}" cy="{py(y):.1f}" r="3.2" fill="rgba(205,70,70,.45)"/>'
    for x,y in resistant if in_pca(x,y))
s_circles = " ".join(
    f'<circle cx="{px(x):.1f}" cy="{py(y):.1f}" r="4.5" fill="rgba(55,112,185,.88)"/>'
    for x,y in susceptible if in_pca(x,y))

xt = " ".join(
    f'<line x1="{px(v):.0f}" y1="{B}" x2="{px(v):.0f}" y2="{B+4}" stroke="#bbb"/>'
    f'<text x="{px(v):.0f}" y="{B+15}" text-anchor="middle" font-size="10" fill="#999">{v}</text>'
    for v in [-40,-20,0,20,40])
yt = " ".join(
    f'<line x1="{L-4}" y1="{py(v):.0f}" x2="{L}" y2="{py(v):.0f}" stroke="#bbb"/>'
    f'<text x="{L-7}" y="{py(v)+3.5:.0f}" text-anchor="end" font-size="10" fill="#999">{v}</text>'
    for v in [-20,0,20])

pca = f"""<svg viewBox="0 0 {W} {H}" width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:{W}px;display:block;margin-top:.5rem">
<line x1="{L}" y1="{T}" x2="{L}" y2="{B}" stroke="#bbb"/>
<line x1="{L}" y1="{B}" x2="{R}" y2="{B}" stroke="#bbb"/>
{xt} {yt}
{r_circles}
{s_circles}
<circle cx="{R-150}" cy="{T+14}" r="5" fill="rgba(55,112,185,.88)"/>
<text x="{R-142}" y="{T+18}" font-size="11" fill="#333" font-family="system-ui,sans-serif">Phage-susceptible strains (n=34)</text>
<circle cx="{R-150}" cy="{T+31}" r="4" fill="rgba(205,70,70,.7)"/>
<text x="{R-142}" y="{T+35}" font-size="11" fill="#333" font-family="system-ui,sans-serif">Phage-resistant strains (n=91)</text>
<text x="{L+(R-L)//2}" y="{H-16}" text-anchor="middle" font-size="12" fill="#555" font-family="system-ui,sans-serif">PC1 (defense-repertoire richness, 41.2% var)</text>
<text x="11" y="{T+(B-T)//2}" text-anchor="middle" font-size="12" fill="#555" font-family="system-ui,sans-serif" transform="rotate(-90,11,{T+(B-T)//2})">PC2 (R-M / CBASS / PCD balance, 16.9% var)</text>
</svg>"""

# ─── Volcano: pooled AG screen — fitness (rescue of phage infectivity) ────
VW,VH = 560,350
VL,VR,VT,VB = 55,544,20,268

def vx(v): return VL + (v+8.5)/17*(VR-VL)
def vy(v): return VB - v/52*(VB-VT)
def in_vol(x,y): return VL<=vx(x)<=VR and VT<=vy(y)<=VB

rng2 = lcg(99)
ns_pts = [(norm(rng2,0,2.6), max(0,norm(rng2,.4,.5))) for _ in range(900)]
up_pts = [(1.1+abs(norm(rng2,0,1.6)), 1.4+abs(norm(rng2,7,9))) for _ in range(140)]
dn_pts = [(-1.1-abs(norm(rng2,0,1.3)), 1.4+abs(norm(rng2,6,8))) for _ in range(70)]

ns_svg = " ".join(
    f'<circle cx="{vx(x):.1f}" cy="{vy(y):.1f}" r="1.6" fill="rgba(150,150,150,.22)"/>'
    for x,y in ns_pts if in_vol(x,y))
dn_svg = " ".join(
    f'<circle cx="{vx(x):.1f}" cy="{vy(y):.1f}" r="2" fill="rgba(50,108,175,.5)"/>'
    for x,y in dn_pts if in_vol(x,y))
up_svg = " ".join(
    f'<circle cx="{vx(x):.1f}" cy="{vy(y):.1f}" r="2" fill="rgba(200,60,60,.5)"/>'
    for x,y in up_pts if in_vol(x,y))

# AGs: positive log2FC = rescues phage infectivity (anti-defense); negative = sensitizes host (PCD-trigger)
ags = [
    ('AcrIF7-like',5.6,42,1),
    ('Ocr-like (anti-R-M)',4.7,36,1),
    ('CBASS-evasion AG',3.1,27,1),
    ('Broad-spectrum AG-114',2.0,19,1),
    ('Thoeris-evasion AG',1.6,14,1),
    ('PCD-trigger AG-22',-4.2,33,-1),
    ('PCD-trigger AG-58',-2.6,20,-1),
]
g_svg = " ".join(
    f'<circle cx="{vx(fc):.1f}" cy="{vy(lp):.1f}" r="4.5" fill="{"rgb(170,35,35)" if d>0 else "rgb(34,90,158)"}"/>'
    f'<text x="{vx(fc)+d*7:.1f}" y="{vy(lp)+3.5:.1f}" font-size="10" font-weight="bold" '
    f'text-anchor="{"start" if d>0 else "end"}" fill="#111" font-family="system-ui,sans-serif">{name}</text>'
    for name,fc,lp,d in ags)

vxt = " ".join(
    f'<line x1="{vx(v):.0f}" y1="{VB}" x2="{vx(v):.0f}" y2="{VB+4}" stroke="#bbb"/>'
    f'<text x="{vx(v):.0f}" y="{VB+15}" text-anchor="middle" font-size="10" fill="#999">{v}</text>'
    for v in [-6,-4,-2,0,2,4,6])
vyt = " ".join(
    f'<line x1="{VL-4}" y1="{vy(v):.0f}" x2="{VL}" y2="{vy(v):.0f}" stroke="#bbb"/>'
    f'<text x="{VL-7}" y="{vy(v)+3.5:.0f}" text-anchor="end" font-size="10" fill="#999">{v}</text>'
    for v in [0,10,20,30,40,50])

vol = f"""<svg viewBox="0 0 {VW} {VH}" width="{VW}" height="{VH}" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:{VW}px;display:block;margin-top:.5rem">
<line x1="{VL}" y1="{VT}" x2="{VL}" y2="{VB}" stroke="#bbb"/>
<line x1="{VL}" y1="{VB}" x2="{VR}" y2="{VB}" stroke="#bbb"/>
<line x1="{vx(1):.0f}" y1="{VT}" x2="{vx(1):.0f}" y2="{VB}" stroke="#ddd" stroke-dasharray="4,3"/>
<line x1="{vx(-1):.0f}" y1="{VT}" x2="{vx(-1):.0f}" y2="{VB}" stroke="#ddd" stroke-dasharray="4,3"/>
<line x1="{VL}" y1="{vy(1.301):.0f}" x2="{VR}" y2="{vy(1.301):.0f}" stroke="#ddd" stroke-dasharray="4,3"/>
{vxt} {vyt}
{ns_svg}
{dn_svg}
{up_svg}
{g_svg}
<text x="{VR-4}" y="{VT+14}" text-anchor="end" font-size="11" fill="rgb(170,35,35)" font-family="system-ui,sans-serif">&#x2191; 140 anti-defense AGs</text>
<text x="{VL+4}" y="{VT+14}" text-anchor="start" font-size="11" fill="rgb(34,90,158)" font-family="system-ui,sans-serif">&#x2193; 70 PCD-trigger AGs</text>
<text x="{VL+(VR-VL)//2}" y="{VH-16}" text-anchor="middle" font-size="12" fill="#555" font-family="system-ui,sans-serif">log&#x2082; Fold Change (phage infectivity rescue, pooled AG screen)</text>
<text x="11" y="{VT+(VB-VT)//2}" text-anchor="middle" font-size="12" fill="#555" font-family="system-ui,sans-serif" transform="rotate(-90,11,{VT+(VB-VT)//2})">&#x2212;log&#x2081;&#x2080;(adjusted p-value)</text>
</svg>"""

with open("/Users/apple/Desktop/job demos/Quigley Lab - Bioinformatics Specialist/silas-lab-demo/pca.svg", "w") as f:
    f.write(pca)
with open("/Users/apple/Desktop/job demos/Quigley Lab - Bioinformatics Specialist/silas-lab-demo/volcano.svg", "w") as f:
    f.write(vol)

print(f"PCA SVG: {len(pca):,} chars")
print(f"Volcano SVG: {len(vol):,} chars")

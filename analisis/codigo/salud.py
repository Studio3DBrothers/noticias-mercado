"""Tarjetas estilo 'Salud financiera' y gráfico de 5 años (precio ajustado, ingresos y ganancia por acción de 12 meses)."""
import json, datetime as dt
from informe import *
from trim import serie_ttm
from sec import Facts
from calc import REV
FR=['rojo','amarillo','verde']
def _pos(v, cortes, mayor=True):
    """cortes = (mín, límite rojo/amarillo, límite amarillo/verde, máx). Devuelve 0..1 en tercios: rojo, amarillo, verde."""
    a,b,c,d=cortes
    if not mayor: v=-v; a,b,c,d=-d,-c,-b,-a
    v=max(a,min(d,v))
    if v<b: p=(v-a)/(b-a)/3
    elif v<c: p=1/3+(v-b)/(c-b)/3
    else: p=2/3+(v-c)/(d-c)/3
    return p
def posicion(k, m, est):
    if est not in FR: return None
    if k=='valuacion': p=_pos(m['pe'],(10,20,35,60),False)
    elif k=='rentabilidad': p=min(_pos(m['margenOp'],(0,10,20,45)),_pos(m['roe'],(0,8,15,45)))
    elif k=='balance': p=0.95 if m['deudaNeta']<=0 else _pos(m['dnEbitda'],(0,1.5,3,6),False)
    elif k=='flujo': p=_pos(m['margenFcf'],(0,5,15,35))
    elif k=='crecimiento': p=_pos(m['crec'],(-10,3,10,25))
    elif k=='dividendos': p=_pos(m['retorno'],(0,1,3,6))
    else: return None
    if est not in FR: return None
    i=FR.index(est); return max(i/3+.03,min((i+1)/3-.03,p))   # la marca queda siempre dentro del tramo de su color
def barra(p, est):
    segs=''.join(f'<span style="background:{COL[e] if est in FR else GRIS};opacity:{1 if est==e else .35}"></span>' for e in FR)
    mk=f'<i style="left:calc({p*100:.1f}% - 5px);border-top-color:{INK}"></i>' if p is not None else ''
    return f'<div class="bar">{mk}{segs}</div>'
CSS=f'''.sal{{display:grid;grid-template-columns:1fr 1fr;gap:8px}}
.tj{{background:#fff;border:2px solid {LINE};border-radius:11px;padding:8px 10px 9px;display:flex;flex-direction:column;gap:3px}}
.tj .n{{font-size:12px;font-weight:700}} .tj .c{{font-size:19px;font-weight:800;line-height:1.05}} .tj .d{{font-size:10.5px;color:{MU};line-height:1.3;flex:1}}
.bar{{position:relative;display:grid;grid-template-columns:1fr 1fr 1fr;gap:4px;margin-top:9px}} .bar span{{height:5px;border-radius:3px}}
.bar i{{position:absolute;top:-8px;width:0;height:0;border:5px solid transparent;border-bottom:0}}'''
def tarjetas(d, m):
    out=[]
    for x in d['semaforo']:
        e=x['estado']; col=COL[e]; p=posicion(x['id'],m,e)
        out.append(f'<div class="tj" style="border-color:{col if e in FR else LINE}"><div class="n">{x["nombre"]}</div><div class="c" style="color:{col}">{x["calificacion"]}</div><div class="d">{esc(x["dato"])}</div>{barra(p,e)}</div>')
    return f'<div class="sal">{"".join(out)}</div>'
# ---------- gráfico de 5 años ----------
D=dt.date.fromisoformat
def datos5(cik, pxfile, fecha, precio_hoy):
    f=Facts(cik); ini=D(fecha).replace(year=D(fecha).year-5)
    r=[(k,v) for k,v in serie_ttm(f,REV) if D(k)>=ini]
    e=[(k,v) for k,v in serie_ttm(f,['EarningsPerShareDiluted'],'USD/shares') if D(k)>=ini]
    j=json.load(open(pxfile)); pts=[(dd,p) for dd,p in zip(j['dates'],j['prices']) if D(dd)>=ini]
    pts=pts[::5]+([(fecha,precio_hoy)] if pts[-1][0]<fecha else [])
    return {'desde':ini.isoformat(),'hasta':fecha,'ingresos12m':[{'fin':k,'valor':v} for k,v in r],'gpa12m':[{'fin':k,'valor':round(v,2)} for k,v in e],
            'precio':[{'fecha':k,'valor':round(v,2)} for k,v in pts],'fuentePrecio':'Data912 (precio ajustado)'}
def _nice(mx, n=4):
    import math
    raw=mx/n; mag=10**math.floor(math.log10(raw)); st=min((s*mag for s in (1,1.5,2,2.5,3,4,5,6,8,10) if s*mag>=raw))
    return st, st*n
def chart5(g, CW=698, CH=250):
    L,R,T,Bm=46,86,28,24; W=CW-L-R; Hh=CH-T-Bm
    t0=D(g['desde']); t1=D(g['hasta']); X=lambda s: L+(D(s)-t0).days/(t1-t0).days*W
    rs,rmx=_nice(max(x['valor'] for x in g['ingresos12m'])/1e9*1.08)
    pv=[x['valor'] for x in g['precio']]; ps,pmx=_nice(max(pv)*1.08)
    ev=[x['valor'] for x in g['gpa12m']]; emn=min(0,min(ev)); es,emx=_nice((max(ev)-emn)*1.15); emx+=emn
    Y=lambda v,mx,mn=0: T+Hh-(v-mn)/(mx-mn)*Hh
    o=[]
    for i in range(5):  # grilla y ejes
        y=T+Hh-i*Hh/4
        o.append(f'<line x1="{L}" x2="{L+W}" y1="{y:.1f}" y2="{y:.1f}" stroke="{LINE}"/>')
        o.append(f'<text x="{L-6}" y="{y+4:.1f}" font-size="10.5" fill="{MU}" text-anchor="end">{n(i*rs,0 if rs>=1 else 1)}</text>')
        o.append(f'<text x="{L+W+6}" y="{y+4:.1f}" font-size="10.5" fill="{AC}">{n(i*ps,0)}</text>')
        o.append(f'<text x="{L+W+48}" y="{y+4:.1f}" font-size="10.5" fill="{WARN}">{n(emn+i*es,2 if es<1 else 1)}</text>')
    bw=max(6,W/len(g['ingresos12m'])*0.62)
    for x in g['ingresos12m']:
        cx=X(x['fin']); v=x['valor']/1e9; o.append(f'<rect x="{cx-bw/2:.1f}" y="{Y(v,rmx):.1f}" width="{bw:.1f}" height="{T+Hh-Y(v,rmx):.1f}" rx="2" fill="{CEL}" opacity=".45"/>')
    for yr in range(t0.year+1,t1.year+1):
        x=X(f'{yr}-01-01'); o.append(f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{T+Hh}" y2="{T+Hh+4}" stroke="{MU}"/><text x="{x:.1f}" y="{CH-6}" font-size="10.5" fill="{MU}" text-anchor="middle">{yr}</text>')
    pp=' '.join(f'{X(x["fecha"]):.1f},{Y(x["valor"],pmx):.1f}' for x in g['precio'])
    o.append(f'<polyline points="{pp}" fill="none" stroke="{AC}" stroke-width="1.8" stroke-linejoin="round"/>')
    ep=' '.join(f'{X(x["fin"]):.1f},{Y(x["valor"],emx,emn):.1f}' for x in g['gpa12m'])
    o.append(f'<polyline points="{ep}" fill="none" stroke="{WARN}" stroke-width="2.2"/>'+''.join(f'<circle cx="{X(x["fin"]):.1f}" cy="{Y(x["valor"],emx,emn):.1f}" r="2.6" fill="{WARN}"/>' for x in g['gpa12m']))
    # rótulos de ejes
    o.append(f'<text x="{L-6}" y="{T-14}" font-size="10" fill="{MU}" text-anchor="end">mil M</text><text x="{L+W+6}" y="{T-14}" font-size="10" fill="{AC}">US$</text><text x="{L+W+48}" y="{T-14}" font-size="10" fill="{WARN}">US$</text>')
    return f'<svg width="{CW}" height="{CH}">{"".join(o)}</svg>'

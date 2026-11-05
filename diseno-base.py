# Genera 6 muestras de diseño de la hoja oscura para compartir (HTML -> PNG con Playwright).
import os
from playwright.sync_api import sync_playwright

D = os.path.dirname(os.path.abspath(__file__))

CSS = """
*{box-sizing:border-box}
:root{--bg:#070D19;--card:#0F1A2D;--card2:#13213A;--line:#1F2F4D;--ink:#EAF0FA;--muted:#8C9BB5;
--acc:#4C8DFF;--cel:#7CC4FF;--up:#35D49A;--down:#FF5C6E;--gold:#E9B949}
body{margin:0;background:var(--bg);font-family:'Inter','Inter Display',sans-serif;color:var(--ink)}
.page{width:1080px;padding:34px 34px 26px;position:relative;overflow:hidden;
 background:radial-gradient(900px 500px at 85% -5%,rgba(76,141,255,.22),transparent 60%),radial-gradient(700px 500px at -10% 105%,rgba(124,196,255,.10),transparent 60%),var(--bg)}
.velas{position:absolute;right:20px;top:150px;width:460px;height:220px;opacity:.13;pointer-events:none}
.head{display:flex;align-items:center;gap:18px;position:relative;z-index:1}
.head img{width:78px;height:78px;border-radius:18px;box-shadow:0 0 0 1px rgba(255,255,255,.08)}
.head h1{margin:0;font:900 46px/1 'Inter Display','Inter';letter-spacing:.5px}
.head .sub{color:var(--muted);font-size:15px;letter-spacing:3px;margin-top:8px;text-transform:uppercase}
.fecha{margin-left:auto;text-align:right}
.fecha .pill{display:inline-block;border:1px solid rgba(124,196,255,.45);background:rgba(76,141,255,.12);color:var(--cel);font-weight:800;font-size:17px;padding:10px 16px;border-radius:12px}
.fecha small{display:block;color:var(--muted);font-size:13px;margin-top:6px}
.lead{z-index:1;margin:22px 0 18px;padding:20px 24px;border-radius:20px;background:linear-gradient(135deg,rgba(76,141,255,.18),rgba(76,141,255,.04));border:1px solid rgba(124,196,255,.25);position:relative}
.eyebrow{font-size:13px;font-weight:800;letter-spacing:2.5px;color:var(--cel);text-transform:uppercase}
.lead h2{margin:8px 0 6px;font:800 33px/1.15 'Inter Display','Inter'}
.lead p{margin:0;color:#C9D4E8;font-size:17px;line-height:1.45}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}
.card{background:linear-gradient(180deg,var(--card2),var(--card));border:1px solid var(--line);border-radius:20px;padding:18px;position:relative;overflow:hidden;display:flex;flex-direction:column;gap:10px;min-height:330px}
.card.ch{min-height:170px;gap:6px}
.tag{display:inline-flex;align-items:center;gap:8px;font-size:12px;font-weight:800;letter-spacing:1.8px;text-transform:uppercase;color:var(--cel)}
.tag i{width:8px;height:8px;border-radius:50%;background:var(--cel);display:inline-block}
.tag.ar i{background:linear-gradient(90deg,#74ACDF 33%,#fff 33% 66%,#74ACDF 66%)}
.tag.br i{background:#2BB673} .tag.us i{background:#E25563}
.card h3{margin:0;font:800 22px/1.2 'Inter Display','Inter'}
.card p{margin:0;color:#B9C5DA;font-size:15.5px;line-height:1.45}
.row{display:flex;align-items:center;gap:12px}
.logo{width:46px;height:46px;border-radius:50%;display:grid;place-items:center;font-weight:900;font-size:14px;color:#fff;flex:none;box-shadow:0 0 0 2px rgba(255,255,255,.06)}
.big{font:800 34px/1 'Inter Display','Inter';font-variant-numeric:tabular-nums}
.var{font-weight:800;font-size:19px;font-variant-numeric:tabular-nums}
.up{color:var(--up)}.down{color:var(--down)}.flat{color:var(--muted)}
.cif{margin-top:auto;display:flex;flex-direction:column;gap:6px}
.cif div{display:flex;justify-content:space-between;align-items:baseline;border-top:1px solid var(--line);padding-top:6px;font-size:15px;font-variant-numeric:tabular-nums}
.cif b{font-weight:800;white-space:nowrap}
.cif span:first-child{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-right:10px}
.cif span:first-child{color:#C9D4E8}
.src{font-size:12px;color:var(--muted)}
.ilus{position:absolute;right:14px;top:12px;opacity:.10}.ilus svg{width:70px;height:70px}
.sect{display:flex;align-items:center;gap:12px;margin:20px 0 12px;font-size:14px;font-weight:800;letter-spacing:2.5px;color:var(--muted);text-transform:uppercase}
.sect:after{content:"";flex:1;height:1px;background:var(--line)}
.foot{display:flex;justify-content:space-between;align-items:center;margin-top:22px;padding-top:16px;border-top:1px solid var(--line);color:var(--muted);font-size:12.5px}
.foot b{color:var(--ink);letter-spacing:2px}
.muestra{position:absolute;top:16px;right:16px;font-size:11px;font-weight:800;letter-spacing:1.5px;color:var(--gold);border:1px solid rgba(233,185,73,.5);padding:4px 8px;border-radius:8px}
.pts{display:flex;flex-direction:column;gap:7px;font-size:15px}
.pts div{display:flex;gap:8px;align-items:flex-start;line-height:1.35}
.cuenta{font:900 92px/0.9 'Inter Display','Inter';color:var(--cel);letter-spacing:-2px}
"""

def velas(color='#4C8DFF'):
    import random
    random.seed(7)
    x, y, out = 10, 150, []
    for i in range(26):
        o = y; y = max(40, min(220, y + random.randint(-28, 22)))
        c = y; hi = min(o, c) - random.randint(6, 20); lo = max(o, c) + random.randint(6, 20)
        col = '#35D49A' if c < o else '#FF5C6E'
        out.append(f'<line x1="{x+6}" y1="{hi}" x2="{x+6}" y2="{lo}" stroke="{col}" stroke-width="2"/><rect x="{x}" y="{min(o,c)}" width="12" height="{max(3,abs(c-o))}" fill="{col}" rx="2"/>')
        x += 20
    return f'<svg class="velas" viewBox="0 0 520 250">{"".join(out)}</svg>'

def linea(up=True, w=260, h=90, col=None):
    import random
    random.seed(3 if up else 9)
    pts, y = [], 60
    for i in range(30):
        y += random.uniform(-6, 4) if up else random.uniform(-4, 6)
        y = max(8, min(h - 8, y))
        pts.append(f"{i*w/29:.1f},{y:.1f}")
    col = col or ('#35D49A' if up else '#FF5C6E')
    poly = ' '.join(pts)
    return f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs><linearGradient id="g{int(up)}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{col}" stop-opacity=".35"/><stop offset="1" stop-color="{col}" stop-opacity="0"/></linearGradient></defs><polygon points="0,{h} {poly} {w},{h}" fill="url(#g{int(up)})"/><polyline points="{poly}" fill="none" stroke="{col}" stroke-width="3" stroke-linejoin="round"/></svg>'

ICON = {
 'gota': '<svg width="150" height="150" viewBox="0 0 24 24"><path d="M12 2s7 7.5 7 12a7 7 0 0 1-14 0c0-4.5 7-12 7-12z" fill="#fff"/></svg>',
 'banco': '<svg width="160" height="160" viewBox="0 0 24 24" fill="#fff"><path d="M12 2 2 7v2h20V7z"/><rect x="4" y="10" width="2.5" height="8"/><rect x="9" y="10" width="2.5" height="8"/><rect x="13.5" y="10" width="2.5" height="8"/><rect x="18" y="10" width="2.5" height="8"/><rect x="2" y="19" width="20" height="3"/></svg>',
 'escudo': '<svg width="150" height="150" viewBox="0 0 24 24"><path d="M12 2 4 5v6c0 5 3.4 9.4 8 11 4.6-1.6 8-6 8-11V5z" fill="#fff"/></svg>',
 'bitcoin': '<svg width="160" height="160" viewBox="0 0 24 24"><circle cx="12" cy="12" r="11" fill="#fff"/></svg>',
}

def logo(t, col):
    return f'<div class="logo" style="background:{col}">{t}</div>'

def head(fecha='Jueves 5 de noviembre de 2026', hora='Datos al cierre del miércoles 4/11 · 11:45 h'):
    return f'''{velas()}<div class="head"><img src="logo.png"><div><h1>NOTICIAS DEL MERCADO</h1><div class="sub">Argentina · EE.UU. · Brasil · Empresas</div></div>
<div class="fecha"><span class="pill">{fecha}</span><small>{hora}</small></div></div>'''

LEAD = '''<div class="lead"><div class="eyebrow">Resumen del día</div><h2>Wall Street sube tras el resultado electoral en EE.UU. y Argentina va a contramano</h2>
<p>El Dow gana 3% y el petróleo cae 8%; acá el riesgo país toca 852 puntos, máximo en un año, y el Merval pierde 2,4%.</p></div>'''

FOOT = '<div class="foot"><span><b>NOTICIAS DEL MERCADO</b> · Control de Inversiones</span><span>Resumen automático de fuentes públicas. Puede contener errores. No es una recomendación de inversión.</span></div>'

# Tarjetas de noticias
C = {
 'dow': f'''<div class="card"><span class="tag us"><i></i>Estados Unidos</span><h3>El Dow tiene su mejor día desde abril de 2025</h3>
<p>Tras el resultado electoral subieron todos los sectores menos energía y la volatilidad se desplomó.</p><div>{linea(True)}</div>
<div class="cif"><div><span>Dow Jones · 4/11</span><b class="up">53.356 ▲ 3,03%</b></div><div><span>S&amp;P 500</span><b class="up">7.689 ▲ 1,58%</b></div></div><div class="src">Fuente: TheStreet · 4/11</div></div>''',
 'wti': f'''<div class="card"><div class="ilus">{ICON['gota']}</div><span class="tag us"><i></i>Materias primas</span><h3>El petróleo se desploma 8% y bajan las tasas</h3>
<p>El mercado apuesta a que el resultado electoral acerque el fin de la guerra con Irán.</p>
<div class="row" style="margin-top:6px"><span class="big">US$ 88,12</span><span class="var down">▼ 8,29%</span></div>
<div class="cif"><div><span>Oro · cierre 4/11</span><b class="up">US$ 4.065 ▲ 3,3%</b></div><div><span>Bono 10 años</span><b class="down">4,89% ▼ 6 pb</b></div></div><div class="src">Fuente: StockTitan (CNBC) · 4/11</div></div>''',
 'rp': f'''<div class="card"><span class="tag ar"><i></i>Argentina</span><h3>Riesgo país en 852: máximo desde octubre de 2025</h3>
<p>Los activos locales no acompañaron el rebote global: pesaron el petróleo sobre las energéticas y los vencimientos de 2027.</p>
<div class="row" style="margin-top:6px"><span class="big">852 pb</span><span class="var down">▲ 24 pb</span></div>
<div class="cif"><div><span>Merval · cierre 4/11</span><b class="down">88.238 ▼ 2,4%</b></div><div><span>YPF (ADR)</span><b class="down">US$ 41,61 ▼ 7,1%</b></div></div><div class="src">Fuente: Infobae · 4/11</div></div>''',
 'bcra': f'''<div class="card"><div class="ilus">{ICON['banco']}</div><span class="tag ar"><i></i>Argentina</span><h3>Sube el MEP y el BCRA vuelve a comprar</h3>
<p>El BCRA compró US$ 9 M tras dos ruedas sin intervenir y las reservas subieron por el oro.</p>
<div class="cif"><div><span>MEP · cierre 4/11</span><b class="up">$ 1.584,76 ▲ 0,7%</b></div><div><span>Mayorista</span><b class="down">$ 1.546 ▼ 0,3%</b></div><div><span>Reservas</span><b class="up">US$ 50.435 M ▲ 142 M</b></div></div><div class="src">Fuente: Ámbito · 4/11</div></div>''',
 'cedear': f'''<div class="card"><div class="ilus">{ICON['escudo']}</div><span class="tag ar"><i></i>Argentina · CEDEARs</span><h3>Se frena el impuesto del 15% a la venta de CEDEARs</h3>
<p>El Gobierno retiró para revisarla la ley que gravaba con Ganancias la venta de CEDEARs, igual que las acciones del exterior. Por ahora no hay cambios.</p><div class="src" style="margin-top:auto">Fuente: El Cronista · 4/11</div></div>''',
 'selic': f'''<div class="card"><span class="tag br"><i></i>Brasil</span><h3>El Copom frena los recortes: Selic en 13,75%</h3>
<p>El Banco Central de Brasil pausó el ciclo por la inflación; antes, el Ibovespa cortó seis bajas seguidas.</p>
<div class="row" style="margin-top:6px"><span class="big">13,75%</span><span class="var flat">=</span></div>
<div class="cif"><div><span>Ibovespa · 4/11</span><b class="up">167.563 ▲ 1,23%</b></div><div><span>Dólar / real</span><b class="down">R$ 5,45 ▼ 0,64%</b></div></div><div class="src">Fuente: InfoMoney · 4/11</div></div>''',
 'btc': f'''<div class="card">{''}<span class="tag"><i style="background:#F7931A"></i>Cripto</span><div class="row">{logo('₿','#F7931A')}<h3>Bitcoin vuelve a US$ 80.000</h3></div>
<p>Rebotó después del recuento de votos; los ETF de bitcoin cortaron tres días de salidas.</p>
<div class="cif"><div><span>Bitcoin · 5/11 7 h</span><b class="up">US$ 80.300 ▲ 3,4%</b></div><div><span>Ether</span><b class="up">US$ 2.425 ▲ 6%</b></div></div><div class="src">Fuente: crypto.news · 5/11</div></div>''',
 'big': f'''<div class="card"><span class="tag"><i></i>Empresas</span><div class="row">{logo('AMZN','#232F3E')}{logo('AAPL','#555')}<h3>Las grandes tecnológicas lideran el rebote</h3></div>
<p>El mercado lee un Congreso dividido como menos cambios para el sector.</p>
<div class="cif"><div><span>AMZN · cierre 4/11</span><b class="up">▲ 6,12%</b></div><div><span>AAPL · cierre 4/11</span><b class="up">▲ 5,31%</b></div></div><div class="src">Fuente: 24/7 Wall St. · 4/11</div></div>''',
}
CH = {
 'mep': '<div class="card ch"><span class="tag ar"><i></i>Dólar MEP</span><span class="big">$ 1.584,76</span><span class="var up">▲ 0,7%</span><span class="src" style="margin-top:auto">Ámbito · cierre 4/11</span></div>',
 'rp': '<div class="card ch"><span class="tag ar"><i></i>Riesgo país</span><span class="big">852 pb</span><span class="var down">▲ 24 pb · máximo del año</span><span class="src" style="margin-top:auto">Infobae · cierre 4/11</span></div>',
 'ibov': '<div class="card ch"><span class="tag br"><i></i>Ibovespa</span><span class="big">167.563</span><span class="var up">▲ 1,23%</span><span class="src" style="margin-top:auto">InfoMoney · cierre 4/11</span></div>',
 'agenda': '<div class="card ch"><span class="tag us"><i></i>Viernes 6/11</span><h3 style="font-size:19px">Sale el informe de empleo de EE.UU.</h3><p style="font-size:14px">Dato clave para la Fed de diciembre.</p></div>',
 'feriado': '<div class="card ch"><span class="tag ar"><i></i>Semana corta</span><h3 style="font-size:19px">Lunes 9 feriado; martes 10 sin bancos</h3><p style="font-size:14px">Menos ruedas para operar en Argentina.</p></div>',
 'balances': '<div class="card ch"><span class="tag"><i style="background:var(--gold)"></i>Balances hoy</span><h3 style="font-size:19px">Airbnb, EOG y Monster</h3><p style="font-size:14px">Después del cierre de Wall Street.</p></div>',
}

FEATURE_WIDE = f'''<div class="card" style="grid-column:span 3;min-height:300px;flex-direction:row;gap:26px;align-items:stretch">
<div style="flex:1.2;display:flex;flex-direction:column;gap:12px"><span class="tag us"><i></i>Destacada · Estados Unidos</span>
<h3 style="font-size:34px;line-height:1.12">Wall Street tiene su mejor día desde abril de 2025 tras el resultado electoral</h3>
<p style="font-size:17px">Subieron todos los sectores menos energía, la volatilidad cayó 20% y la tasa a 10 años bajó a 4,89%. El petróleo se desplomó 8%.</p>
<div class="src" style="margin-top:auto">Fuente: TheStreet · StockTitan (CNBC) · 4/11</div></div>
<div style="flex:1;display:flex;flex-direction:column;gap:10px;justify-content:center">{linea(True, 400, 120)}
<div class="cif" style="margin-top:0"><div><span>Dow Jones</span><b class="up">53.356 ▲ 3,03%</b></div><div><span>S&amp;P 500</span><b class="up">7.689 ▲ 1,58%</b></div><div><span>Nasdaq</span><b class="up">25.737 ▲ 1,44%</b></div><div><span>VIX</span><b class="down">16,61 ▼ 20,3%</b></div></div></div></div>'''

FEATURE_BIG = f'''<div class="card" style="grid-column:span 2;grid-row:span 2;gap:14px">
<span class="tag ar"><i></i>Destacada · Argentina</span><h3 style="font-size:36px;line-height:1.1">Riesgo país en 852: el nivel más alto en un año</h3>
<p style="font-size:17.5px">Los activos argentinos no acompañaron el rebote global. Pesaron la caída del petróleo sobre las energéticas, la incertidumbre por 2027 y los vencimientos de deuda.</p>
<div class="row" style="gap:24px;margin-top:8px"><div><div class="eyebrow" style="color:var(--muted)">Riesgo país</div><span class="big" style="font-size:64px">852</span> <span class="var down">▲ 24 pb</span></div>
<div>{linea(False, 280, 110)}</div></div>
<div class="cif"><div><span>Merval · cierre 4/11</span><b class="down">88.238 ▼ 2,4%</b></div><div><span>Merval en dólares</span><b class="down">53 ▼ 2,6%</b></div><div><span>YPF (ADR)</span><b class="down">US$ 41,61 ▼ 7,1%</b></div><div><span>Bonos en dólares (prom.)</span><b class="down">▼ 1,1%</b></div></div>
<div class="src">Fuente: Infobae · El Cronista · 4/11</div></div>'''

def page(body, extra_css=''):
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}{extra_css}</style></head><body><div class="page">{body}</div></body></html>'

def cartera(con_balances=True):
    if con_balances:
        v1 = '''<div class="card" style="background:linear-gradient(160deg,rgba(76,141,255,.28),var(--card));border-color:rgba(124,196,255,.4)"><span class="tag"><i style="background:var(--gold)"></i>Próximo balance</span>
<div class="row"><div class="logo" style="background:#0B3D2E">CRWV</div><div><h3>CoreWeave</h3><div class="src" style="font-size:14px">Martes 10/11 · después del cierre</div></div></div>
<div style="margin-top:8px"><span class="cuenta">5</span> <span style="font-size:26px;font-weight:800;color:var(--cel)">DÍAS</span></div>
<p>Aparece 7 días antes y baja día a día hasta "HOY". Si presentan varios activos en la semana, se muestran en orden.</p></div>'''
        v2 = '''<div class="card"><span class="muestra">CIFRAS DE EJEMPLO</span><span class="tag"><i style="background:var(--up)"></i>Balance · 3T</span>
<div class="row"><div class="logo" style="background:#555">AAPL</div><div><h3>Apple</h3><div class="src" style="font-size:14px">Presentó el 30/10 · la acción <b class="up">▲ 2,1%</b></div></div></div>
<p>Superó lo esperado en ingresos y ganancia por acción, con récord en servicios.</p>
<div class="pts"><div><b class="up">▲</b> Ingresos US$ 102.500 M (+8% anual)</div><div><b class="up">▲</b> Servicios +15% anual, récord</div><div><b class="down">▼</b> China −4% anual</div><div><b class="down">▼</b> Margen bruto 45,9% (−0,4 pp)</div></div></div>'''
        v3 = '''<div class="card"><span class="muestra">CIFRAS DE EJEMPLO</span><span class="tag"><i style="background:var(--down)"></i>Balance · 3T</span>
<div class="row"><div class="logo" style="background:#232F3E">AMZN</div><div><h3>Amazon</h3><div class="src" style="font-size:14px">Presentó el 30/10 · la acción <b class="down">▼ 4,3%</b></div></div></div>
<p><b style="color:var(--ink)">Por qué cayó:</b> el flujo de caja libre bajó 20% por la inversión en data centers, aunque AWS aceleró.</p>
<div class="pts"><div><b class="down">▼</b> Flujo de caja libre −20% anual</div><div><b class="down">▼</b> Inversión US$ 34.000 M (+60%)</div><div><b class="up">▲</b> AWS +21% anual</div><div><b class="up">▲</b> Ingresos US$ 180.000 M (+12%)</div></div></div>'''
    else:
        v1 = f'''<div class="card"><span class="tag"><i></i>Tu cartera · Noticia</span><div class="row">{logo('CRM','#00A1E0')}<h3>Salesforce compra Cresta</h3></div>
<p>Suma agentes de voz con IA a Service Cloud; es su tercera compra en pocas semanas y no informó el precio.</p><div class="src" style="margin-top:auto">Fuente: Salesforce · 2/11</div></div>'''
        v2 = C['btc'].replace('<span class="tag"><i style="background:#F7931A"></i>Cripto</span>','<span class="tag"><i style="background:#F7931A"></i>Tu cartera · IBIT · ETHA</span>')
        v3 = C['big'].replace('<span class="tag"><i></i>Empresas</span>','<span class="tag"><i></i>Tu cartera · AMZN · AAPL</span>')
    titulo = 'Semana de balances' if con_balances else 'Sin balances en los próximos 7 días'
    return f'''<div class="head"><img src="logo.png" style="width:60px;height:60px"><div><h1 style="font-size:38px">TU CARTERA</h1><div class="sub">{titulo} · armado en tu celular</div></div>
<div class="fecha"><span class="pill">Jueves 5/11</span></div></div>
<div class="grid" style="margin-top:22px">{v1}{v2}{v3}</div>
<div class="foot"><span><b>TU CARTERA</b> · Control de Inversiones</span><span>Resumen automático de fuentes públicas. No es una recomendación de inversión.</span></div>'''

MUESTRAS = {
 '1-estandar': page(head() + LEAD + '<div class="grid">' + C['big'] + C['btc'] + C['rp'] + C['bcra'] + C['dow'] + C['selic'] + '</div><div class="sect">En números</div><div class="grid">' + CH['mep'] + CH['rp'] + CH['ibov'] + '</div>' + FOOT),
 '2-destacada-ancha': page(head() + LEAD + '<div class="grid">' + FEATURE_WIDE + C['rp'] + C['bcra'] + C['selic'] + '</div><div class="sect">Agenda</div><div class="grid">' + CH['balances'] + CH['agenda'] + CH['feriado'] + '</div>' + FOOT),
 '3-destacada-grande': page(head() + LEAD + '<div class="grid">' + FEATURE_BIG + C['cedear'] + C['bcra'] + C['dow'] + C['wti'] + C['selic'] + '</div><div class="sect">En números</div><div class="grid">' + CH['mep'] + CH['ibov'] + CH['agenda'] + '</div>' + FOOT),
 '4-variante-verde': page(head() + LEAD + '<div class="grid">' + C['big'] + C['wti'] + C['rp'] + C['cedear'] + C['dow'] + C['selic'] + '</div><div class="sect">En números</div><div class="grid">' + CH['mep'] + CH['rp'] + CH['ibov'] + '</div>' + FOOT,
   ':root{--acc:#2FD1A4;--cel:#5EE6BE;--line:#1C3337;--card:#0C1A1C;--card2:#10262A;--bg:#061113}.page{background:radial-gradient(900px 500px at 85% -5%,rgba(47,209,164,.18),transparent 60%),var(--bg)}.lead{background:linear-gradient(135deg,rgba(47,209,164,.16),rgba(47,209,164,.03));border-color:rgba(94,230,190,.25)}.fecha .pill{border-color:rgba(94,230,190,.45);background:rgba(47,209,164,.1)}'),
 '5-tu-cartera-balances': page(cartera(True)),
 '6-tu-cartera-noticias': page(cartera(False)),
}

with sync_playwright() as p:
    b = p.chromium.launch()
    for nombre, html in MUESTRAS.items():
        f = os.path.join(D, nombre + '.html')
        open(f, 'w').write(html)
        pg = b.new_page(viewport={'width': 1080, 'height': 800}, device_scale_factor=1)
        pg.goto('file://' + f)
        pg.wait_for_timeout(200)
        pg.locator('.page').screenshot(path=os.path.join(D, nombre + '.png'))
        print(nombre, pg.evaluate("document.querySelector('.page').offsetHeight"))
        pg.close()
    b.close()

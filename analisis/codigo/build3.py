import json, os, sys, base64, re
sys.path.insert(0,'.')
from informe import *
from sankey2 import sankey as sankey2, mil
import salud
import importlib, datos_in; importlib.reload(datos_in)
from datos_in import E, FUENTE_PX
C=json.load(open(B+'calc.json'))
RATIO={'AAPL':20,'MSFT':30,'KO':5,'NU':2}  # catálogo de la app (BYMA, septiembre 2026)
CED={x['symbol']:x for x in json.load(open(B+'raw/live_cedears.json'))}
def var12(t,precio):
    j=json.load(open(B+f'raw/px_{t}.json')); import datetime as _d
    obj=(_d.date.fromisoformat(FECHA)-_d.timedelta(days=365)).isoformat()
    i=max(k for k,dd in enumerate(j['dates']) if dd<=obj); return (precio/j['prices'][i]-1)*100
FECHA='2026-11-12'; DATOS='cierre del 12/11/26'
PX={'AAPL':(354.84,-0.15,246.03,355.63),'MSFT':(522.98,0.36,352.17,555.80),'KO':(97.45,-0.12,66.25,97.57),'NU':(11.84,-3.9,11.60,18.76)}
OUT=B+'a4/'; os.makedirs(OUT,exist_ok=True)
LEYENDA='Este informe de análisis fundamental es solo un diagnóstico de la empresa según criterios fijos y no constituye una recomendación de compra ni venta. Las decisiones de inversión son responsabilidad exclusiva de cada inversor.'
def logo_html(t):
    """Logo a color (logos/color/<T>.png): si es blanco va sobre el círculo azul; si tiene color, sobre blanco con borde azul."""
    pc=REPO+f'logos/color/{t}.png'
    if os.path.exists(pc):
        from PIL import Image as _I
        im=_I.open(pc).convert('RGBA'); px=[q for q in im.getdata() if q[3]>128]
        blanco=bool(px) and sum(1 for q in px if min(q[:3])>230)/len(px)>.8
        b64=base64.b64encode(open(pc,'rb').read()).decode()
        return f'<div class="logo{"" if blanco else " cl"}"><img src="data:image/png;base64,{b64}"/></div>'
    return f'<div class="logo"><span>{t}</span></div>'
app_b64=base64.b64encode(open(REPO+'logos/app.png','rb').read()).decode()
def ft(iso): y,m,d=iso.split('-'); return f'{int(d)}/{int(m)}/{y[2:]}'
LBL={'valuacion':'Valuación','rentabilidad':'Rentabilidad','balance':'Balance','flujo':'Flujo de caja','crecimiento':'Crecimiento','dividendos':'Dividendos y recompras'}
# Calificación de cada punto, como en el diseño aprobado por Adrián (según el color que dan los criterios fijos).
CAL={'valuacion':{'verde':'Moderada','amarillo':'Media','rojo':'Exigente'},
     'rentabilidad':{'verde':'Alta','amarillo':'Media','rojo':'Baja'},
     'balance':{'verde':'Sólido','amarillo':'Moderado','rojo':'Endeudado'},
     'flujo':{'verde':'Alto','amarillo':'Medio','rojo':'Bajo'},
     'crecimiento':{'verde':'Alto','amarillo':'Moderado','rojo':'Bajo'},
     'dividendos':{'verde':'Alto','amarillo':'Medio','rojo':'Bajo'}}
def cal(i,e): return 'No aplica' if e=='na' else 'No paga' if e=='gris' else 'Sin dato' if e=='sin' else CAL[i][e]
def armar(t):
    e=E[t]; c=C[t]; m=c['m']; px=PX[t]; s=e['sankey']
    ov=e.get('datoSem',{})
    def _d(k,f):
        if k in ov: return ov[k]
        try: return f()
        except Exception: return ''
    dato={'valuacion':_d('valuacion',lambda:f"P/E 12 meses {n(m['pe'],1)} (precio US$ {n(px[0],2)} ÷ ganancia por acción US$ {n(m['eps'],2)})"),
     'rentabilidad':_d('rentabilidad',lambda:f"Margen operativo {n(m['margenOp'],0)}% · ROE {n(m['roe'],0)}%"),
     'balance':_d('balance',lambda:('Más caja que deuda: caja neta de US$ '+mil(-m['deudaNeta'])) if m['deudaNeta']<=0 else f"Deuda neta US$ {mil(m['deudaNeta'])} · {n(m['dnEbitda'],1)} veces la ganancia operativa antes de amortizaciones"),
     'flujo':_d('flujo',lambda:f"Flujo libre 12 meses US$ {mil(m['fcf'])} ({n(m['margenFcf'],0)}% de los ingresos)"),
     'crecimiento':_d('crecimiento',lambda:f"Ingresos 12 meses US$ {mil(m['ingresos'])} ({pc(m['crec'],1)})"),
     'dividendos':_d('dividendos',lambda:f"Dividendos {n(m['rendDiv'],1)}% + recompras {n(m['retorno']-m['rendDiv'],1)}% = {n(m['retorno'],1)}% de la capitalización")}
    nota=e['nota']+((' Otros ingresos netos (intereses, participaciones y otros): '+('+' if s['otros']>=0 else '−')+mil(abs(s['otros']))+'.') if abs(s['otros'])>=0.005*s['ingresos'] else '')
    jp=json.load(open(B+f'raw/px_{t}.json'))
    def pfin(f):
        ks=[k for k,dd in enumerate(jp['dates']) if dd<=f]; return round(jp['prices'][ks[-1]],2) if ks else None
    anios=[{**{k:v for k,v in a.items() if k!='presentado'},'ultimaPresentacion':a['presentado'],'precioCierre':pfin(a['fin'])} for a in c['anios']]
    return {'formato':'analisis/1','ticker':t,'nombre':e['nombre'],'trimestre':e['trimestre'],'periodo':e['periodo'],'fechaBalance':e['fechaBalance'],
       'fechaDatos':FECHA,'datosAl':DATOS,'ultimos12MesesHasta':m['hasta'],'puntaje':c['puntaje'],'tituloPuntaje':'Puntaje según 6 criterios fijos',
       'semaforo':[{'id':k,'nombre':LBL[k],'estado':v,'calificacion':cal(k,v),'dato':dato[k]} for k,v in c['sem'].items()],
       'notaSalud':e.get('notaSalud'),'margenNombre':e.get('margenNombre','Margen operativo'),'fuenteAnual':e.get('fuenteAnual','informes anuales 10-K ante la SEC'),'sankey':s,'nota':nota,'diezAnios':anios,'ultimoBalance':e['ultimo'],'ultimoFilas':e['ultimoFilas'],'fortalezas':e['fortalezas'],'debilidades':e['debilidades'],
       'cedear':({'ticker':t,'ratio':f'{RATIO[t]}:1','precioArs':CED[t]['c'],'dolarImplicito':round(CED[t]['c']*RATIO[t]/px[0],2),'fuente':'Data912 (BYMA) y ratio BYMA'} if t in CED and t in RATIO else None),'cotizacion':{'var12m':round(var12(t,px[0]),2),'distMax':round((px[0]/px[3]-1)*100,2),'precio':px[0],'variacionDia':px[1],'rango52':[px[2],px[3]],'capitalizacion':m['capitalizacion'],'proximoBalance':None},
       'prevision':e['prevision'],'conclusion':e['conclusion'],'noticiaClave':None,
       'calculos':{k:m[k] for k in ['ingresos','ingresosAnt','operativa','neta','eps','flujoOperativo','inversiones','dividendos','recompras','amortizaciones','patrimonio','deuda','deudaDetalle','caja','cajaDetalle','acciones','fechaAcciones','fechaBalance','como']},
       'fuentes':[{'nombre':f"Comunicado del balance (SEC, {e.get('formPR','8-K')})",'url':e['pr'],'fecha':e['fechaBalance']},
                  {'nombre':'SEC XBRL companyfacts','url':f"https://data.sec.gov/api/xbrl/companyfacts/CIK{e['cik']}.json",'fecha':m['fechaBalance']},
                  {**FUENTE_PX,'fecha':FECHA}]+e.get('fuentesExtra',[])+([{'nombre':'Data912 (CEDEARs en BYMA)','url':'https://data912.com/live/arg_cedears','fecha':FECHA}] if t in CED else [])+([e['prevision']['fuente']] if e['prevision'].get('fuente') else [])}
css=f'''@page{{size:A4;margin:0}} *{{box-sizing:border-box}} html,body{{margin:0;padding:0;background:#fff}}
body{{font-family:-apple-system,"Helvetica Neue",Helvetica,Arial;color:{INK};-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.page{{width:794px;height:1123px;padding:30px 34px 22px;display:flex;flex-direction:column;background:#fff;overflow:hidden;page-break-after:always;break-after:page;position:relative}}
.page:last-child{{page-break-after:auto;break-after:auto}}
.band{{display:flex;align-items:center;gap:10px;background:{AC};color:#fff;border-radius:14px;padding:10px 14px}} .band img.app{{width:30px;height:30px;border-radius:7px;background:#fff}}
.band .t1{{font-weight:800;font-size:15px;letter-spacing:1px}} .band .t2{{font-size:12px;opacity:.9}} .band .der{{margin-left:auto;text-align:right;font-size:12px;opacity:.95}}
.cab{{display:flex;align-items:center;gap:12px;margin-top:14px}} .logo{{width:52px;height:52px;border-radius:26px;background:{AC};display:flex;align-items:center;justify-content:center;flex:none}} .logo img{{width:34px;height:34px;object-fit:contain}} .logo.cl{{background:#fff;border:3px solid {AC}}} .logo span{{color:#fff;font-weight:800;font-size:13px}}
h1{{font-size:26px;margin:0;line-height:1}} .mu{{color:{MU};font-size:12px}}
.win{{background:{BG};border:1px solid {LINE};border-radius:14px;padding:11px 13px}}
.wt{{display:flex;align-items:center;gap:7px;font-weight:800;font-size:13px;letter-spacing:.6px;margin-bottom:7px}} .wt:before{{content:"";width:4px;height:15px;border-radius:2px;background:{CEL}}}
.g2{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px}} .g2>*,.win{{min-width:0}} .g2>*,.win{{min-width:0}}
.sem{{display:flex;gap:9px;align-items:center;padding:6px 0;border-bottom:1px solid {LINE};font-size:13px}} .sem:last-of-type{{border:0}} .dot{{width:12px;height:12px;border-radius:6px;flex:none}} .v{{font-weight:800;font-size:12px;white-space:nowrap}}
ul{{margin:0;padding-left:17px;font-size:13px;line-height:1.42}} li{{margin:3px 0}} p{{margin:0;font-size:13px;line-height:1.45}}
.row{{display:flex;justify-content:space-between;font-size:13px;padding:4px 0;border-bottom:1px solid {LINE}}} .row:last-child{{border:0}}
.cot{{display:grid;grid-template-columns:1.1fr .9fr 1.3fr 1fr 1fr;gap:10px}} .cot div{{min-width:0;display:flex;flex-direction:column;gap:3px;font-size:13.5px}} .cot .mu{{font-size:11px}}
.uf{{display:grid;grid-template-columns:1.45fr 1.1fr .7fr;gap:6px;font-size:13px;padding:5px 0;border-bottom:1px solid {LINE};align-items:baseline}} .uf:last-of-type{{border:0}} .uf>*{{min-width:0}} .uf b:last-child{{text-align:right}}
.pr{{display:flex;gap:14px;font-size:12px;color:{MU};margin-top:6px;padding-top:6px;border-top:1px solid {LINE}}} .pr b{{color:{INK}}}
.una{{white-space:nowrap;overflow:hidden}} .lg.una{{flex-wrap:nowrap;gap:10px}}
.lg{{display:flex;gap:14px;flex-wrap:wrap;font-size:12px;color:{MU};margin-top:4px}}
.nro{{margin-top:auto;padding-top:6px;text-align:center;font-size:8.5px;color:{MU}}} .pie+.nro{{margin-top:0}} .pie{{margin-top:auto;padding-top:9px;border-top:1px solid {LINE}}} .pie .f{{font-size:8.5px;color:{MU};line-height:1.35}} .pie .ley{{font-size:8px;color:{MU};line-height:1.3;margin-top:3px}}
'''+salud.CSS
def band(d,i): return f'''<div class="band"><img class="app" src="data:image/png;base64,{app_b64}"/><div><div class="t1">ANÁLISIS FUNDAMENTAL</div><div class="t2">Control de Inversiones</div></div></div>
<div class="cab">{logo_html(d['ticker'])}<div style="flex:1"><h1 class="una">{d['ticker']} - {esc(d['nombre'])}</h1><div class="mu una" style="font-size:13.5px;margin-top:4px">{d['trimestre']} ({d['periodo']}) - Balance Presentado el {'-'.join(f'{int(x):02d}' for x in reversed(d['fechaBalance'][2:].split('-')))}</div></div></div>'''
def band2(d): return f'''<div class="band"><img class="app" src="data:image/png;base64,{app_b64}"/><div><div class="t1">ANÁLISIS FUNDAMENTAL</div><div class="t2">Control de Inversiones</div></div></div>'''
def nro(i): return f'<div class="nro">Hoja {i} de 2</div>'
def pie(d):
    fu=' · '.join(f"{f['nombre']} ({ft(f['fecha'])})" for f in d['fuentes'])
    return f'<div class="pie"><div class="f">Datos al {d["datosAl"]}; últimos 12 meses hasta el {ft(d["ultimos12MesesHasta"])}. Fuentes: {esc(fu)}.</div><div class="ley">{LEYENDA} Las marcas y logos pertenecen a sus respectivos dueños.</div></div>'
def ufilas(u):
    def vc(v): return OK if v.startswith('+') else DN if v.startswith(('−','-')) else MU
    r=''.join((f'<div class="uf"><span class="una">{esc(a)}</span><b class="una">{esc(b)}</b>' if b else f'<div class="uf"><span class="una" style="grid-column:span 2">{esc(a)}</span>')+f'<b class="una" style="color:{vc(c)}">{esc(c)}</b></div>' for a,b,c in u['filas'])
    return r+(f'<div class="mu" style="margin-top:6px">{esc(u["nota"])}</div>' if u.get('nota') else '')
def ced(x):
    if not x: return ''
    return f'<div class="pr una"><span>CEDEAR {x["ticker"]} <b>$ {n(x["precioArs"],0)}</b></span><span>ratio <b>{x["ratio"]}</b></span><span>dólar implícito <b>$ {n(x["dolarImplicito"],0)}</b></span></div>'
def hoja1(d):
    c=d['cotizacion']; an=d['diezAnios']; p=d['puntaje']; pcol=OK if p>=7.5 else WARN if p>=5 else DN
    sem=salud.tarjetas(d,C[d['ticker']]['m'])
    return f'''<div class="page">{band(d,1)}
<div class="g2" style="grid-template-columns:minmax(0,1.25fr) minmax(0,1fr)">
 <div class="win"><div class="wt">SALUD FINANCIERA</div>{sem}<div class="mu" style="padding-top:7px">Colores según los criterios fijos de la tabla de la app. La marca muestra dónde queda el dato dentro de su tramo.{(' '+esc(d['notaSalud'])) if d.get('notaSalud') else ''}</div></div>
 <div style="display:flex;flex-direction:column;gap:12px">
  <div class="win" style="display:flex;align-items:center;gap:12px"><div style="width:76px;height:76px;border-radius:50%;border:8px solid {pcol};display:flex;align-items:center;justify-content:center;font-weight:800;font-size:24px;flex:none;background:#fff">{n(p,1)}</div><div><b class="una" style="font-size:14px;display:block">Puntaje según 6 criterios fijos</b><div class="mu" style="margin-top:3px">Pesos: 20% valuación, rentabilidad, flujo y crecimiento; 15% balance; 5% dividendos.</div></div></div>
  <div class="win"><div class="wt">PRECIO</div><div style="font-size:26px;font-weight:800">US$ {n(c['precio'],2)}</div><div class="mu una">{d['datosAl']} · capitalización US$ {mil(c['capitalizacion'])}</div><div class="pr una"><span>12 meses <b style="color:{OK if c['var12m']>=0 else DN}">{pc(c['var12m'],1)}</b></span><span>Distancia al máximo de 52 semanas <b>{'en máximos' if c['distMax']>-0.05 else pc(c['distMax'],1)}</b></span></div>{ced(d['cedear'])}</div>
  <div class="win" style="flex:1"><div class="wt">ÚLTIMO BALANCE</div>{ufilas(d['ultimoFilas'])}</div>
 </div>
</div>
<div class="win" style="margin-top:12px"><div class="wt">DE DÓNDE OBTIENE SUS INGRESOS</div><div class="mu" style="margin-bottom:4px">{d['trimestre']} ({d['periodo']}) · en US$</div>{sankey2(d['sankey'])}<div class="mu" style="margin-top:2px">{esc(d['nota'])}</div></div>
{nro(1)}</div>'''
PCOL=OK
def chart10(an):
    CW,CH=698,250; L=6; Bb=CH-20; nn=len(an); bw=44; gap=(CW-L*2-bw*nn)/(nn-1)
    mx=max(a['ingresos'] for a in an)*1.1; out=[]
    hi=max(max(a['margenOp'],a['margenNeto']) for a in an)*1.18
    lo=min(0,min(min(a['margenOp'],a['margenNeto']) for a in an))*1.25
    ly=(lambda v: Bb-max(v,0)/hi*(Bb-30)) if lo==0 else (lambda v: (Bb-30)-(v-lo)/(hi-lo)*(Bb-60))
    for i,a in enumerate(an):
        x=L+i*(bw+gap); h=a['ingresos']/mx*(Bb-18)
        out.append(f'<rect x="{x:.1f}" y="{Bb-h:.1f}" width="{bw}" height="{h:.1f}" rx="4" fill="{CEL}" opacity=".5"/><text x="{x+bw/2:.1f}" y="{CH-4}" font-size="12" fill="{MU}" text-anchor="middle">{a["fin"][:4]}</text><text x="{x+bw/2:.1f}" y="{Bb-6:.1f}" font-size="12" font-weight="700" fill="{INK}" text-anchor="middle">{n(a["ingresos"]/1e9,0 if mx>55e9 else 1)}</text>')
    for key,col,dash in (('margenOp',AC,''),('margenNeto',MU,'5,4')):
        pts=' '.join(f'{L+i*(bw+gap)+bw/2:.1f},{ly(a[key]):.1f}' for i,a in enumerate(an))
        out.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2.6" stroke-dasharray="{dash}"/>'+''.join(f'<circle cx="{L+i*(bw+gap)+bw/2:.1f}" cy="{ly(a[key]):.1f}" r="3" fill="{col}"/>' for i,a in enumerate(an)))
    pv=[x.get('precioCierre') for x in an]
    if all(v for v in pv):
        pm=max(pv); py=lambda v: (Bb-42)-v/pm*(Bb-42-34)
        pts=' '.join(f'{L+i*(bw+gap)+bw/2:.1f},{py(v):.1f}' for i,v in enumerate(pv))
        out.append(f'<polyline points="{pts}" fill="none" stroke="{PCOL}" stroke-width="2.6"/>'+''.join(f'<circle cx="{L+i*(bw+gap)+bw/2:.1f}" cy="{py(v):.1f}" r="3" fill="{PCOL}"/>' for i,v in enumerate(pv)))
    for key,col,dy in (('margenOp',AC,-8),):
        a=an[-1]; i=nn-1; out.append(f'<text x="{L+i*(bw+gap)+bw/2-6:.1f}" y="{ly(a[key])-9:.1f}" font-size="12.5" font-weight="800" fill="{col}" text-anchor="end" style="paint-order:stroke;stroke:{BG};stroke-width:5px;stroke-linejoin:round">{n(a[key],0)}%</text>')
        a=an[0]; out.append(f'<text x="{L+bw/2:.1f}" y="{ly(a[key])+dy:.1f}" font-size="12.5" font-weight="800" fill="{col}" text-anchor="middle" style="paint-order:stroke;stroke:{BG};stroke-width:5px;stroke-linejoin:round">{n(a[key],0)}%</text>')
    return f'<svg width="{CW}" height="{CH}">{"".join(out)}</svg>'
def prev(p):
    tit='PREVISIÓN DE LA EMPRESA'+(f' - {p["periodo"]}' if p.get('periodo') else '')
    if not p['items']: return f'<div class="win" style="margin-top:12px"><div class="wt">{tit}</div><div class="mu" style="font-size:12.5px">{esc(p["nota"])}</div></div>'
    cel=''.join(f'<div><span class="mu una">{esc(x["nombre"])}</span><b class="una">{esc(x["actual"])}</b><span class="mu una">{esc(x["ref"])}</span></div>' for x in p['items'])
    return f'<div class="win" style="margin-top:12px"><div class="wt">{tit}</div><div class="cot" style="grid-template-columns:repeat({len(p["items"])},1fr)">{cel}</div><p style="margin-top:7px">{esc(p["resumen"])}</p></div>'
def hoja2(d):
    c=d['cotizacion']; an=d['diezAnios']; ul=lambda xs:'<ul>'+''.join(f'<li>{esc(x)}</li>' for x in xs)+'</ul>'
    return f'''<div class="page">{band2(d)}
<div class="win" style="margin-top:12px"><div class="wt">{len(an)} AÑOS</div>{chart10(an)}<div class="lg una"><span><span style="color:{CEL}">▮</span> Ingresos (mil M de US$, año fiscal)</span><span><span style="color:{AC}">━</span> {d['margenNombre']}</span><span><span style="color:{MU}">┅</span> Margen neto</span><span><span style="color:{PCOL}">━</span> Precio de la acción al cierre del año fiscal (US$ {n(an[0]['precioCierre'],0)} → US$ {n(an[-1]['precioCierre'],0)})</span></div><div class="mu" style="margin-top:3px">Fuente: {d['fuenteAnual']}; precio: Data912. {d['margenNombre']} de {n(an[0]['margenOp'],0)}% en {an[0]['fin'][:4]} a {n(an[-1]['margenOp'],0)}% en {an[-1]['fin'][:4]}.</div></div>
<div class="g2"><div class="win"><div class="wt">FORTALEZAS</div>{ul(d['fortalezas'])}</div><div class="win"><div class="wt">DEBILIDADES</div>{ul(d['debilidades'])}</div></div>
{prev(d['prevision'])}
<div class="win" style="margin-top:12px"><div class="wt">CONCLUSIÓN</div><p>{esc(d['conclusion'])}</p></div>
{pie(d)}{nro(2)}</div>'''
from playwright.sync_api import sync_playwright
from PIL import Image
with sync_playwright() as pw:
    b=pw.chromium.launch()
    for t in E:
        d=armar(t); errs=controles(d['sankey'],d)
        print(t,'puntaje',d['puntaje'],'controles:',errs or 'OK')
        dd=OUT+t+'/'; os.makedirs(dd,exist_ok=True)
        json.dump(d,open(dd+'datos.json','w'),ensure_ascii=False,indent=1,default=str)
        if errs: continue
        html=f'<html><head><meta charset="utf-8"><style>{css}</style></head><body>{hoja1(d)}{hoja2(d)}</body></html>'
        open(dd+'informe.html','w').write(html)
        pg=b.new_page(viewport={'width':794,'height':1123},device_scale_factor=1.5)
        pg.goto('file://'+dd+'informe.html')
        # lo que no entra en un renglón achica la letra (mínimo 8 px)
        pg.evaluate('''document.querySelectorAll('.una').forEach(e=>{let f=parseFloat(getComputedStyle(e).fontSize);while(e.scrollWidth>e.clientWidth+1&&f>8){f-=0.25;e.style.fontSize=f+'px'}});document.querySelectorAll('.cot').forEach(g=>{for(const k of [1,2,3]){const els=[...g.querySelectorAll(':scope>div>:nth-child('+k+')')];const m=Math.min(...els.map(e=>parseFloat(getComputedStyle(e).fontSize)));els.forEach(e=>e.style.fontSize=m+'px')}});document.querySelectorAll('.win').forEach(w=>{const rs=[...w.querySelectorAll(':scope>.uf')];for(const k of [1,2,3]){const els=rs.map(r=>r.children[k-1]).filter(Boolean);if(!els.length)continue;const m=Math.min(...els.map(e=>parseFloat(getComputedStyle(e).fontSize)));els.forEach(e=>e.style.fontSize=m+'px')}})''')
        # nada cortado: el contenido de cada hoja entra en su alto
        over=pg.evaluate('''[...document.querySelectorAll('.page')].map(p=>{const r=p.getBoundingClientRect();const last=[...p.children].filter(c=>!c.classList.contains('pie')&&!c.classList.contains('nro')).pop().getBoundingClientRect();const pie=p.querySelector('.pie')||p.querySelector('.nro');return Math.round((pie?pie.getBoundingClientRect().top:r.bottom-22)-last.bottom)})''')
        print('  espacio libre antes del pie (px):',over)
        pg.pdf(path=dd+'informe.pdf',format='A4',print_background=True,margin={'top':'0','bottom':'0','left':'0','right':'0'})
        for i,el in enumerate(pg.query_selector_all('.page'),1):
            el.screenshot(path=dd+f'h{i}.png')
            Image.open(dd+f'h{i}.png').convert('RGB').save(dd+f'hoja-{i}.jpg',quality=85,optimize=True,progressive=True); os.remove(dd+f'h{i}.png')
        pg.close()
        print('  tamaños:',{f:round(os.path.getsize(dd+f)/1024) for f in ['informe.pdf','hoja-1.jpg','hoja-2.jpg']},'KB')
    b.close()

import json, os, html, base64, re, sys
import os as _os
B=_os.environ.get('AF_BASE','./trabajo/')
REPO=_os.environ.get('AF_REPO','/home/claude/noticias-mercado/')
AC='#2A5BD7'; CEL='#5BB0E8'; OK='#2F7A3E'; OKL='#8CC79A'; DN='#B03A2E'; WARN='#C98A1B'; GRIS='#8A97AD'; INK='#14213D'; MU='#5E6B85'; LINE='#DCE4F0'; BG='#F3F6FB'
COL={'verde':OK,'amarillo':WARN,'rojo':DN,'gris':GRIS,'sin':GRIS,'na':GRIS}
def n(v,d=1):  # número con coma decimal y punto de miles
    if d==1 and 0<abs(v)<0.1: d=2
    s=f'{v:,.{d}f}'; return s.replace(',','X').replace('.',',').replace('X','.')
def mm(v): return 'US$ '+n(v/1e6,0)+' M'
def pc(v,d=1,signo=True): return ('+' if signo and v>0 else '−' if v<0 else '')+n(abs(v),d)+'%'
def esc(s): return html.escape(s)

# ───────── diagrama de ingresos (genérico) ─────────
def sankey(s):
    """s: segmentos[{nombre,valor,var}], grupo{nombre,miembros[],var}|None, ingresos, varIngresos, costo, bruta, gastos[{nombre,valor}], operativa, otros, impuestos, neta"""
    W=8; X=[6,110,146,180,212,244]; k=118/s['ingresos']
    nodes={}; links=[]; svg=[]
    def node(i,x,y,v,c): nodes[i]=dict(x=x,y=y,h=max(v*k,1.5),v=v,c=c,o=0,inn=0)
    def link(a,b,v,c): links.append((a,b,v,c))
    segs=s['segmentos']; y=0
    for i,g in enumerate(segs):
        h=max(g['valor']*k,1.5); node('s%d'%i,X[0],y,g['valor'],AC if not g.get('servicio') else CEL)
        y+=h+max(4,13-h if h<13 else 6)
    grupo=s.get('grupo')
    if grupo:
        gv=sum(segs[i]['valor'] for i in grupo['miembros']); node('g',X[1],10,gv,AC)
        for i in grupo['miembros']: link('s%d'%i,'g',segs[i]['valor'],AC)
        link('g','rev',gv,AC)
        otros=[i for i in range(len(segs)) if i not in grupo['miembros']]
        yy=10+gv*k+16
        for i in otros:
            node('p%d'%i,X[1],yy,segs[i]['valor'],CEL); link('s%d'%i,'p%d'%i,segs[i]['valor'],CEL); link('p%d'%i,'rev',segs[i]['valor'],CEL); yy+=segs[i]['valor']*k+8
    else:
        for i,g in enumerate(segs): link('s%d'%i,'rev',g['valor'],nodes['s%d'%i]['c'])
    node('rev',X[2],18,s['ingresos'],INK)
    node('gross',X[3],6,s['bruta'],OK); node('cost',X[3],6+s['bruta']*k+14,s['costo'],DN)
    link('rev','gross',s['bruta'],OK); link('rev','cost',s['costo'],DN)
    gt=sum(g['valor'] for g in s['gastos'])
    node('op',X[4],6,s['operativa'],OK); node('opex',X[4],6+s['operativa']*k+14,gt,DN)
    link('gross','op',s['operativa'],OK); link('gross','opex',gt,DN)
    # columna final: neta, impuestos, otros gastos (si los hay) y el detalle de gastos
    y=2; node('neto',X[5],y,s['netaConsolidada'],OK); y+=max(s['netaConsolidada']*k,22)+8
    if s['otros']>=0:
        if s['otros']*k>=0.8: node('oi',X[4],-12,s['otros'],OKL); link('oi','neto',s['otros'],OKL)
        link('op','neto',s['operativa']-s['impuestos'],OK)
    else:
        link('op','neto',s['operativa']-s['impuestos']+s['otros'],OK)
    node('tax',X[5],y,s['impuestos'],DN); link('op','tax',s['impuestos'],DN); h=max(s['impuestos']*k,1.5); y+=h+max(4,12-h)
    if s['otros']<0:
        node('og',X[5],y,-s['otros'],DN); link('op','og',-s['otros'],DN); h=max(-s['otros']*k,1.5); y+=h+max(4,12-h)
    y=max(y,nodes['opex']['y']-6)
    for i,g in enumerate(s['gastos']):
        node('e%d'%i,X[5],y,g['valor'],DN); link('opex','e%d'%i,g['valor'],DN); h=max(g['valor']*k,1.5); y+=h+max(4,12-h)
    for a,b,v,c in links:
        A=nodes[a]; Bn=nodes[b]; w=v*k
        x1=A['x']+W; y1=A['y']+A['o']; x2=Bn['x']; y2=Bn['y']+Bn['inn']; A['o']+=w; Bn['inn']+=w; xm=(x1+x2)/2
        svg.append(f'<path d="M{x1:.1f},{y1:.1f} C{xm:.1f},{y1:.1f} {xm:.1f},{y2:.1f} {x2:.1f},{y2:.1f} L{x2:.1f},{y2+w:.1f} C{xm:.1f},{y2+w:.1f} {xm:.1f},{y1+w:.1f} {x1:.1f},{y1+w:.1f} Z" fill="{c}" opacity=".22"/>')
    for i,nd in nodes.items(): svg.append(f'<rect x="{nd["x"]}" y="{nd["y"]:.1f}" width="{W}" height="{nd["h"]:.1f}" rx="2" fill="{nd["c"]}"/>')
    def t1(x,y,txt,c=INK,anchor='start',fs=9,bold=True): svg.append(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-size="{fs}" font-weight="{700 if bold else 400}" fill="{c}">{esc(txt)}</text>')
    def t2(x,y,a,b,c=INK,anchor='middle'): t1(x,y,a,c,anchor,9.5); t1(x,y+11,b,MU,anchor,8.5,False)
    for i,g in enumerate(segs):
        nd=nodes['s%d'%i]; v='B · '+pc(g['var']) if g.get('var') is not None else 'B'
        if nd['h']>=18: t1(X[0]+W+5,nd['y']+nd['h']/2-2,g['nombre']); t1(X[0]+W+5,nd['y']+nd['h']/2+9,n(g['valor']/1e9,1)+' '+v,MU,fs=8.5,bold=False)
        else: t1(X[0]+W+5,nd['y']+nd['h']/2+3,g['nombre']+'  '+n(g['valor']/1e9,1)+' '+v,fs=8.5)
    if grupo:
        t2(X[1]+8,-2,grupo['nombre'],n(nodes['g']['v']/1e9,1)+' B · '+pc(grupo['var']),AC,'end')
        for i in [i for i in range(len(segs)) if i not in grupo['miembros']]: pass
    rv=nodes['rev']; t2(X[2]+4,rv['y']+rv['h']+12,'INGRESOS',n(s['ingresos']/1e9,1)+' B · '+pc(s['varIngresos']))
    t2(X[3]+8,-12,'Bruta',n(s['bruta']/1e9,1)+' · '+n(s['bruta']/s['ingresos']*100,0)+'%',OK,'end')
    t2(X[4]-2,-12,'Operativa',n(s['operativa']/1e9,1)+' · '+n(s['operativa']/s['ingresos']*100,0)+'%',OK,'start')
    cs=nodes['cost']; t2(X[3]+13,cs['y']+cs['h']+12,'Costo',n(s['costo']/1e9,1)+' B',DN,'start')
    ox=nodes['opex']; t2(X[4]+4,ox['y']+ox['h']+12,'Gastos',n(gt/1e9,1)+' B',DN)
    nt=nodes['neto']; t1(X[5]+W+4,nt['y']+min(nt['h'],40)/2-1,'Ganancia neta'); t1(X[5]+W+4,nt['y']+min(nt['h'],40)/2+10,n(s['neta']/1e9,1)+' B · '+n(s['neta']/s['ingresos']*100,0)+'%',MU,fs=8.5,bold=False)
    tx=nodes['tax']; t1(X[5]+W+4,tx['y']+tx['h']/2+3,'Impuestos  '+n(s['impuestos']/1e9,1)+' B',fs=8.5)
    if 'og' in nodes: g=nodes['og']; t1(X[5]+W+4,g['y']+g['h']/2+3,'Otros gastos  '+n(-s['otros']/1e9,1)+' B',fs=8.5)
    for i,g in enumerate(s['gastos']):
        e=nodes['e%d'%i]; t1(X[5]+W+4,e['y']+e['h']/2+3,g['nombre']+'  '+n(g['valor']/1e9,1)+' B',fs=8.5)
    bottom=max(nd['y']+nd['h'] for nd in nodes.values())+28
    return f'<svg width="360" height="{bottom+20:.0f}" viewBox="0 -24 360 {bottom+20:.0f}">{"".join(svg)}</svg>', nodes

def controles(s, d):
    errs=[]
    if abs(s['ingresos']-s['costo']-s['bruta'])>0.005*s['ingresos']: errs.append('ingresos − costo ≠ ganancia bruta')
    if abs(sum(g['valor'] for g in s['segmentos'])-s['ingresos'])>0.005*s['ingresos']: errs.append('los segmentos no suman los ingresos')
    gt=sum(g['valor'] for g in s['gastos'])
    if abs(s['bruta']-gt-s['operativa'])>0.005*s['ingresos']: errs.append('bruta − gastos ≠ operativa')
    if abs(s['operativa']+s['otros']-s['impuestos']-s['netaConsolidada'])>0.005*s['ingresos']: errs.append('operativa + otros − impuestos ≠ neta')
    for nom,v in [('bruto',s['bruta']/s['ingresos']*100),('operativo',s['operativa']/s['ingresos']*100),('neto',s['neta']/s['ingresos']*100)]+[('anual '+a['fin'][:4],a['margenOp']) for a in d['diezAnios']]+[('neto '+a['fin'][:4],a['margenNeto']) for a in d['diezAnios']]:
        if not -100<=v<=100: errs.append(f'margen {nom} fuera de rango ({v})')
    g=d.get('cincoAnios')
    if g:
        if len(g['ingresos12m'])<16 or len(g['gpa12m'])<16: errs.append('5 años: faltan trimestres')
        if any(x['valor']<=0 for x in g['ingresos12m']+g['precio']): errs.append('5 años: ingresos o precio no positivos')
        ing=d['calculos']['ingresos']
        if abs(g['ingresos12m'][-1]['valor']-ing)>0.005*ing: errs.append('5 años: el último ingreso de 12 meses no coincide con el del semáforo')
    texto=json.dumps(d,ensure_ascii=False).lower()
    for p in re.findall(r'(?<![\wáéíóúñ])(barat[ao]s?|car[ao]s?|atractiv\w*|conviene|convendría|oportunidad\w*|comprar|vender|mantener)(?![\wáéíóúñ])',texto):
        errs.append('palabra no permitida: '+p)
    for f in d['fuentes']:
        if not f['url'].startswith('https://'): errs.append('link sin https: '+f['url'])
    for x in d['semaforo']:
        if re.search(r'\d{1,2}/\d{1,2}/\d{2,4}',x['dato']): errs.append('dato con fecha en el semáforo')
    return errs

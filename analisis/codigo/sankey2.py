from informe import AC, CEL, OK, OKL, DN, INK, MU, n, pc, esc
def mil(v):
    """Monto en miles de millones: '62,6 mil M' (2 decimales si es menos de mil millones)."""
    x=v/1e9; d=1 if abs(x)>=1 else 2
    s=f'{abs(x):,.{d}f}'.replace(',','X').replace('.',',').replace('X','.')
    return ('−' if x<0 else '')+s+' mil M'
def sankey(s, SW=700, H=200):
    W=9; X=[8,int(SW*.42),int(SW*.52),int(SW*.60),int(SW*.67),int(SW*.735)]; k=H/s['ingresos']
    nodes={}; links=[]; svg=[]
    def node(i,x,y,v,c): nodes[i]=dict(x=x,y=y,h=max(v*k,1.8),v=v,c=c,o=0,inn=0)
    def link(a,b,v,c): links.append((a,b,v,c))
    segs=s['segmentos']; y=0
    for i,g in enumerate(segs):
        h=max(g['valor']*k,1.8); node('s%d'%i,X[0],y,g['valor'],CEL if g.get('servicio') else AC); y+=max(h,32)+9
    grupo=s.get('grupo')
    if grupo:
        gv=sum(segs[i]['valor'] for i in grupo['miembros']); node('g',X[1],12,gv,AC)
        for i in grupo['miembros']: link('s%d'%i,'g',segs[i]['valor'],AC)
        link('g','rev',gv,AC); yy=12+gv*k+18
        for i in [i for i in range(len(segs)) if i not in grupo['miembros']]:
            node('p%d'%i,X[1],yy,segs[i]['valor'],CEL); link('s%d'%i,'p%d'%i,segs[i]['valor'],CEL); link('p%d'%i,'rev',segs[i]['valor'],CEL); yy+=segs[i]['valor']*k+8
    else:
        for i,g in enumerate(segs): link('s%d'%i,'rev',g['valor'],nodes['s%d'%i]['c'])
    node('rev',X[2],20,s['ingresos'],INK)
    node('gross',X[3],8,s['bruta'],OK); node('cost',X[3],8+s['bruta']*k+18,s['costo'],DN)
    link('rev','gross',s['bruta'],OK); link('rev','cost',s['costo'],DN)
    gt=sum(g['valor'] for g in s['gastos'])
    node('op',X[4],8,s['operativa'],OK); node('opex',X[4],8+s['operativa']*k+18,gt,DN)
    link('gross','op',s['operativa'],OK); link('gross','opex',gt,DN)
    y=2; node('neto',X[5],y,s['netaConsolidada'],OK); y+=max(s['netaConsolidada']*k,30)+9
    if s['otros']>=0:
        link('op','neto',s['operativa']-s['impuestos'],OK)
        if s['otros']*k>=0.8: node('oi',X[4],8+s['operativa']*k+5,s['otros'],OKL); link('oi','neto',s['otros'],OKL)
    else: link('op','neto',s['operativa']-s['impuestos']+s['otros'],OK)
    node('tax',X[5],y,s['impuestos'],DN); link('op','tax',s['impuestos'],DN); h=max(s['impuestos']*k,1.8); y+=h+max(5,16-h)
    if s['otros']<0:
        node('og',X[5],y,-s['otros'],DN); link('op','og',-s['otros'],DN); h=max(-s['otros']*k,1.8); y+=h+max(5,16-h)
    y=max(y,nodes['opex']['y']-6)
    for i,g in enumerate(s['gastos']):
        node('e%d'%i,X[5],y,g['valor'],DN); link('opex','e%d'%i,g['valor'],DN); h=max(g['valor']*k,1.8); y+=h+max(5,16-h)
    for a,b,v,c in links:
        A=nodes[a]; Bn=nodes[b]; w=v*k; x1=A['x']+W; y1=A['y']+A['o']; x2=Bn['x']; y2=Bn['y']+Bn['inn']; A['o']+=w; Bn['inn']+=w; xm=(x1+x2)/2
        svg.append(f'<path d="M{x1:.1f},{y1:.1f} C{xm:.1f},{y1:.1f} {xm:.1f},{y2:.1f} {x2:.1f},{y2:.1f} L{x2:.1f},{y2+w:.1f} C{xm:.1f},{y2+w:.1f} {xm:.1f},{y1+w:.1f} {x1:.1f},{y1+w:.1f} Z" fill="{c}" opacity=".22"/>')
    for i,nd in nodes.items(): svg.append(f'<rect x="{nd["x"]}" y="{nd["y"]:.1f}" width="{W}" height="{nd["h"]:.1f}" rx="2" fill="{nd["c"]}"/>')
    def t1(x,y,txt,c=INK,anchor='start',fs=12,bold=True): svg.append(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-size="{fs}" font-weight="{700 if bold else 400}" fill="{c}">{esc(txt)}</text>')
    def t2(x,y,a,b,c=INK,anchor='middle'): t1(x,y,a,c,anchor,12); t1(x,y+14,b,MU,anchor,12,False)
    for i,g in enumerate(segs):
        nd=nodes['s%d'%i]; v=mil(g['valor'])+(' · '+pc(g['var']) if g.get('var') is not None else '')
        nombre=g['nombre']+(f" ({g['oficial']})" if g.get('oficial') else '')
        cy=nd['y']+max(nd['h'],32)/2; t1(X[0]+W+6,cy-2,nombre); t1(X[0]+W+6,cy+12,v,MU,fs=12,bold=False)
    if grupo: t2(X[1]+9,-4,grupo['nombre'],mil(nodes['g']['v'])+' · '+pc(grupo['var']),AC,'end')
    rv=nodes['rev']; t2(X[2]+4,rv['y']+rv['h']+16,'INGRESOS',mil(s['ingresos'])+' · '+pc(s['varIngresos']))
    t2(X[3]+9,-18,'Ganancia bruta',mil(s['bruta'])+' · '+n(s['bruta']/s['ingresos']*100,0)+'%',OK,'end')
    t2(X[4]-2,-18,'Ganancia operativa',mil(s['operativa'])+' · '+n(s['operativa']/s['ingresos']*100,0)+'%',OK,'start')
    cs=nodes['cost']; t2(X[3]+15,cs['y']+cs['h']+16,'Costo',mil(s['costo']),DN,'start')
    ox=nodes['opex']; t2(X[4]+4,ox['y']+ox['h']+16,'Gastos',mil(gt),DN)
    nt=nodes['neto']; cy=nt['y']+min(nt['h'],44)/2
    t1(X[5]+W+5,cy-2,'Ganancia neta',fs=12); t1(X[5]+W+5,cy+13,mil(s['neta'])+' · '+n(s['neta']/s['ingresos']*100,0)+'%',MU,fs=12,bold=False)
    tx=nodes['tax']; t1(X[5]+W+5,tx['y']+tx['h']/2+3.5,'Impuestos  '+mil(s['impuestos']),fs=12)
    if 'og' in nodes: g=nodes['og']; t1(X[5]+W+5,g['y']+g['h']/2+3.5,s.get('otrosNombre','Otros gastos')+'  '+mil(-s['otros']),fs=12)
    for i,g in enumerate(s['gastos']): e=nodes['e%d'%i]; t1(X[5]+W+5,e['y']+e['h']/2+3.5,g['nombre']+'  '+mil(g['valor']),fs=12)
    bottom=max(nd['y']+nd['h'] for nd in nodes.values())+32
    return f'<svg width="{SW}" height="{bottom+34:.0f}" viewBox="0 -34 {SW} {bottom+34:.0f}">{"".join(svg)}</svg>'

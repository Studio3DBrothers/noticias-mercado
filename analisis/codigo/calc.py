import sys, json, datetime as dt
sys.path.insert(0,'.')
from sec import Facts
R='/tmp/claude-0/-home-claude/990d0e6d-c245-5c61-9829-7455ebe8c7a2/scratchpad/af2/raw/'
REV=['RevenueFromContractWithCustomerExcludingAssessedTax','Revenues','SalesRevenueNet']
def prior_ttm(f, cs, hasta):
    """Ingresos de los 12 meses que terminan un año antes (para el crecimiento)."""
    c,es=f.entries(cs)
    es=[e for e in es if 'start' in e]
    best={}
    for e in es:
        k=(e['start'],e['end'])
        if k not in best or e['filed']>best[k]['filed']: best[k]=e
    es=list(best.values()); D=dt.date.fromisoformat
    objetivo=D(hasta)-dt.timedelta(days=364)
    anual=[e for e in es if abs((D(e['end'])-objetivo).days)<=7 and 350<=(D(e['end'])-D(e['start'])).days<=380]
    if anual: return max(anual,key=lambda e:e['filed'])['val']
    ytd=[e for e in es if abs((D(e['end'])-objetivo).days)<=7 and (D(e['end'])-D(e['start'])).days<350]
    if not ytd: return None
    y=max(ytd,key=lambda e:(D(e['end'])-D(e['start'])).days); ini=D(y['start']); dur=(D(y['end'])-ini).days
    fy=[e for e in es if abs((D(e['end'])-(ini-dt.timedelta(days=1))).days)<=4 and 350<=(D(e['end'])-D(e['start'])).days<=380]
    pv=[e for e in es if abs((D(e['end'])-(objetivo-dt.timedelta(days=364))).days)<=7 and abs((D(e['end'])-D(e['start'])).days-dur)<=7]
    if not fy or not pv: return None
    return max(fy,key=lambda e:e['filed'])['val']+y['val']-max(pv,key=lambda e:e['filed'])['val']
def ultimo(f, cs):
    c,a=f.instante(cs)
    return (list(a.values())[-1]['val'], list(a)[-1]) if a else (None,None)
def metricas(cik, precio, debt_cs, cash_cs, da_cs):
    f=Facts(R+f'cf_{cik}.json'); m={}
    _,rev,mr=f.ttm(REV); _,op,_=f.ttm(['OperatingIncomeLoss']); _,net,_=f.ttm(['NetIncomeLoss'])
    _,eps,_=f.ttm(['EarningsPerShareDiluted'],'USD/shares'); _,ocf,_=f.ttm(['NetCashProvidedByUsedInOperatingActivities'])
    _,capex,_=f.ttm(['PaymentsToAcquirePropertyPlantAndEquipment']); _,div,_=f.ttm(['PaymentsOfDividends','PaymentsOfDividendsCommonStock'])
    _,buy,_=f.ttm(['PaymentsForRepurchaseOfCommonStock'])
    da=0
    for cs in da_cs:
        _,v,_=f.ttm([cs]); da+=v or 0
    eq,feq=ultimo(f,['StockholdersEquity'])
    debt=0; dd={}
    for cs in debt_cs:
        v,fe=ultimo(f,[cs])
        if v is not None and fe==feq: debt+=v; dd[cs]=v
    cash=0; cd={}
    for cs in cash_cs:
        v,fe=ultimo(f,[cs])
        if v is not None and fe==feq: cash+=v; cd[cs]=v
    sh=sorted(f.f['dei']['EntityCommonStockSharesOutstanding']['units']['shares'],key=lambda e:e['end'])[-1]
    rev_prev=prior_ttm(f,REV,mr['hasta'])
    mcap=sh['val']*precio
    m=dict(hasta=mr['hasta'],como=mr['como'],ingresos=rev,ingresosAnt=rev_prev,operativa=op,neta=net,eps=eps,flujoOperativo=ocf,inversiones=capex,
           dividendos=div,recompras=buy,amortizaciones=da,patrimonio=eq,fechaBalance=feq,deuda=debt,deudaDetalle=dd,caja=cash,cajaDetalle=cd,
           acciones=sh['val'],fechaAcciones=sh['end'],precio=precio,capitalizacion=mcap)
    m['pe']=precio/eps; m['margenOp']=op/rev*100; m['roe']=net/eq*100
    m['ebitda']=op+da; m['deudaNeta']=debt-cash; m['dnEbitda']=(debt-cash)/m['ebitda']
    m['fcf']=ocf-capex; m['margenFcf']=m['fcf']/rev*100; m['crec']=(rev/rev_prev-1)*100
    m['retorno']=(div+buy)/mcap*100; m['rendDiv']=div/mcap*100
    return f,m
def anios(f, n=10):
    _,r=f.anual(REV); _,o=f.anual(['OperatingIncomeLoss']); _,ne=f.anual(['NetIncomeLoss'])
    out=[]
    for k in list(r)[-n:]:
        if k in o and k in ne:
            out.append({'fin':k,'ingresos':r[k]['val'],'margenOp':round(o[k]['val']/r[k]['val']*100,1),'margenNeto':round(ne[k]['val']/r[k]['val']*100,1),'presentado':r[k]['filed'],'formulario':r[k]['form']})
    return out
def semaforo(m):
    def c3(v,verde,amar,mayor=True):
        if v is None: return 'sin'
        if mayor: return 'verde' if v>=verde else 'amarillo' if v>=amar else 'rojo'
        return 'verde' if v<verde else 'amarillo' if v<=amar else 'rojo'
    pe=c3(m['pe'],20,35,False)
    r1=c3(m['margenOp'],20,10); r2=c3(m['roe'],15,8)
    orden=['verde','amarillo','rojo']; rent=max(r1,r2,key=orden.index)
    bal='verde' if m['deudaNeta']<=0 else c3(m['dnEbitda'],1.5,3,False)
    fcf=c3(m['margenFcf'],15,5); cre=c3(m['crec'],10,3)
    ret='gris' if m['retorno']<=0 else c3(m['retorno'],3,1)
    pesos={'valuacion':.20,'rentabilidad':.20,'balance':.15,'flujo':.20,'crecimiento':.20,'dividendos':.05}
    est={'valuacion':pe,'rentabilidad':rent,'balance':bal,'flujo':fcf,'crecimiento':cre,'dividendos':ret}
    val={'verde':10,'amarillo':5,'rojo':0}
    cuentan={k:v for k,v in est.items() if v in val}
    tot=sum(pesos[k] for k in cuentan)
    puntaje=sum(val[v]*pesos[k] for k,v in cuentan.items())/tot
    return est, round(puntaje+1e-9,1)

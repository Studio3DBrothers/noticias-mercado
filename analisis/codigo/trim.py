"""Serie trimestral (3 meses) desde companyfacts: Q1-Q3 directos del 10-Q, Q4 = año fiscal − 9 meses."""
import datetime as dt
from sec import Facts, D
def trimestres(f, concepts, unit='USD'):
    for c in concepts:
        _,es=f.entries([c],unit)
        if not es: continue
        best={}
        for e in es:
            if 'start' not in e: continue
            k=(e['start'],e['end'])
            if k not in best or e['filed']>best[k]['filed']: best[k]=e
        q={}; anual={}; nueve={}
        for (s,e),x in best.items():
            d=(D(e)-D(s)).days
            if 80<=d<=100: q[e]=x['val']
            elif 350<=d<=380: anual[e]=(s,x['val'])
            elif 260<=d<=285: nueve[(s,e)]=x['val']
        for fin,(ini,v) in anual.items():
            if fin in q: continue
            n9=[val for (s,e),val in nueve.items() if s==ini and 80<=(D(fin)-D(e)).days<=100]
            if n9: q[fin]=v-n9[0]
        yield c,dict(sorted(q.items()))
def serie_ttm(f, concepts, unit='USD'):
    """Une los conceptos (el primero manda) y devuelve [(fin_trimestre, suma de 4 trimestres)]."""
    q={}
    for c,d in trimestres(f,concepts,unit):
        for k,v in d.items(): q.setdefault(k,v)
    ks=sorted(q); out=[]
    for i in range(3,len(ks)):
        w=ks[i-3:i+1]
        if (D(w[-1])-D(w[0])).days<300: out.append((w[-1],sum(q[k] for k in w)))
    return out
if __name__=='__main__':
    import sys,json
    from calc import REV
    for cik in ['0000320193','0000789019','0000021344']:
        f=Facts(f'../raw/cf_{cik}.json')
        r=serie_ttm(f,REV); e=serie_ttm(f,['EarningsPerShareDiluted'],'USD/shares')
        print(f.name,len(r),r[-21:][0],r[-1],'|',len(e),e[-21:][0],e[-1])

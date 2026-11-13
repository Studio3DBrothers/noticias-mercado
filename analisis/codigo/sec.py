import json, datetime as dt
D=lambda s: dt.date.fromisoformat(s)
class Facts:
    def __init__(s, path):
        j=json.load(open(path)); s.name=j['entityName']; s.f=j['facts']
    def entries(s, concepts, unit='USD', tax='us-gaap'):
        for c in concepts:
            u=s.f.get(tax,{}).get(c,{}).get('units',{})
            if unit in u and u[unit]: return c,u[unit]
        return None,[]
    def anual(s, concepts, unit='USD'):
        c,es=s.entries(concepts,unit); out={}
        for e in es:
            if e.get('form') not in ('10-K','10-K/A') or 'start' not in e: continue
            d=(D(e['end'])-D(e['start'])).days
            if 350<=d<=380:
                k=e['end']
                if k not in out or e['filed']>out[k]['filed']: out[k]=e
        return c,dict(sorted(out.items()))
    def instante(s, concepts, unit='USD'):
        c,es=s.entries(concepts,unit); out={}
        for e in es:
            if 'start' in e: continue
            k=e['end']
            if k not in out or e['filed']>out[k]['filed']: out[k]=e
        return c,dict(sorted(out.items()))
    def ttm(s, concepts, unit='USD'):
        """Últimos 12 meses: FY + acumulado del año en curso − acumulado igual del año anterior."""
        c,es=s.entries(concepts,unit)
        es=[e for e in es if 'start' in e]
        if not es: return c,None,None
        best={}
        for e in es:
            k=(e['start'],e['end'])
            if k not in best or e['filed']>best[k]['filed']: best[k]=e
        es=list(best.values())
        fin=max(e['end'] for e in es)
        cand=[e for e in es if e['end']==fin]
        largo=max(cand,key=lambda e:(D(e['end'])-D(e['start'])).days)
        dur=(D(largo['end'])-D(largo['start'])).days
        if dur>=350: return c,largo['val'],{'hasta':fin,'como':'año fiscal','filed':largo['filed']}
        ini=D(largo['start'])
        # año fiscal anterior: termina el día antes del inicio del acumulado
        fy=[e for e in es if abs((D(e['end'])-(ini-dt.timedelta(days=1))).days)<=4 and 350<=(D(e['end'])-D(e['start'])).days<=380]
        prev=[e for e in es if abs((D(e['end'])-(D(fin)-dt.timedelta(days=364))).days)<=7 and abs((D(e['end'])-D(e['start'])).days-dur)<=7]
        if not fy or not prev: return c,None,{'hasta':fin,'error':'faltan piezas'}
        fy=max(fy,key=lambda e:e['filed']); prev=max(prev,key=lambda e:e['filed'])
        return c,fy['val']+largo['val']-prev['val'],{'hasta':fin,'como':f"FY {fy['end']} + acumulado {largo['start']}→{fin} − {prev['start']}→{prev['end']}",'filed':largo['filed']}
    def ultimo_trim(s, concepts, unit='USD'):
        """Valor de los últimos 3 meses (si el último dato es anual o de 6/9 meses, se resta el acumulado anterior)."""
        c,es=s.entries(concepts,unit)
        es=[e for e in es if 'start' in e]
        best={}
        for e in es:
            k=(e['start'],e['end'])
            if k not in best or e['filed']>best[k]['filed']: best[k]=e
        es=list(best.values())
        if not es: return c,None,None
        fin=max(e['end'] for e in es)
        cand={(D(e['end'])-D(e['start'])).days:e for e in es if e['end']==fin}
        for d,e in cand.items():
            if 80<=d<=100: return c,e['val'],{'desde':e['start'],'hasta':fin}
        largo=cand[max(cand)]
        ini=largo['start']
        # acumulado que termina ~3 meses antes con el mismo inicio
        prev=[e for e in es if e['start']==ini and 70<=(D(fin)-D(e['end'])).days<=110]
        if not prev: return c,None,{'hasta':fin,'error':'sin acumulado previo'}
        p=max(prev,key=lambda e:e['end'])
        return c,largo['val']-p['val'],{'desde':p['end'],'hasta':fin,'como':'acumulado − acumulado previo'}

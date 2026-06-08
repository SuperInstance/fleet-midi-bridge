"""Production engine for fleet MIDI service."""
import json
def process(v, base=60):
    n=[base]
    for x in v:
        if x==1: n.append(n[-1]+4)
        elif x==-1: n.append(n[-1]-4)
        else: n.append(n[-1])
    return {'notes':n,'vector':v,'length':len(n)}
def stats(v):
    d=sum(1 for x in v if x!=0)/len(v)
    b=(sum(1 for x in v if x==1)-sum(1 for x in v if x==-1))/len(v)
    return {'density':d,'balance':b}
if __name__=='__main__':
    v=[1,0,-1,1,0,-1,1,1]
    r=process(v)
    print(json.dumps({**r,'stats':stats(v)}))

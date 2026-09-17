import json,sys
a=json.load(open(sys.argv[1]));b=json.load(open(sys.argv[2]))
n=0
for k in sorted(set(a)|set(b)):
    if k not in a or k not in b: print('MISSING route',k); n+=1; continue
    A,B=a[k],b[k]
    if set(A)!=set(B): print('ELEMSET',k,len(A),len(B)); n+=1
    for e in set(A)&set(B):
        for p in set(A[e])|set(B[e]):
            if A[e].get(p)!=B[e].get(p):
                n+=1
                if n<40: print(k,e[:90],p,A[e].get(p),'->',B[e].get(p))
print('DIFFS',n, 'routes',len(a),'elements',sum(len(v) for v in a.values()))

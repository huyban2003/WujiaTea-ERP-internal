import json,sys,os,re
# CDIFF_IGNORE='<regex đường dẫn phần tử>' — bỏ qua thuộc tính hình học dao động theo đồng hồ (thanh tiến độ khung giờ đặt hàng)
IGN=re.compile(os.environ['CDIFF_IGNORE']) if os.environ.get('CDIFF_IGNORE') else None
GEO={'width','inline-size','perspective-origin','transform-origin'}
a=json.load(open(sys.argv[1]));b=json.load(open(sys.argv[2]))
n=0
for k in sorted(set(a)|set(b)):
    if k not in a or k not in b: print('MISSING route',k); n+=1; continue
    A,B=a[k],b[k]
    if set(A)!=set(B): print('ELEMSET',k,len(A),len(B)); n+=1
    for e in set(A)&set(B):
        for p in set(A[e])|set(B[e]):
            if A[e].get(p)!=B[e].get(p):
                if IGN and p in GEO and IGN.search(e): continue
                n+=1
                if n<40: print(k,e[:90],p,A[e].get(p),'->',B[e].get(p))
print('DIFFS',n, 'routes',len(a),'elements',sum(len(v) for v in a.values()))

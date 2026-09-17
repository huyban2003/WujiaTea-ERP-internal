import json, re, sys
sys.path.insert(0, sys.argv[1])
moves=json.load(open(sys.argv[1]+'/moves.json'))
ROOT='/Users/huyban2003/odoo-dev/WujiaTea/custom/'
D=ROOT+'wujia_portal_layout/static/assets/css/'
MODCSS={'wujia_portal_knowledge':'static/src/css/portal_knowledge.css','wujia_portal_purchase_history':'static/src/css/portal_history.css',
        'wujia_portal_support':'static/src/css/portal_support.css','wujia_portal_notification':'static/src/css/portal_notification.css'}
byfile={}
for m in moves: byfile.setdefault(m['file'],[]).append(m)
chunks={}  # owner -> list of (file, media tuple, text)
for f,ms in byfile.items():
    t=open(D+f).read()
    spans=[]
    for m in sorted(ms,key=lambda x:x['start']):
        ls=t.rfind('\n',0,m['start'])+1
        s=ls if t[ls:m['start']].strip()=='' else m['start']
        e=m['end']
        if t[e:e+1]=='\n': e+=1
        body=t[m['start']:m['end']]
        chunks.setdefault(m['owner'],[]).append((f,tuple(m['media']),m['line'],body))
        spans.append((s,e))
    for s,e in sorted(spans,reverse=True):
        t=t[:s]+t[e:]
    open(D+f,'w').write(t)
for owner,items in chunks.items():
    out=[]; cur=None
    for f,media,line,body in items:
        key=(f,media)
        if key!=cur:
            if cur and cur[1]: out.append('}\n')
            out.append(f'/* F2: dời từ portal_layout {f}:{line} */\n')
            if media: out.append(media[0]+' {\n')
            cur=key
        ind='    ' if media else ''
        lines=body.split('\n')
        # re-indent: first line gets ind, others keep relative indent from source
        out.append(ind+lines[0]+'\n'+''.join(l+'\n' for l in lines[1:]))
    if cur and cur[1]: out.append('}\n')
    block=''.join(out)
    p=ROOT+owner+'/'+MODCSS[owner]
    t=open(p).read()
    m=re.match(r'\s*/\*.*?\*/\n?', t, flags=re.S)
    k=m.end() if m else 0
    t=t[:k]+('\n' if k else '')+block+'\n'+t[k:]
    open(p,'w').write(t)
    print(owner, len(items), 'rules ->', p)

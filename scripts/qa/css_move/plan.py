import re, sys, json
sys.path.insert(0, sys.argv[1])
from cssparse import *
ROOT='/Users/huyban2003/odoo-dev/WujiaTea'
rep=open(sys.argv[2]).read()
owners={}
cur=None
for line in rep.splitlines():
    m=re.match(r'### → `(\w+)`', line)
    if m: cur=m.group(1); continue
    if line.startswith('### '): cur=None
    m=re.match(r'- `([\w-]+)` — ', line)
    if m and cur: owners[m.group(1)]=cur
TARGET={'wujia_portal_knowledge','wujia_portal_purchase_history','wujia_portal_support','wujia_portal_notification',
        'wujia_portal_debt','wujia_portal_exam','wujia_portal_return','wujia_portal_delivery'}
KEEP={'wujia-msheet-open','wj-filter-select','wj-inspection-pc','wj-pc-page-btn'}
files=['_components.css','_pc_components.css','_pc_account.css','_interaction.css']
D=ROOT+'/custom/wujia_portal_layout/static/assets/css/'
moves=[]; mixed=[]
allrules=[]
for fi,f in enumerate(files):
    t=open(D+f).read()
    for r in flat_rules(parse(t),t):
        r['file']=f; r['fi']=fi; r['line']=t.count('\n',0,r['start'])+1
        allrules.append(r)
        if ':is(' in r['sel']: continue
        parts=split_selectors(r['sel'])
        po=[]
        for p in parts:
            gs={group(c) for c in classes(p)}
            os_={owners[g] for g in gs if g in owners and owners[g] in TARGET and g not in KEEP}
            po.append(os_)
        if not any(po): continue
        mods=set().union(*po)
        if len(mods)>1 or not all(po):
            mixed.append((f,r['line'],r['sel'],[sorted(x) for x in po])); continue
        r['owner']=mods.pop(); moves.append(r)
print('MOVES',len(moves))
from collections import Counter
print(Counter((m['owner'],m['file']) for m in moves))
print('MIXED/SKIP'); [print(' ',x) for x in mixed]
# cascade check: later layout rules (not moved) sharing a class of moved rule's parts and a property
moved_ids={id(m) for m in moves}
for m in moves:
    mcls=set().union(*[classes(p) for p in split_selectors(m['sel'])])
    mprops={k for k,_ in decls(m['body'])}
    for r in allrules:
        if id(r) in moved_ids: continue
        if (r['fi'],r['start'])<=(m['fi'],m['start']): continue
        rc=set().union(*[classes(p) for p in split_selectors(r['sel'])])
        inter=(mcls & rc) - {'is-active','is-open','wj-data-item','wj-data-list--compact-row','is-unread','is-stacked'}
        rprops={k for k,_ in decls(r['body'])}
        props={a for a in mprops for b in rprops if a==b or a.startswith(b+'-') or b.startswith(a+'-')}
        if inter and props:
            print('CASCADE?',m['file'],m['line'],m['sel'][:60],'<->',r['file'],r['line'],r['sel'][:80],sorted(props))
            m.setdefault('conf',[]).append((r['file'],r['line'],r['sel'][:80],sorted(props)))
json.dump([dict(conf=m.get('conf'),file=m['file'],line=m['line'],start=m['start'],end=m['end'],sel=m['sel'],media=m['media'],owner=m['owner']) for m in moves],open(sys.argv[1]+'/moves.json','w'),ensure_ascii=False,indent=1)

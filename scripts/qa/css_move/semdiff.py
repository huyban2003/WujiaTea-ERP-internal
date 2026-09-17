import sys, subprocess, re
sys.path.insert(0, sys.argv[1])
from cssparse import *
R='/Users/huyban2003/odoo-dev/WujiaTea/'
L=['custom/wujia_portal_layout/static/assets/css/'+f for f in ['_components.css','_pc_components.css','_pc_account.css','_interaction.css']]
M=['custom/wujia_portal_knowledge/static/src/css/portal_knowledge.css','custom/wujia_portal_purchase_history/static/src/css/portal_history.css',
   'custom/wujia_portal_support/static/src/css/portal_support.css','custom/wujia_portal_notification/static/src/css/portal_notification.css',
   'custom/wujia_portal_debt/static/src/css/portal_debt.css','custom/wujia_portal_exam/static/src/css/portal_exam.css',
   'custom/wujia_portal_return/static/src/css/portal_return.css','custom/wujia_portal_delivery/static/src/css/portal_delivery.css']
from collections import Counter
def atoms(text):
    c=Counter()
    for r in flat_rules(parse(text),text):
        for p in split_selectors(r['sel']):
            for k,v in decls(r['body']):
                c[(' | '.join(r['media']),' '.join(p.split()),k,v)]+=1
    return c
def old(p): return subprocess.run(['git','show','HEAD:'+p],cwd=R,capture_output=True,text=True).stdout
lost=Counter(); gain=Counter()
for p in L:
    a,b=atoms(old(p)),atoms(open(R+p).read()); lost+=a-b; gain+=b-a
mg=Counter(); ml=Counter()
for p in M:
    a,b=atoms(old(p)),atoms(open(R+p).read()); mg+=b-a; ml+=a-b
print('layout lost',sum(lost.values()),'layout gained',sum(gain.values()))
print('modules gained',sum(mg.values()),'modules lost',sum(ml.values()))
print('lost-not-gained',sum((lost-mg).values()),'gained-not-lost',sum((mg-lost).values()))
for x in list((lost-mg))[:10]+list((mg-lost))[:10]: print(' ',x)

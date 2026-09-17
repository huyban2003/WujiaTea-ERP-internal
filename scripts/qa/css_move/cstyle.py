"""Dump FULL computed style (+ :hover/:active forced) of elements whose class hits screen groups."""
import json, sys, asyncio
from playwright.async_api import async_playwright
BASE='http://127.0.0.1:8099'
ACC={'anh.owner':['/portal/knowledge','/portal/knowledge/pha-tr-earl-grey-size-l','/portal/purchase-history','/portal/purchase-history/12',
      '/portal/support','/portal/support/15','/portal/support/new','/portal/notification','/portal/notification/1'],
     'em.hcm':['/portal/knowledge','/portal/purchase-history','/portal/support','/portal/support/67','/portal/notification']}
PREF=['wujia-mknow','wujia-mhist','wujia-mticket','wj-pc-noti-head-actions']
JS='''(pref)=>{const out={};const els=[...document.querySelectorAll('*')].filter(e=>{const c=(e.getAttribute('class')||'');return pref.some(p=>c.includes(p))});
const sub=[];for(const e of els){sub.push(e);for(const k of e.querySelectorAll('*'))sub.push(k)}
const uniq=[...new Set(sub)];
uniq.forEach((e,i)=>{const cs=getComputedStyle(e);const o={};for(const p of cs)o[p]=cs.getPropertyValue(p);
 for(const ps of ['::before','::after']){const c2=getComputedStyle(e,ps);o[ps+'content']=c2.content;o[ps+'bg']=c2.backgroundColor;o[ps+'w']=c2.width}
 let path=e.tagName+'.'+(e.getAttribute('class')||'');let p=e.parentElement,d=0;while(p&&d<3){path=p.tagName+'>'+path;p=p.parentElement;d++}
 out[i+'|'+path]=o});return out}'''
async def main(tag):
    res={}
    async with async_playwright() as pw:
        b=await pw.chromium.launch()
        for login,routes in ACC.items():
            for w in (390,1440):
                ctx=await b.new_context(viewport={'width':w,'height':900})
                pg=await ctx.new_page()
                await pg.goto(BASE+'/web/login'); await pg.fill('input[name=login]',login); await pg.fill('input[name=password]','wujia@test123')
                await pg.click('button[type=submit]'); await pg.wait_for_load_state('networkidle')
                for r in routes:
                    await pg.goto(BASE+r); await pg.wait_for_load_state('networkidle'); await pg.wait_for_timeout(300)
                    key=f'{login}@{w}{r}'
                    res[key]=await pg.evaluate(JS,PREF)
                    # forced hover/active on first element of each prefix
                    cdp=await ctx.new_cdp_session(pg)
                    await cdp.send('DOM.enable'); await cdp.send('CSS.enable')
                    doc=await cdp.send('DOM.getDocument',{'depth':-1})
                    for p in PREF:
                        q=await cdp.send('DOM.querySelectorAll',{'nodeId':doc['root']['nodeId'],'selector':f'[class*="{p}"]'})
                        for ix,nid in enumerate(q['nodeIds'][:6]):
                            for st in (['hover'],['active'],['focus']):
                                await cdp.send('CSS.forcePseudoState',{'nodeId':nid,'forcedPseudoClasses':st})
                                cs=await cdp.send('CSS.getComputedStyleForNode',{'nodeId':nid})
                                res[key][f'FORCE{st[0]}|{p}|{ix}']={x['name']:x['value'] for x in cs['computedStyle']}
                            await cdp.send('CSS.forcePseudoState',{'nodeId':nid,'forcedPseudoClasses':[]})
                    print(key,len(res[key]),file=sys.stderr)
                await ctx.close()
        await b.close()
    json.dump(res,open(tag,'w'))
asyncio.run(main(sys.argv[1]))

const {chromium}=require('@playwright/test');
const AxeBuilder=require('@axe-core/playwright').default;
const fs=require('node:fs');const path=require('node:path');
(async()=>{
 const base=new URL(process.env.QA_URL||'http://127.0.0.1:3100');
 if(!['127.0.0.1','localhost'].includes(base.hostname))throw Error('Only loopback is allowed');
 const out=process.env.QA_RUN_DIR||path.resolve(__dirname,'../reports/accessibility');fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch();const page=await browser.newPage({viewport:{width:1440,height:1000}});
 await page.route('**/*',r=>['127.0.0.1','localhost'].includes(new URL(r.request().url()).hostname)?r.continue():r.abort());
 await page.goto(base.href);const id=await page.locator('#seleccion_grupo_id option').filter({hasText:/^A$/}).getAttribute('value');
 const screens=['/partidos_grupo/calendario','/grupos/'+id,'/fase_eliminatoria'];
 let failed=false;
 async function scan(i){
   const response=await page.goto(new URL(screens[i],base).href);if(response.status()>=400)throw Error('Screen inaccessible: '+screens[i]+' '+response.status());
   const result=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']).analyze();
   fs.writeFileSync(path.join(out,`axe-ACC-${String(i+1).padStart(3,'0')}.json`),JSON.stringify(result,null,2));
   await page.screenshot({path:path.join(out,`ACC-${String(i+1).padStart(3,'0')}.png`),fullPage:true});
   failed ||= result.violations.length>0;
 }
 const checks=[async function test_ACC_001(){await scan(0);},async function test_ACC_002(){await scan(1);},async function test_ACC_003(){await scan(2);}];
 for(const check of checks)await check();
 await browser.close();process.exitCode=failed?1:0;
})().catch(e=>{console.error(e);process.exitCode=2;});

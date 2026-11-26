const fs=require('node:fs');const YAML=require('../node_modules/yaml');
const path=require('node:path');
const root=path.resolve(__dirname,'../..');
const doc=YAML.parse(fs.readFileSync(path.resolve(root,'../.github/workflows/qa.yml'),'utf8'));
if(doc.permissions?.contents!=='read'||!doc.jobs?.audit?.steps?.length)throw Error('Invalid CI workflow');
if(doc.jobs.audit.defaults?.run?.['working-directory']!=='Entregables')throw Error('CI must execute from Entregables');
const design=JSON.parse(fs.readFileSync(path.join(root,'qa/data/design.json'),'utf8'));
const missing=[];
for(const c of design.cases){if(!fs.existsSync(path.join(root,c.implementacion)))missing.push(c.id+': implementation missing');}
console.log(JSON.stringify({workflow:'Valid YAML1.2; read-only contents permission',implemented:design.cases.length-missing.length,missing},null,2));
process.exitCode=missing.length?1:0;

// Reproducible cyclomatic count from the official Ruby Prism AST, not text tokens.
import {loadPrism} from '../node_modules/@ruby/prism/src/index.js';
import fs from 'node:fs';import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const appRoot=path.resolve(root,'..');
const parse=await loadPrism();
const decision=new Set(['IfNode','UnlessNode','WhileNode','UntilNode','ForNode','WhenNode','InNode','RescueNode','AndNode','OrNode']);
const iterators=new Set(['each','each_with_index','each_with_object','map','collect','select','reject','find','detect','any?','all?','none?','one?','count','sum','times','loop','find_each','each_slice']);
function children(node){return node.childNodes().filter(Boolean);}
function count(node){if(!node||node.constructor.name==='DefNode')return 0;
 const type=node.constructor.name;let n=decision.has(type)?1:0;
 if(type==='CallNode'&&node.block&&iterators.has(node.name))n++;
 if(type==='CallNode'&&(node.flags&4))n++;
 return n+children(node).reduce((sum,child)=>sum+count(child),0);}
function files(dir){return fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?files(path.join(dir,e.name)):e.name.endsWith('.rb')?[path.join(dir,e.name)]:[]);}
const rows=[],errors=[];
for(const file of files(path.join(appRoot,'app'))){
 const source=fs.readFileSync(file);const result=parse(source);
 if(result.errors.length)errors.push({file,errors:result.errors});
 function walk(node,klass=''){
  if(node.constructor.name==='ClassNode'||node.constructor.name==='ModuleNode')klass=node.constantPath?.name||klass;
  if(node.constructor.name==='DefNode')rows.push({file:path.relative(appRoot,file).replaceAll('\\','/'),class:klass,method:node.name,line:node.location.startLine(),end_line:node.location.endLine(),complexity:1+count(node.body)});
  for(const child of children(node))walk(child,klass);
 }walk(result.value);
}
if(!rows.length)throw Error('No methods parsed; invalid measurement');
const out=process.argv[2]||path.join(root,'qa/reports/complexity.json');fs.mkdirSync(path.dirname(out),{recursive:true});
fs.writeFileSync(out,JSON.stringify({tool:'Ruby Prism AST + QA cyclomatic counter v1',convention:'1 + if/unless/loops/when/in/rescue/and/or + iterator blocks + safe navigation; nested method definitions excluded',
 version:JSON.parse(fs.readFileSync(path.join(root,'qa/node_modules/@ruby/prism/package.json'))).version,
 count:rows.length,average:rows.reduce((s,r)=>s+r.complexity,0)/rows.length,max:Math.max(...rows.map(r=>r.complexity)),
 distribution:{at_most_10:rows.filter(r=>r.complexity<=10).length,from_11_to_15:rows.filter(r=>r.complexity>10&&r.complexity<=15).length,above_15:rows.filter(r=>r.complexity>15).length},methods:rows,parse_errors:errors},null,2));
console.log('Parsed',rows.length,'methods;',errors.length,'parse errors; maximum',Math.max(...rows.map(r=>r.complexity)));
process.exitCode=errors.length?2:rows.some(r=>r.complexity>15)?1:0;

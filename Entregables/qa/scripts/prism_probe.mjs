import {loadPrism} from '../node_modules/@ruby/prism/src/index.js';
import fs from 'node:fs';
import {fileURLToPath} from 'node:url';
const parse=await loadPrism();
const result=parse(fs.readFileSync(fileURLToPath(new URL('../../../app/services/calcular_ganador_partido.rb',import.meta.url))));
console.log(JSON.stringify(result.value,null,2).slice(0,7000));

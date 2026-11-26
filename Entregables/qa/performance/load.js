import http from 'k6/http';
import {check,sleep} from 'k6';
import {Trend,Rate} from 'k6/metrics';
import exec from 'k6/execution';
const base=__ENV.QA_URL||'http://127.0.0.1:3100';
if(!/^http:\/\/(127\.0\.0\.1|localhost):3100\/?$/.test(base))throw Error('QA only allows the local server on port3100');
const scenario=__ENV.QA_LOAD==='high'?'PERF-002':'PERF-001';
const levels=scenario==='PERF-002'?[25,50,100]:[5,10,20];
const latency=new Trend('qa_latency',true);const transport=new Rate('qa_transport');const unexpected=new Rate('qa_unexpected_http');const invalid=new Rate('qa_invalid_content');
const thresholds={'http_req_failed':[{threshold:'rate<0.10',abortOnFail:true,delayAbortEval:'30s'}]};
for(const vu of levels)for(const route of ['/','/partidos_grupo/calendario']){thresholds[`qa_latency{load:${vu},route:${route}}`]=['p(95)<=1000'];thresholds[`qa_invalid_content{load:${vu},route:${route}}`]=['rate<=0.01'];}
export const options={stages:[{duration:'30s',target:levels[0]},{duration:'60s',target:levels[0]},{duration:'10s',target:levels[1]},{duration:'60s',target:levels[1]},{duration:'10s',target:levels[2]},{duration:'60s',target:levels[2]},{duration:'30s',target:0}],thresholds,summaryTrendStats:['avg','med','p(90)','p(95)','p(99)','max'],tags:{scenario}};
function requestScenario(){
 const t=exec.instance.currentTestRunDuration/1000;
 const load=t>=30&&t<90?levels[0]:t>=100&&t<160?levels[1]:t>=170&&t<230?levels[2]:'transition';
 for(const route of ['/','/partidos_grupo/calendario']){
  const r=http.get(base+route,{redirects:0,tags:{load:String(load),route}});
  const ok=check(r,{'HTTP200':x=>x.status===200,'content':x=>x.body&&(/Gestion de Grupos|Calendario y resultados/).test(x.body)});
  latency.add(r.timings.duration,{load:String(load),route});transport.add(r.status===0,{load:String(load),route});
  unexpected.add(r.status!==0&&r.status!==200,{load:String(load),route});invalid.add(!ok,{load:String(load),route});
 }
 sleep(1);
}
export function test_PERF_001(){requestScenario();}
export function test_PERF_002(){requestScenario();}
export default function(){scenario==='PERF-002'?test_PERF_002():test_PERF_001();}

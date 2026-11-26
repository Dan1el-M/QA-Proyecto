"""Single runner. Preserve raw output and exit codes; continue independent jobs."""
import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

from paths import ROOT, APP_ROOT
sys.path.insert(0,str(Path(__file__).parent))


def environment():
    env=os.environ.copy()
    portable=ROOT/'.qa-runtime/rubyinstaller-4.0.5-1-x64/bin'
    if portable.exists() and (not shutil.which('ruby',path=env['PATH']) or env.get('QA_USE_PORTABLE_RUBY')=='1'):
        env['PATH']=str(portable)+os.pathsep+str(ROOT/'.qa-runtime/gems/bin')+os.pathsep+env['PATH']
        env['GEM_HOME']=str(ROOT/'.qa-runtime/gems')
    env.update(RAILS_ENV='test',RI_FORCE_PATH_FOR_DLL='1',BUNDLE_GEMFILE=str(ROOT/'qa/Gemfile'),QA_URL='http://127.0.0.1:3100',PYTHONIOENCODING='utf-8')
    return env


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--only',choices=['unit','integration','security','e2e','performance','accessibility','static'])
    parser.add_argument('--load',action='store_true')
    parser.add_argument('--no-report',action='store_true')
    args=parser.parse_args()
    stamp=datetime.now(timezone(timedelta(hours=-6))).strftime('%Y%m%dT%H%M%S%f-0600')
    run=ROOT/'qa/reports/runs'/stamp;run.mkdir(parents=True)
    env=environment();env['QA_RUN_DIR']=str(run)
    jobs=[]
    def command(name,cmd,timeout=240,extra=None,cwd=ROOT):
        start=time.monotonic();log=run/(name+'.log')
        current=env| (extra or {})
        cmd=[shutil.which(cmd[0],path=current['PATH']) or cmd[0],*cmd[1:]]
        try:
            result=subprocess.run(cmd,cwd=cwd,env=current,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=timeout)
            output=result.stdout.decode('utf-8',errors='replace');code=result.returncode
        except FileNotFoundError as e:output=str(e);code=127
        except subprocess.TimeoutExpired as e:
            output=(e.stdout or b'').decode('utf-8',errors='replace')+'\nTIMEOUT';code=124
        log.write_text(output,encoding='utf-8')
        job=dict(name=name,command=cmd,cwd=str(cwd),exit_code=code,seconds=round(time.monotonic()-start,3),log=str(log.relative_to(ROOT)),started_at=stamp)
        jobs.append(job);print(name,code,flush=True)
        return code
    def selected(name):return not args.only or args.only==name
    command('versions',[sys.executable,'qa/scripts/versions.py'])
    if selected('static'):
        command('complexity',['node','qa/scripts/complexity.mjs',str(run/'complexity.json')])
        command('duplication',['node',str(ROOT/'qa/node_modules/jscpd/bin/jscpd'),'app','--format','ruby,markup','--min-lines','5','--min-tokens','50','--reporters','json','--output',str(run/'jscpd')],cwd=APP_ROOT)
        for name,cmd in [('rubocop',['rubocop','app','--format','json','--out',str(run/'rubocop.json')]),('reek',['reek','app','--format','json']),('flay',['flay','app']),('brakeman',['brakeman','--no-threads','--no-pager','--format','json','--output',str(run/'brakeman.json')]),('bundler-audit',['bundler-audit','check','--gemfile-lock','Gemfile.lock','--format','json'])]:
            command(name,['ruby','-r',str(ROOT/'qa/scripts/stdio.rb'),'-S',*cmd],cwd=APP_ROOT)
        command('static-review',[sys.executable,'qa/scripts/static_review.py','--run',str(run)])
    for name,file in [('unit','test/unit/qa_unit_test.rb'),('integration','test/integration/qa_integration_test.rb'),('security','test/integration/qa_security_test.rb')]:
        if selected(name):
            command(name,['ruby',file],extra={'QA_RESULTS':str(run/(name+'.json')),'QA_COVERAGE':str(run/('coverage-'+name))})
    needs_server=selected('e2e') or selected('accessibility') or (selected('performance') and args.load)
    if needs_server:
        ready=command('prepare',['ruby','qa/scripts/prepare.rb','finished'])==0
        if selected('e2e'):
            command('e2e',['node','qa/node_modules/@playwright/test/cli.js','test','-c','qa/e2e/playwright.config.cjs'],timeout=600)
        if selected('accessibility') or (selected('performance') and args.load):
            # A server belongs to this run; close only that process in finally.
            server=None
            if ready:
                command('prepare-browser',['ruby','qa/scripts/prepare.rb','knockout'])
                serverlog=(run/'server.log').open('w',encoding='utf-8')
                server=subprocess.Popen([shutil.which('ruby',path=env['PATH']) or 'ruby','qa/scripts/server.rb'],cwd=ROOT,env=env,stdout=serverlog,stderr=subprocess.STDOUT)
                from urllib.request import urlopen
                for _ in range(60):
                    try:
                        with urlopen(env['QA_URL']+'/up',timeout=1) as response:
                            if response.status==200:break
                    except Exception:time.sleep(0.5)
            try:
                if selected('accessibility'):command('accessibility',['node','qa/accessibility/scan.cjs'])
                if selected('performance') and args.load:
                    for profile in ['normal','high']:
                        code=command('performance-'+profile,['k6','run','--out','json='+str(run/('k6-'+profile+'.jsonl')),'--summary-export',str(run/('k6-'+profile+'-summary.json')),'qa/performance/load.js'],timeout=420,extra={'QA_LOAD':profile})
                        if code not in [124,127]:time.sleep(30) # recovery after actual load only
            finally:
                if server:
                    server.terminate()
                    try:server.wait(timeout=10)
                    except subprocess.TimeoutExpired:server.kill()
                    serverlog.close()
    if selected('performance') and not args.load:
        jobs.append(dict(name='performance',exit_code=None,command=[],log='',reason='Use --load to activate the local maximum100VU profile'))
    report=dict(run_id=stamp,commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                os=platform.platform(),jobs=jobs)
    (run/'run.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    (ROOT/'qa/reports/latest.json').write_text(json.dumps({'path':str(run.relative_to(ROOT))}),encoding='utf-8')
    if not args.no_report:
        subprocess.run([sys.executable,'qa/scripts/finalize.py'],cwd=ROOT,env=env)
    return 1 if any(j.get('exit_code') not in [0,None] for j in jobs) else 0


if __name__=='__main__':raise SystemExit(main())

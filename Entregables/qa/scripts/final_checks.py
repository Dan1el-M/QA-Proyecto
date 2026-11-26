"""Check QA artifact syntax and frozen-design integrity without running the application."""
import compileall
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from design import ROOT


def main():
    results=[]
    results.append({'check':'Python syntax','passed':compileall.compile_dir(ROOT/'qa/scripts',quiet=1)})
    frozen=ROOT/'qa/data/design.json'
    results.append({'check':'Frozen design SHA256','passed':hashlib.sha256(frozen.read_bytes()).hexdigest()==(ROOT/'qa/data/design.sha256').read_text().strip()})
    env=os.environ.copy();env['RI_FORCE_PATH_FOR_DLL']='1'
    ruby=shutil.which('ruby') or str(ROOT/'.qa-runtime/rubyinstaller-4.0.5-1-x64/bin/ruby.exe')
    node=shutil.which('node')
    git_bash=Path('C:/Program Files/Git/bin/bash.exe')
    bash=str(git_bash) if os.name=='nt' and git_bash.is_file() else shutil.which('bash')
    jobs=[]
    for folder in ['qa','test']:
        for path in (ROOT/folder).rglob('*.rb'):
            if any(part in ['node_modules','reports'] for part in path.parts):continue
            jobs.append(('Ruby syntax: '+str(path.relative_to(ROOT)),[ruby,'--disable-gems','-r',str(ROOT/'qa/scripts/stdio.rb'),'-c',str(path)]))
    for pattern in ['*.cjs','*.mjs']:
        for path in (ROOT/'qa').rglob(pattern):
            if any(part in ['node_modules','reports'] for part in path.parts):continue
            jobs.append(('JavaScript syntax: '+str(path.relative_to(ROOT)),[node,'--check',str(path)]))
    for path in sorted((ROOT/'qa/scripts').glob('*.sh')):
        jobs.append(('Bash syntax: '+path.name,[bash,'-n',path.as_posix()]))
    for name,command in jobs:
        try:
            run=subprocess.run(command,cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=30)
            results.append({'check':name,'passed':run.returncode==0,'exit':run.returncode,'output':(run.stdout+run.stderr).strip()})
        except (OSError,subprocess.TimeoutExpired) as error:
            results.append({'check':name,'passed':False,'output':str(error)})
    output={'checked_at':datetime.now().isoformat(),'scope':'QA harness syntax and frozen design; does not credit application or human tests','results':results}
    (ROOT/'qa/reports/Final_Validation.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
    failures=[item['check'] for item in results if not item['passed']]
    print('Artifact checks:',len(results),'; failures:',failures)
    return int(bool(failures))


if __name__=='__main__':raise SystemExit(main())

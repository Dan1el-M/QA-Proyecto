import json,platform,subprocess,shutil
from pathlib import Path
result={'os':platform.platform(),'python':platform.python_version(),'cpu':platform.processor()}
for name,args in {'ruby':['ruby','-v'],'bundler':['ruby','-S','bundle','-v'],'git':['git','--version'],'node':['node','-v'],'k6':['k6','version'],'npm':['npm.cmd','-v']}.items():
    try:
        r=subprocess.run(args,capture_output=True,timeout=15)
        result[name]={'exit_code':r.returncode,'output':(r.stdout+r.stderr).decode('utf-8',errors='replace').strip()}
    except Exception as e:result[name]={'error':str(e)}
print(json.dumps(result,indent=2,ensure_ascii=True))

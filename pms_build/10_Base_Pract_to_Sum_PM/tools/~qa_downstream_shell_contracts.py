#!/usr/bin/env python3
from pathlib import Path
import subprocess, sys
bundle=Path(__file__).resolve().parents[1]
stage=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
checks=[
 bundle/'family_pms/Base_Activities_PM/tools/~qa_activity_shell_contracts.py',
 bundle/'family_pms/Base_Recurring_Assessment_PM/tools/~qa_recurring_shell_contracts.py',
]
failed=0
for tool in checks:
    print(f'RUN {tool.name}')
    r=subprocess.run([sys.executable,str(tool),str(stage)])
    failed |= (r.returncode!=0)
print('DOWNSTREAM_SHELL_CONTRACTS=' + ('FAIL' if failed else 'PASS'))
sys.exit(1 if failed else 0)

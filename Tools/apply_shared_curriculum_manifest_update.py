#!/usr/bin/env python3
"""Non-destructively register approved shared-curriculum amendments in the local manifest.

Run once after the accompanying Curriculum Transfer files are installed.
No Git actions, resource migration, deletions, or application changes.
"""
from __future__ import annotations
import json
import os
import shutil
import stat
import tempfile
import time
from pathlib import Path

MEMORIES = Path(__file__).resolve().parent.parent
TARGET = MEMORIES / 'SYSTEM_MANIFEST.json'
REGISTRATIONS = {
    'philosophy_amendments': 'Curriculum_Philosophy_Shared_Curriculum_And_Teacher_Workspaces_Amendment.txt',
    'runtime_amendments': 'SYSTEM_RUNTIME_SHARED_RESOURCE_DISTRIBUTION_AMENDMENT.txt',
}

def main():
    if not TARGET.is_file():
        raise RuntimeError('Missing SYSTEM_MANIFEST.json; nothing changed.')
    for name in REGISTRATIONS.values():
        if not (MEMORIES/name).is_file():
            raise RuntimeError('Required new amendment not installed: '+name)
    original = TARGET.read_bytes()
    try:
        data = json.loads(original.decode('utf-8'))
    except (UnicodeError, json.JSONDecodeError) as e:
        raise RuntimeError('Cannot parse SYSTEM_MANIFEST.json; nothing changed: '+str(e))
    if not isinstance(data, dict):
        raise RuntimeError('SYSTEM_MANIFEST.json must be a JSON object; nothing changed.')
    changed=[]
    for key,value in REGISTRATIONS.items():
        existing=data.get(key)
        if not isinstance(existing,list) or any(not isinstance(s,str) for s in existing):
            raise RuntimeError(f'Expected {key} to be a list of strings; nothing changed.')
        if value not in existing:
            existing.append(value)
            changed.append(value)
    if not changed:
        print('SUCCESS: Both amendments are already registered. No changes required.')
        return
    backup_dir=MEMORIES.parent / '_curriculum_transfers' / '_backups' / 'manual_manifest_registration'
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp=time.strftime('%Y%m%d_%H%M%S')
    backup=backup_dir / f'SYSTEM_MANIFEST_before_shared_curriculum_{timestamp}.json'
    counter=1
    while backup.exists():
        counter+=1
        backup=backup_dir / f'SYSTEM_MANIFEST_before_shared_curriculum_{timestamp}_{counter}.json'
    backup.write_bytes(original)
    mode=stat.S_IMODE(TARGET.stat().st_mode)
    new_bytes=(json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    tmp_name=None
    try:
        fd,tmp_name=tempfile.mkstemp(prefix='.SYSTEM_MANIFEST.safe-',suffix='.tmp',dir=MEMORIES)
        with os.fdopen(fd,'wb') as out:
            out.write(new_bytes)
            out.flush()
            os.fsync(out.fileno())
        os.chmod(tmp_name,mode)
        os.replace(tmp_name,TARGET)
        tmp_name=None
        verified=json.loads(TARGET.read_text(encoding='utf-8'))
        if any(value not in verified[key] for key,value in REGISTRATIONS.items()):
            TARGET.write_bytes(original)
            raise RuntimeError('Post-save verification failed. Original manifest restored.')
    finally:
        if tmp_name and os.path.exists(tmp_name):
            os.unlink(tmp_name)
    print('SUCCESS: Registered '+str(len(changed))+' new amendment(s).')
    for name in changed:
        print('  '+name)
    print('Preserved every existing manifest entry and other setting.')
    print('Backup:',backup)
    print('No Git commit or push was run.')

if __name__=='__main__':
    try:
        main()
    except Exception as exc:
        print('FAILURE:',exc)
        raise SystemExit(1)

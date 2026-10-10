#!/usr/bin/env python3
from pathlib import Path
import sys
f=Path(sys.argv[1])/'app/build.gradle.kts'
s=f.read_text(encoding='utf-8')
for before,after in [('versionCode = 50','versionCode = 51'),('versionName = "1.13.9"','versionName = "1.13.10"')]:
    assert s.count(before)==1, 'Build base changed: '+before
    s=s.replace(before,after,1)
f.write_text(s,encoding='utf-8')
print('PASSOU: BEAT flow 1.13.10 — atualização somente dos metadados')

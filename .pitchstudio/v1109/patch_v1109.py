#!/usr/bin/env python3
"""v1.10.9 — primeiro build autônomo do PitchStudio (sem dependência Brother Matrizes)."""
from pathlib import Path
import sys
root=Path(sys.argv[1])
gradle=root/"app/build.gradle.kts"
s=gradle.read_text(encoding="utf-8")
for old in ("versionCode = 28", 'versionName = "1.10.8"', 'applicationIdSuffix = ".vocalqa"'):
    if s.count(old)!=1: raise SystemExit(f"Versão-base do PitchStudio inesperada: {old}")
s=s.replace("versionCode = 28","versionCode = 29",1)
s=s.replace('versionName = "1.10.8"','versionName = "1.10.9"',1)
s=s.replace('applicationIdSuffix = ".vocalqa"','applicationIdSuffix = ".standaloneqa"',1)
gradle.write_text(s,encoding="utf-8")
# As atividades, os recursos de áudio e os modelos não foram alterados.
assert (root/"app/src/main/java/br/com/timachado/pitchstudio/VocalStemSeparator.kt").is_file()
assert (root/"app/src/main/java/br/com/timachado/pitchstudio/YouTubeBrowserActivity.kt").is_file()
assert (root/"app/src/main/java/br/com/timachado/pitchstudio/audio/Mp3Exporter.kt").is_file()
print("PitchStudio 1.10.9 — projeto Android independente compilável.")

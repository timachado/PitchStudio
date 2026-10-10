#!/usr/bin/env python3
"""BEAT flow v1.12.1 — waveform real + refinamento de acessibilidade/estados."""
from pathlib import Path
import sys
root=Path(sys.argv[1])
base=Path(__file__).resolve().parent
pkg=root/"app/src/main/java/br/com/timachado/pitchstudio"
for name in ("BeatStemActivity.kt","BeatWaveformView.kt"):
    data=(base/name).read_text(encoding="utf-8")
    assert "package br.com.timachado.pitchstudio" in data
    (pkg/name).write_text(data,encoding="utf-8")
gradle=root/"app/build.gradle.kts"
s=gradle.read_text(encoding="utf-8")
for old in ("versionCode = 31",'versionName = "1.12.0"','applicationIdSuffix = ".playbackqa"'):
    assert s.count(old)==1,old
s=s.replace("versionCode = 31","versionCode = 32",1)
s=s.replace('versionName = "1.12.0"','versionName = "1.12.1"',1)
s=s.replace('applicationIdSuffix = ".playbackqa"','applicationIdSuffix = ".waveqa"',1)
gradle.write_text(s,encoding="utf-8")
print("BEAT flow v1.12.1: áudio intacto, waveform verdadeiro + Material 3 Expressive.")

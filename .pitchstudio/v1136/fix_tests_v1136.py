#!/usr/bin/env python3
"""Kotlin/JUnit Java overload compatibility for the v1.13.6 unit test."""
from pathlib import Path
import sys
f=Path(sys.argv[1])/"app/src/test/java/br/com/timachado/pitchstudio/StageTempoAnalyzerTest.kt"
s=f.read_text(encoding="utf-8")
old="assertEquals(bpm,estimate!!.bpm,3)"
new="assertTrue(kotlin.math.abs(estimate!!.bpm-bpm)<=3)"
assert s.count(old)==1
f.write_text(s.replace(old,new,1),encoding="utf-8")
print("PASSOU: JUnit usa tolerância inteira explícita para BPM.")

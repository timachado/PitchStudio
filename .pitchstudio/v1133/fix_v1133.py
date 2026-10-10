#!/usr/bin/env python3
"""1.13.3 QA correction: Kotlin 2.2 temp dir API + marker at 0:00."""
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
source=root/"app/src/main/java/br/com/timachado/pitchstudio/SectionDspRenderer.kt"
unit=root/"app/src/test/java/br/com/timachado/pitchstudio/SectionDspRendererTest.kt"
s=source.read_text(encoding="utf-8")
old="val bounds = (listOf(0L) + normalized.map {"
new="val bounds = (listOf(0L) + normalized.filter { it.fraction > 0.0 }.map {"
assert s.count(old)==1,"Unexpected SectionDspRenderer source"
source.write_text(s.replace(old,new,1),encoding="utf-8")
t=unit.read_text(encoding="utf-8")
old='createTempDir(prefix="sections")'
assert t.count(old)==2,"Unexpected unit test content"
unit.write_text(t.replace(old,'java.nio.file.Files.createTempDirectory("sections").toFile()'),encoding="utf-8")
print("BEAT flow 1.13.3: Kotlin 2.2 tests and 0:00 marker fixed.")

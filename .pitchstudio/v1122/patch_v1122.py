#!/usr/bin/env python3
"""BEAT flow v1.12.2 — navegação real no playback, tempo e estados do player."""
from pathlib import Path
import sys

root=Path(sys.argv[1])
base=Path(__file__).resolve().parent
pkg=root/"app/src/main/java/br/com/timachado/pitchstudio"
activity=(base/"BeatStemActivity.kt").read_text(encoding="utf-8")
for required in ("SeekBar(this)", "player.seekFraction(", "timelineHandler.removeCallbacks("):
    assert required in activity, required
player=(pkg/"audio/PcmAudioPlayer.kt").read_text(encoding="utf-8")
assert "fun seekFraction(" in player and "fun fraction()" in player
(pkg/"BeatStemActivity.kt").write_text(activity,encoding="utf-8")
gradle=root/"app/build.gradle.kts"
s=gradle.read_text(encoding="utf-8")
for before,after in (("versionCode = 32","versionCode = 33"),
                     ('versionName = "1.12.1"','versionName = "1.12.2"')):
    assert s.count(before)==1,before
    s=s.replace(before,after,1)
gradle.write_text(s,encoding="utf-8")
print("BEAT flow 1.12.2: seek + tempo decorrido; motor de IA intacto.")

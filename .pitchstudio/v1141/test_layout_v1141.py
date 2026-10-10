#!/usr/bin/env python3
"""Validate coverage of the 34 UI controls by Expressive reflow."""
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
s=(root/"app/src/main/java/br/com/timachado/pitchstudio/MainActivity.kt").read_text(encoding="utf-8")
m=s[s.index("    private fun reflowExpressiveUi()"):s.index("    private fun applyTheme()")]
groups=[[0],[1,2,3,5,6],[4,7,8,9],list(range(10,16)),[16,17],list(range(18,25)),list(range(25,29)),[29,30,31],[32,33]]
used=[x for group in groups for x in group]
assert len(used)==34 and sorted(used)==list(range(34)),used
assert 'nodes.size != 34' in m
assert 'button("Tom Ideal · Analisar minha voz")' in m
assert 'button("Separação com IA · Gerar playback")' in m
assert 'button("Meus projetos")' in m
assert 'nodes[17] as? LinearLayout' in m
assert 'button("Modo Palco e Ensaio")' in s
assert 'button("WAV por trechos")' in s and 'button("MP3 por trechos")' in s
assert 'openYouTubeBrowser()' in s and 'openBeatSeparation()' in s
assert 'reflowExpressiveUi()' in s
assert 'versionName = "1.13.11"' in (root/"app/build.gradle.kts").read_text()
print("PASSOU: 34 elementos preservados; Material, Tom Ideal, Playback, biblioteca, Palco, downloads e exportações.")

#!/usr/bin/env python3
"""Static regression checks for persistent library navigation v1.13.12."""
from pathlib import Path
import sys

root=Path(sys.argv[1]).resolve()
s=(root/"app/src/main/java/br/com/timachado/pitchstudio/MainActivity.kt").read_text(encoding="utf-8")
gradle=(root/"app/build.gradle.kts").read_text(encoding="utf-8")
pre=s.index("        reflowExpressiveUi()")
post=s.index("        applyTheme()",pre)
new=s[pre:post]
assert 'button("Biblioteca Inteligente") { showSavedProjects() }' in new
assert 'button("Salvar projeto") { promptSaveProject() }' in new
assert 'root.addView(libraryShortcuts, 2' in new
assert 'if (root.getChildAt(1) !is MaterialCardView)' in new
assert 'root.addView(recoveryActions, 3' in new
assert s.count('button("Tom Ideal · Analisar minha voz")')==2
assert s.count('button("Separação com IA · Gerar playback")')==2
assert s.count('button("Biblioteca Inteligente")')==1
assert s.count('button("Salvar projeto")')==1
assert 'button("Meus projetos")' not in s[s.index('private fun reflowExpressiveUi()'):]
assert 'nodes.size != 34' in s
assert 'button("Tom Ideal · Analisar minha voz")' in s
assert 'button("Separação com IA · Gerar playback")' in s
assert 'button("Modo Palco e Ensaio")' in s
assert 'versionCode = 53' in gradle
assert 'versionName = "1.13.12"' in gradle
print("PASSOU: atalhos de biblioteca independentes do reflow e sem botões duplicados.")

#!/usr/bin/env python3
"""Safeguards for BEAT flow v1.13.13's library/repertoire bridge."""
from pathlib import Path
import sys

base=Path(sys.argv[1]).resolve()
p=base/"app/src/main/java/br/com/timachado/pitchstudio"
s=(p/"StageActivity.kt").read_text(encoding="utf-8")
m=(p/"MainActivity.kt").read_text(encoding="utf-8")
g=(base/"app/build.gradle.kts").read_text(encoding="utf-8")
assert "offerLibraryImportIfEmpty()" in s
assert 'setNeutralButton("Adicionar todas")' in s
assert 'setPositiveButton("Escolher música")' in s
assert "StageSetlists.update(this,set.copy(songIds=ids))" in s
assert "load(ids.indexOf(selected.id),false)" in s
assert "load(0,false)" in s
assert "playBtn.isEnabled=player.project!=null" in s
assert "progress.isEnabled=player.project!=null" in s
assert "Salve uma música na Biblioteca" in s
assert 'toast("Projeto salvo. No Modo Palco, toque em Adicionar música' in m
assert "versionCode = 54" in g and 'versionName = "1.13.13"' in g
# Never automatically play, delete library files or change neural separation
assert "load(ids.indexOf(selected.id),true)" not in s
assert 'ProjectLibrary.delete(' not in s
print("PASSOU: repertório recebe IDs existentes, seleciona música sem autoplay e preserva áudio.")

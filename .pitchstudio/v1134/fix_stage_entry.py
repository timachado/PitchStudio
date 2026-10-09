#!/usr/bin/env python3
"""v1.13.4 QA: keep Stage quick access near top of editor, no duplicated button."""
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
main=root/'app/src/main/java/br/com/timachado/pitchstudio/MainActivity.kt'
s=main.read_text(encoding='utf-8')
late='''                column.addView(button("Modo Palco e Ensaio") {
                    player.pause()
                    refreshPlayButton()
                    startActivity(Intent(this, StageActivity::class.java))
                }, full(dp(54), top = 9))'''
assert s.count(late)==1, 'Stage button not uniquely located'
s=s.replace(late,'',1)
anchor='''        root.addView(text("Seu som. No seu ritmo.  •  by T.I. Machado", 13f, false))'''
quick='''
        // O acesso ao Palco deve ficar visível sem percorrer todo o editor.
        root.addView(button("Modo Palco e Ensaio") {
            player.pause()
            refreshPlayButton()
            startActivity(Intent(this, StageActivity::class.java))
        }, full(dp(52), top = 10))'''
assert s.count(anchor)==1
s=s.replace(anchor,anchor+quick,1)
assert s.count('button("Modo Palco e Ensaio")')==1
main.write_text(s,encoding='utf-8')
print('v1.13.4: stage shortcut moved next to main header')

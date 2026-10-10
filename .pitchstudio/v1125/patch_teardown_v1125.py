#!/usr/bin/env python3
"""Preserva a posição do projeto antes de liberar o AudioTrack."""
from pathlib import Path
import sys
main=Path(sys.argv[1])/"app/src/main/java/br/com/timachado/pitchstudio/MainActivity.kt"
s=main.read_text(encoding="utf-8")
a="""    override fun onDestroy() {
        super.onDestroy()
        handler.removeCallbacksAndMessages(null)
        player.release()
        executor.shutdownNow()
        cleanupProjects()
    }"""
b="""    override fun onDestroy() {
        super.onDestroy()
        handler.removeCallbacksAndMessages(null)
        // Preservar a fração antes de release() zerar o player.
        player.pause()
        executor.shutdownNow()
        cleanupProjects()
        player.release()
    }"""
assert s.count(a)==1, "v1.12.5: onDestroy mudou"
s=s.replace(a,b,1)
assert "flushLibraryAutosave()" in s
main.write_text(s,encoding="utf-8")
print("BEAT flow: posição preservada no encerramento.")

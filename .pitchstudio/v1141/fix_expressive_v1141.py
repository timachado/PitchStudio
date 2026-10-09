#!/usr/bin/env python3
"""Restore Material 3 Expressive after two new controls expanded 32 children to 34."""
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
p=root/"app/src/main/java/br/com/timachado/pitchstudio/MainActivity.kt"
gfile=root/"app/build.gradle.kts"
s=p.read_text(encoding="utf-8")
def replace(old,new):
    global s
    assert s.count(old)==1, f"Unexpected MainActivity layout ({s.count(old)}): {old[:90]}"
    s=s.replace(old,new,1)
replace('''        // O layout base tem 32 blocos; não reorganizar se outra versão divergir.
        if (nodes.size != 32) return''','''        // Preservar os 32 elementos antigos, além do Palco (2) e da
        // exportação por trechos (31). A guarda antiga ocultava Tom Ideal.
        if (nodes.size != 34 ||
            (nodes[2] as? MaterialButton)?.text?.toString() != "Modo Palco e Ensaio" ||
            nodes[31] !is LinearLayout) {
            android.util.Log.e("BEATflow", "Estrutura Expressive inesperada: " + nodes.size)
            return
        }''')
replace('''        group(listOf(1,2,4,5),"COMECE POR AQUI","Transforme cada nota.","hero")
        group(listOf(3,6,7,8),"AGORA NO ESTÚDIO","Ouça suas alterações")
        group((9..14).toList(),"TRANSFORMAÇÃO")
        val presetRow=nodes[16] as? LinearLayout''','''        // Mapeamento sem duplicar ou perder nenhum dos 34 controles.
        group(listOf(1,2,3,5,6),"COMECE POR AQUI","Transforme cada nota.","hero")
        group(listOf(4,7,8,9),"AGORA NO ESTÚDIO","Ouça suas alterações")
        group((10..15).toList(),"TRANSFORMAÇÃO")
        val presetRow=nodes[17] as? LinearLayout''')
replace('''        group(listOf(15,16),"ATALHOS MUSICAIS")
        group((17..23).toList(),"CONTROLES DE ÁUDIO")
        group((24..27).toList(),"FERRAMENTAS")
        group(listOf(28,29),"FINALIZAR","Sua música pronta para usar.","hero")
        for(i in 30..31) root.addView(nodes[i],full(nodes[i].layoutParams?.height?:wrap(),top=9))''','''        group(listOf(16,17),"ATALHOS MUSICAIS")
        group((18..24).toList(),"CONTROLES DE ÁUDIO")
        group((25..28).toList(),"FERRAMENTAS")
        group(listOf(29,30,31),"FINALIZAR","Sua música pronta para usar.","hero")
        for(i in 32..33) root.addView(nodes[i],full(nodes[i].layoutParams?.height?:wrap(),top=9))''')
p.write_text(s,encoding="utf-8")
g=gfile.read_text(encoding="utf-8")
for old,new in [('versionCode = 51','versionCode = 52'),('versionName = "1.13.10"','versionName = "1.13.11"')]:
    assert g.count(old)==1, "Version changed: "+old
    g=g.replace(old,new,1)
gfile.write_text(g,encoding="utf-8")
print("PASSOU: Material Expressive com 34 elementos, Tom Ideal e Palco preservados")

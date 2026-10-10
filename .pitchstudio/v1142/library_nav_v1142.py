#!/usr/bin/env python3
"""BEAT flow 1.13.12: always expose the local project library.

The Material Expressive reflow is intentionally optional. Navigation and
save actions must not be created only inside the reflow branch because the
fallback layout would otherwise hide the entire project library.
"""
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
main = root / "app/src/main/java/br/com/timachado/pitchstudio/MainActivity.kt"
gradle = root / "app/build.gradle.kts"
s = main.read_text(encoding="utf-8")

def replace_once(before, after):
    global s
    assert s.count(before) == 1, f"Unexpected MainActivity structure: {before[:95]!r}"
    s = s.replace(before, after, 1)

replace_once('''        reflowExpressiveUi()
        applyTheme()''', '''        reflowExpressiveUi()
        // Sempre acessível, inclusive quando reflowExpressiveUi retorna sem
        // agrupar os cards. Não duplicar áudio nem limpar arquivos existentes.
        // A ação apenas abre o repositório privado de projetos já existente.
        val libraryShortcuts = row()
        libraryShortcuts.addView(button("Biblioteca Inteligente") { showSavedProjects() },
            LinearLayout.LayoutParams(0, dp(54), 1f).apply { marginEnd = dp(4) })
        libraryShortcuts.addView(button("Salvar projeto") { promptSaveProject() },
            LinearLayout.LayoutParams(0, dp(54), 1f).apply { marginStart = dp(4) })
        // Na tela Expressive vem logo após o card inicial; no fallback, abaixo
        // do subtítulo e acima de Modo Palco. Sem depender de 34 nós válidos.
        root.addView(libraryShortcuts, 2, full(wrap(), top = 10))
        // Se a proteção estrutural do Expressive rejeitar a reorganização,
        // manter também Tom Ideal e Separação IA acessíveis no layout básico.
        if (root.getChildAt(1) !is MaterialCardView) {
            val recoveryActions = LinearLayout(this).apply {
                orientation = LinearLayout.VERTICAL
            }
            recoveryActions.addView(
                button("Tom Ideal · Analisar minha voz") { openTomIdeal() },
                full(dp(52), top = 4))
            recoveryActions.addView(
                button("Separação com IA · Gerar playback") { openBeatSeparation() },
                full(dp(52), top = 6))
            root.addView(recoveryActions, 3, full(wrap(), top = 6))
        }
        applyTheme()''')

replace_once('''            if (kicker == "COMECE POR AQUI") {
                val actions = row()
                actions.addView(button("Salvar projeto") { promptSaveProject() },
                    LinearLayout.LayoutParams(0, dp(52), 1f).apply { marginEnd = dp(4) })
                actions.addView(button("Meus projetos") { showSavedProjects() },
                    LinearLayout.LayoutParams(0, dp(52), 1f).apply { marginStart = dp(4) })
                column.addView(actions, full(wrap(), top = 12))
                column.addView(''', '''            if (kicker == "COMECE POR AQUI") {
                // Atalhos da biblioteca ficam permanentemente na raiz, para
                // não desaparecerem em caso de fallback do layout Expressive.
                column.addView(''')

main.write_text(s, encoding="utf-8")
g = gradle.read_text(encoding="utf-8")
for before, after in [
    ('versionCode = 52', 'versionCode = 53'),
    ('versionName = "1.13.11"', 'versionName = "1.13.12"'),
]:
    assert g.count(before) == 1, f"Unexpected version: {before}"
    g = g.replace(before, after, 1)
gradle.write_text(g, encoding="utf-8")
print("PASSOU: Biblioteca Inteligente sempre visível (Expressive e fallback), v1.13.12.")

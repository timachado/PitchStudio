#!/usr/bin/env python3
"""BEAT flow 1.11.0: identidade visual/nominal; áudio, IA e player permanecem intactos."""
from pathlib import Path
import sys

root = Path(sys.argv[1])
java = root / "app/src/main/java/br/com/timachado/pitchstudio"
res = root / "app/src/main/res"

def read(path):
    if not path.is_file():
        raise SystemExit(f"Recurso não encontrado: {path}")
    return path.read_text(encoding="utf-8")

def change(path, old, new):
    content = read(path)
    count = content.count(old)
    if count != 1:
        raise SystemExit(f"BEAT flow: marcador precisa ocorrer 1x; encontrado {count}: {path.name}: {old[:100]}")
    path.write_text(content.replace(old, new, 1), encoding="utf-8")

def change_present(path, old, new):
    content = read(path)
    if old not in content:
        raise SystemExit(f"BEAT flow: sem marcador {path}: {old}")
    path.write_text(content.replace(old, new), encoding="utf-8")

gradle = root / "app/build.gradle.kts"
change(gradle, '        applicationId = "br.com.timachado.pitchstudio"',
       '        applicationId = "br.com.timachado.beatflow"')
change(gradle, 'versionCode = 29', 'versionCode = 30')
change(gradle, 'versionName = "1.10.9"', 'versionName = "1.11.0"')
change(gradle, 'applicationIdSuffix = ".standaloneqa"', 'applicationIdSuffix = ".brandqa"')
# O namespace Kotlin permanece igual; só o ID Android de instalação muda.

manifest = root / "app/src/main/AndroidManifest.xml"
change(manifest, 'android:label="Pitch Studio"', 'android:label="@string/app_name"')

strings = res / "values/strings.xml"
change(strings, '<string name="app_name">Pitch Studio</string>',
       '<string name="app_name">BEAT flow</string>\n'
       '    <string name="brand_tagline">Seu som. No seu ritmo.</string>')

home = java / "MainActivity.kt"
change(home, 'text("Pitch Studio", 26f, true)', 'text("BEAT flow", 26f, true)')
change(home, '"T.I. Machado • processamento local no aparelho"',
       '"Seu som. No seu ritmo.  •  by T.I. Machado"')
change(home, 'heading?.apply { text = "PitchStudio";',
       'heading?.apply { text = "BEAT flow";')
change(home, 'contentDescription = "Marca de onda sonora PitchStudio"',
       'contentDescription = "Símbolo BEAT flow, batida musical em forma de b"')
change_present(home, 'para o Pitch Studio', 'para o BEAT flow')
change_present(home, '→ Pitch Studio.', '→ BEAT flow.')
change_present(home, 'no Pitch Studio…', 'no BEAT flow…')

# Ajustar cores do Material 3 Expressive sem alterar hierarquia dos controles.
change(home, 'Color.rgb(43,219,230) else Color.rgb(8,120,158)',
       'Color.rgb(200,255,112) else Color.rgb(119,48,148)')
change(home, 'Color.rgb(7,13,25) else Color.rgb(247,249,253)',
       'Color.rgb(13,16,32) else Color.rgb(248,249,253)')
change(home, 'Color.rgb(18,28,47) else Color.WHITE',
       'Color.rgb(25,28,50) else Color.WHITE')
change(home, 'Color.rgb(35,39,72) else Color.rgb(229,232,255)',
       'Color.rgb(40,34,76) else Color.rgb(236,231,254)')

change_present(java / "YouTubeUi.kt", "no Pitch Studio", "no BEAT flow")
browser = java / "YouTubeBrowserActivity.kt"
change_present(browser, "Usar no PitchStudio", "Usar no BEAT flow")
change_present(browser, "para o PitchStudio", "para o BEAT flow")
change_present(browser, "no Pitch Studio", "no BEAT flow")
change_present(java / "YouTubeImporter.kt", "o Pitch Studio", "o BEAT flow")
change_present(java / "OnlineMusic.kt", "O Pitch Studio", "O BEAT flow")
change_present(java / "OnlineMusic.kt", "do Pitch Studio", "do BEAT flow")
change(java / "TomIdealActivity.kt", '"PitchStudio_Voz_Isolada.wav"',
       '"BEATflow_Voz_Isolada.wav"')

notice = root / "app/src/main/assets/MDX_MODEL_NOTICE.txt"
change_present(notice, "PitchStudio", "BEAT flow")

# Logo exclusivo desta prévia: letra b em pulso sonoro. Vetor nativo adaptável.
icon = res / "drawable/ic_pitchstudio_mark.xml"
if not icon.exists():
    raise SystemExit("BEAT flow: vetor de ícone base ausente")
icon.write_text("""<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <!-- Haste da nota + ciclo contínuo formando b -->
    <path android:pathData="M34,24 L34,82"
        android:strokeColor="#C8FF70"
        android:strokeWidth="10"
        android:strokeLineCap="round"
        android:fillColor="@android:color/transparent"/>
    <path android:pathData="M35,49 C44,38 66,40 74,54 C84,73 63,86 47,78 C42,76 38,72 35,69"
        android:strokeColor="#C8FF70"
        android:strokeWidth="10"
        android:strokeLineCap="round"
        android:strokeLineJoin="round"
        android:fillColor="@android:color/transparent"/>
    <!-- Movimento / beat: duas ondas sem reprodução da marca de terceiros -->
    <path android:pathData="M68,20 C77,24 85,31 89,41"
        android:strokeColor="#FF628B"
        android:strokeWidth="6"
        android:strokeLineCap="round"
        android:fillColor="@android:color/transparent"/>
    <path android:pathData="M79,16 C87,19 94,25 98,33"
        android:strokeColor="#C4B3FF"
        android:strokeWidth="4"
        android:strokeLineCap="round"
        android:fillColor="@android:color/transparent"/>
</vector>
""", encoding="utf-8")

change(res / "values/pitchstudio_icon_colors.xml",
       '#08111D', '#0D1020')
theme = res / "values/pitchstudio_expressive_theme.xml"
for old, new in (
    ("#2BDBE6", "#C8FF70"),
    ("#07131C", "#0D1020"),
    ("#A7B9F4", "#C4B3FF"),
    ("#A58EFF", "#FF628B"),
    ("#121C2F", "#191C32")
):
    change(theme, old, new)

# Nem pacote Kotlin nem nomes de threads/arquivos já salvos são reescritos:
# evita quebra de projetos e interoperabilidade.
assert "namespace = \"br.com.timachado.pitchstudio\"" in read(gradle)
assert "fun isolateVocalExcerpt()" in read(java / "TomIdealActivity.kt")
assert "VocalChunkPlan" in read(java / "VocalStemSeparator.kt")
assert "YouTubeUrlRules" in read(java / "YouTubeImporter.kt")
print("BEAT flow 1.11.0: launcher, capa, textos e Material 3 Expressive atualizados.")

#!/usr/bin/env python3
"""BEAT flow v1.12.0 — opção Voz/Playback/Ambos e música inteira (streaming)."""
from pathlib import Path
import sys
root=Path(sys.argv[1])
src=Path(__file__).resolve().parent
pkg=root/"app/src/main/java/br/com/timachado/pitchstudio"
def once(path,old,new):
    content=path.read_text(encoding="utf-8")
    n=content.count(old)
    if n!=1:raise RuntimeError(f"Marcador {n}x em {path.name}: {old[:95]}")
    path.write_text(content.replace(old,new,1),encoding="utf-8")

engine=pkg/"VocalStemSeparator.kt"
new_method=(src/"separate-stems-method.txt").read_text(encoding="utf-8")
assert "fun separateStems(" in new_method
once(engine,'    private fun cacheModel(context: Context): File {',
     new_method+'\n    private fun cacheModel(context: Context): File {')
once(engine,'import kotlin.math.roundToInt','import kotlin.math.roundToInt\nimport kotlin.math.roundToLong')

new_ui=src/"BeatStemActivity.kt"
assert new_ui.is_file()
(pkg/"BeatStemActivity.kt").write_text(new_ui.read_text(encoding="utf-8"),encoding="utf-8")

manifest=root/"app/src/main/AndroidManifest.xml"
once(manifest,'        <activity android:name=".TomIdealActivity" android:exported="false" />',
     '        <activity android:name=".TomIdealActivity" android:exported="false" />\n'
     '        <activity android:name=".BeatStemActivity" android:exported="false" />')

main=pkg/"MainActivity.kt"
once(main,'    private fun openTomIdeal() {',r'''    /** Abre a separação apenas sobre áudio original/local validado. */
    private fun openBeatSeparation() {
        player.pause()
        refreshPlayButton()
        val source = original
        if (source == null) {
            statusLabel.text = "Importe uma música do aparelho antes de gerar playback."
            return
        }
        val intent = Intent(this, BeatStemActivity::class.java).apply {
            putExtra(BeatStemActivity.FILE, source.pcmFile.absolutePath)
            putExtra(BeatStemActivity.RATE, source.sampleRate)
            putExtra(BeatStemActivity.CHANNELS, source.channels)
            putExtra(BeatStemActivity.FRAMES, source.frames)
            putExtra(BeatStemActivity.FRACTION, player.fraction())
            putExtra(BeatStemActivity.NAME, source.name)
        }
        startActivity(intent)
    }

    private fun openTomIdeal() {''')
once(main,
     '                    button("Tom Ideal · Analisar minha voz") { openTomIdeal() },\n                    full(dp(52), top = 8)\n                )',
     '                    button("Tom Ideal · Analisar minha voz") { openTomIdeal() },\n                    full(dp(52), top = 8)\n                )\n'
     '                column.addView(button("Separação com IA · Gerar playback") '
     '{ openBeatSeparation() }, full(dp(54), top = 9))')
# WAV em arquivo inteiro. A regra RIFF PCM16 continua limitada a cerca de 2GiB
# por verificação exata de sampleCount no exporter.
exporter=pkg/"StemWavExporter.kt"
once(exporter,'const val MAX_FRAMES = 44100L * 120L',
     'const val MAX_FRAMES = 44100L * 60L * 60L')
gradle=root/"app/build.gradle.kts"
for old,new in [
    ("versionCode = 30","versionCode = 31"),
    ('versionName = "1.11.0"','versionName = "1.12.0"'),
    ('applicationIdSuffix = ".brandqa"','applicationIdSuffix = ".playbackqa"')
]:once(gradle,old,new)
print("BEAT flow 1.12.0: streaming vocal/playback, UI e WAV de música inteira integrados.")

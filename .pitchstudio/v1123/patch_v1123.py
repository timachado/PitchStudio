#!/usr/bin/env python3
"""BEAT flow 1.12.3: prévia das três tonalidades do Tom Ideal.
Áudio local, sem alterar o original nem a integração YouTube.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
pkg=root/"app/src/main/java/br/com/timachado/pitchstudio"
activity=pkg/"TomIdealActivity.kt"
s=activity.read_text(encoding="utf-8")
def once(a,b):
 global s
 n=s.count(a)
 if n!=1: raise SystemExit(f"v1.12.3: marcador incompatível ({n}): {a[:70]!r}")
 s=s.replace(a,b,1)
once("import android.os.SystemClock","import android.os.SystemClock\nimport android.os.Handler\nimport android.os.Looper\nimport kotlin.math.pow")
once("    private var fixedChoiceChildren = 3",'''    private var fixedChoiceChildren = 3
    // Prévia não destrutiva da música local em qualquer uma das tonalidades.
    private var toneSource: AudioProject? = null
    private val tonePlayer = PcmAudioPlayer()
    private val toneUi = Handler(Looper.getMainLooper())
    private var toneTimeout: Runnable? = null
    private var toneButton: MaterialButton? = null
    private var toneButtonLabel: String? = null''')
once('''    private fun analyzeLoadedSong() {
        if (::isolatedPreviewButton.isInitialized) clearIsolatedPreview()''','''    private fun analyzeLoadedSong() {
        stopTonePreview()
        toneSource = null
        if (::isolatedPreviewButton.isInitialized) clearIsolatedPreview()''')
once('''        phraseReading = true
        trackStatus.text = "Analisando um trecho da música localmente…"
        Thread({
            try {
                val source = AudioProject("Trecho analisado",file,rate,channels,frames,0f,
                    floatArrayOf(0f))
                val found = SongPhraseAnalyzer.analyze(source, fraction)''','''        phraseReading = true
        trackStatus.text = "Analisando um trecho da música localmente…"
        val source = AudioProject("Trecho analisado",file,rate,channels,frames,0f,
            floatArrayOf(0f))
        toneSource = source
        Thread({
            try {
                val found = SongPhraseAnalyzer.analyze(source, fraction)''')
once('''    private fun showOptions(profile: VoicePitchAnalyzer.Profile?) {
        if (profile != null)''','''    private fun showOptions(profile: VoicePitchAnalyzer.Profile?) {
        stopTonePreview()
        if (profile != null)''')
once('''                add(choices, button(named, index == 0) { choose(shift) },8)
            }
        } else {''','''                add(choices, button(named, index == 0) { choose(shift) },8)
                addTonePreviewOption(shift)
            }
        } else {''')
once('''                add(choices, button(name + " · " + (if(value > 0) "+" else "") +
                    value + " semitons",delta==0) { choose(value) },8)
            }
        }''','''                add(choices, button(name + " · " + (if(value > 0) "+" else "") +
                    value + " semitons",delta==0) { choose(value) },8)
                addTonePreviewOption(value)
            }
        }''')
once('''    private fun choose(semitones: Int) {
        setResult(RESULT_OK, Intent().putExtra(EXTRA_CHOSEN_SHIFT, semitones))''','''    private fun addTonePreviewOption(shift: Int) {
        if (toneSource == null) return
        val signed = if (shift > 0) "+$shift" else shift.toString()
        lateinit var control: MaterialButton
        control = button("▶ Ouvir $signed semitons") { previewTone(shift, control) }
        add(choices, control, 4)
    }

    private fun stopTonePreview() {
        toneTimeout?.let(toneUi::removeCallbacks)
        toneTimeout = null
        tonePlayer.pause()
        val oldControl = toneButton
        if (oldControl != null && toneButtonLabel != null) {
            oldControl.text = toneButtonLabel
        }
        toneButton = null
        toneButtonLabel = null
    }

    private fun previewTone(shift: Int, control: MaterialButton) {
        if (toneButton === control && tonePlayer.isPlaying()) {
            stopTonePreview()
            return
        }
        stopTonePreview()
        if (capturing) {
            trackStatus.text = "Conclua a gravação vocal antes de ouvir o trecho."
            return
        }
        val source = toneSource ?: return
        if (!source.pcmFile.isFile || source.pcmFile.length() !=
            source.frames * source.channels * 4L) {
            trackStatus.text = "A música não está disponível para prévia. Reimporte o arquivo."
            return
        }
        try {
            val position = (excerptSeek.progress / 100.0).coerceIn(0.0, 0.99)
            tonePlayer.setProject(source, position)
            val factor = 2.0.pow(shift / 12.0).toFloat()
            tonePlayer.setPreviewParams(factor, 1f)
            tonePlayer.play()
            if (!tonePlayer.isPlaying()) {
                trackStatus.text = "O aparelho não conseguiu reproduzir esta tonalidade."
                return
            }
            toneButton = control
            toneButtonLabel = control.text.toString()
            control.text = "■ Parar prévia · $shift semitons"
            val timeout = Runnable { stopTonePreview() }
            toneTimeout = timeout
            toneUi.postDelayed(timeout, 9000L)
        } catch (error: Exception) {
            stopTonePreview()
            trackStatus.text = "Prévia indisponível: " +
                (error.message ?: "reprodução de áudio não iniciada")
        }
    }

    private fun choose(semitones: Int) {
        stopTonePreview()
        setResult(RESULT_OK, Intent().putExtra(EXTRA_CHOSEN_SHIFT, semitones))''')
once('''        clearIsolatedPreview()
        super.onStop()''','''        clearIsolatedPreview()
        stopTonePreview()
        super.onStop()''')
once('''    override fun onDestroy() {
        capturing = false
        super.onDestroy()''','''    override fun onDestroy() {
        capturing = false
        toneTimeout?.let(toneUi::removeCallbacks)
        tonePlayer.release()
        super.onDestroy()''')
activity.write_text(s,encoding="utf-8")
gradle=root/"app/build.gradle.kts"
g=gradle.read_text(encoding="utf-8")
if g.count('versionName = "1.12.2"')!=1 or g.count('versionCode = 33')!=1:
 raise SystemExit("Versão-base 1.12.2 não encontrada")
g=g.replace('versionName = "1.12.2"','versionName = "1.12.3"',1)
g=g.replace('versionCode = 33','versionCode = 34',1)
gradle.write_text(g,encoding="utf-8")
assert '▶ Ouvir $signed semitons' in s
assert 'tonePlayer.setPreviewParams(factor, 1f)' in s
print("BEAT flow 1.12.3: três tonalidades com audição local integradas.")

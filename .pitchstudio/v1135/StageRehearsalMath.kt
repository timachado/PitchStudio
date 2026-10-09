package br.com.timachado.pitchstudio

/** Operações de navegação locais e testáveis, independentes do áudio. */
internal object StageRehearsalMath {
    fun seek(current: Double, seconds: Double, frames: Long, sampleRate: Int): Double {
        if (frames <= 0 || sampleRate <= 0 || !current.isFinite() || !seconds.isFinite())
            return 0.0
        val duration = frames.toDouble() / sampleRate
        return (current.coerceIn(0.0,1.0) + seconds/duration).coerceIn(0.0,1.0)
    }
    fun validLoop(start: Double?, end: Double): Boolean =
        start != null && start.isFinite() && end.isFinite() &&
            start >= 0.0 && start < 1.0 && end <= 1.0 && end > start + 0.003
    fun scrollPixels(speed: Int, density: Float): Int {
        val logical = when(speed) {0 -> 1; 2 -> 5; else -> 3}
        return (logical * density.coerceAtLeast(1f)).toInt().coerceAtLeast(1)
    }
}

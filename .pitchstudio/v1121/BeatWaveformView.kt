package br.com.timachado.pitchstudio

import android.content.Context
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.view.View
import kotlin.math.abs
import kotlin.math.max
import kotlin.math.min

/**
 * Onda do áudio isolado, construída a partir de picos medidos pelo motor de IA.
 * Não gera barras fictícias antes de existir arquivo processado.
 */
internal class BeatWaveformView(context: Context) : View(context) {
    private val p = Paint(Paint.ANTI_ALIAS_FLAG)
    private var amplitudes = FloatArray(0)
    private val colors = intArrayOf(
        Color.rgb(255,98,139),
        Color.rgb(196,179,255),
        Color.rgb(23,213,226)
    )

    fun showSamples(samples: FloatArray?) {
        amplitudes = samples?.copyOf() ?: FloatArray(0)
        visibility = if (amplitudes.isEmpty()) GONE else VISIBLE
        invalidate()
    }

    override fun onMeasure(widthMeasureSpec: Int, heightMeasureSpec: Int) {
        val dp = resources.displayMetrics.density
        super.onMeasure(widthMeasureSpec,
            MeasureSpec.makeMeasureSpec((88 * dp).toInt(), MeasureSpec.EXACTLY))
    }

    override fun onDraw(canvas: Canvas) {
        super.onDraw(canvas)
        if (amplitudes.isEmpty() || width <= 0) return
        val count = amplitudes.size
        val h = height.toFloat()
        val spacing = width.toFloat() / count
        val barW = max(2f, spacing * 0.55f)
        val peak = max(0.015f, amplitudes.maxOf { abs(it) })
        for (i in 0 until count) {
            val x = (i+0.5f) * spacing
            val norm = (abs(amplitudes[i]) / peak).coerceIn(0f,1f)
            val barH = max(4f, norm * (h*0.82f))
            p.color = colors[min(colors.lastIndex, (i*colors.size/count))]
            p.alpha = 240
            canvas.drawRoundRect(x-barW/2, h/2-barH/2,
                x+barW/2, h/2+barH/2, barW/2, barW/2,p)
        }
    }
}

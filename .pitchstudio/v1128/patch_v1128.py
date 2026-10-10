#!/usr/bin/env python3
"""BEAT flow 1.12.8 — corrigir o estimador para vozes estéreo com oposição de fase."""
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
base=root/"app/src/main/java/br/com/timachado/pitchstudio"
path=base/"PlaybackVocalReducer.kt"
src=path.read_text(encoding="utf-8")
old="""            val v = vl.toDouble() + vr.toDouble()
            val m = ml.toDouble() + mr.toDouble()
            // Ambos os canais conservam o mesmo ganho, preservando a imagem estéreo.
            vocalEnergy += v * v
            mixEnergy += m * m
            cross += v * m"""
new="""            // Energias por canal para vozes com polaridade oposta no estéreo.
            // Somar L+R antes de estimar cancelaria esse tipo de voz.
            // Um único ganho continua aplicado a ambos os canais.
            val vL = vl.toDouble()
            val vR = vr.toDouble()
            val mL = ml.toDouble()
            val mR = mr.toDouble()
            vocalEnergy += vL * vL + vR * vR
            mixEnergy += mL * mL + mR * mR
            cross += vL * mL + vR * mR"""
assert src.count(old)==1, "Vocal reducer foi modificado; não substituir sem revisão."
path.write_text(src.replace(old,new,1),encoding="utf-8")
tests=root/"app/src/test/java/br/com/timachado/pitchstudio/PlaybackVocalReducerTest.kt"
t=tests.read_text(encoding="utf-8")
assert t.endswith("\n}\n") and "class PlaybackVocalReducerTest" in t
newtest="""
    @Test fun stereoAntiPhaseVocalRemainsDetectable() {
        val n = 8192
        val offset = 64
        val lead = FloatArray(n) { i ->
            (0.28 * sin(2 * Math.PI * 220 * i / 44100)).toFloat()
        }
        val accompaniment = FloatArray(n) { i ->
            (0.12 * sin(2 * Math.PI * 330 * i / 44100)).toFloat()
        }
        val vocalL = FloatArray(n) { lead[it] * 0.7f }
        val vocalR = FloatArray(n) { -lead[it] * 0.7f }
        val mixL = FloatArray(n + offset) { i ->
            if (i < offset) 0f else lead[i-offset] + accompaniment[i-offset]
        }
        val mixR = FloatArray(n + offset) { i ->
            if (i < offset) 0f else -lead[i-offset] + accompaniment[i-offset]
        }
        val gain = PlaybackVocalReducer.estimateGain(
            mixL, mixR, vocalL, vocalR, 0, n, offset
        )
        assertTrue("Voz estéreo não deve cancelar antes do cálculo", gain > 1.3f)
        assertTrue(gain <= PlaybackVocalReducer.MAX_VOCAL_GAIN)
        var errorBefore = 0.0
        var errorAfter = 0.0
        for (i in 0 until n) {
            val e0 = mixL[i+offset] - vocalL[i] - accompaniment[i]
            val e1 = PlaybackVocalReducer.instrumental(
                mixL[i+offset],vocalL[i],gain
            ) - accompaniment[i]
            errorBefore += e0 * e0
            errorAfter += e1 * e1
        }
        assertTrue("Estéreo antifase: reduzir voz residual",errorAfter < 0.12 * errorBefore)
    }
"""
assert "stereoAntiPhaseVocalRemainsDetectable" not in t
tests.write_text(t[:-2] + newtest + "}\n",encoding="utf-8")
gradle=root/"app/build.gradle.kts"
g=gradle.read_text(encoding="utf-8")
for old,new in (("versionCode = 38","versionCode = 39"),('versionName = "1.12.7"','versionName = "1.12.8"')):
    assert g.count(old)==1, "base 1.12.7 não encontrada: "+old
    g=g.replace(old,new,1)
gradle.write_text(g,encoding="utf-8")
print("BEAT flow v1.12.8: cálculo estéreo de ganho aprimorado e regressão antifase adicionada.")

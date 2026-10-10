#!/usr/bin/env python3
"""BEAT flow 1.13.0 — sincronizar vocal com áudio-fonte antes de gerar playback.
Corrige erro matemático de 2048 samples (46,44ms a 44100Hz) detectado
pela comparação do original com o WAV exportado pelo usuário.
"""
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve()
base=root/"app/src/main/java/br/com/timachado/pitchstudio"
engine=base/"VocalStemSeparator.kt"
s=engine.read_text(encoding="utf-8")
def replace_once(old,new):
    global s
    n=s.count(old)
    if n!=1:
        raise RuntimeError(f"Não encontrei marcador único ({n}): {old[:95]}")
    s=s.replace(old,new,1)
# Manter o vocal ISOLADO antigo intacto. Apenas separarStems com PLAYBACK precisa
# casar a origem left[i+FFT_SIZE] com a saída da STFT (janela centrada -HALF).
replace_once("                            val vocalsL = istft(inferred, 0)\n                            val vocalsR = istft(inferred, 2)",
"""                            // VOICE continua usando o caminho original inalterado.
                            // PLAYBACK/BOTH exigem sinal no mesmo instante de left[i+FFT_SIZE].
                            val mixAlignment = if (beatOut != null) HALF else 0
                            val vocalsL = istft(inferred, 0, mixAlignment)
                            val vocalsR = istft(inferred, 2, mixAlignment)""")
replace_once("                                val nextL = istft(inferred, 0)\n                                val nextR = istft(inferred, 2)",
"""                                // Segunda inferência recebe a mistura já alinhada.
                                val nextL = istft(inferred, 0, HALF)
                                val nextR = istft(inferred, 2, HALF)""")
replace_once("    private fun istft(spec: ByteBuffer, plane: Int): FloatArray {",
"""    private fun istft(spec: ByteBuffer, plane: Int, alignmentOffset: Int = 0): FloatArray {
        require(alignmentOffset == 0 || alignmentOffset == HALF)""")
replace_once("            val idx = i + HALF * 2 // trim center; see MDX pipeline",
"""            // STFT lê samples[frame*HOP + i - HALF]; a síntese antiga
            // devolvia sample[i+HALF] quando o playback subtraía
            // sample[i+FFT_SIZE]. Faltavam HALF=2048 amostras de alinhamento.
            val idx = i + HALF * 2 + alignmentOffset""")
# Derivação: síntese em idx tem origem em input[idx-HALF]; mix em input[i+FFT_SIZE].
# Offset extra HALF: idx=i+3HALF -> idx-HALF=i+2HALF=i+FFT_SIZE.
FFT_SIZE=4096
HALF=FFT_SIZE//2
FRAMES=256
HOP=1024
CHUNK=HOP*(FRAMES-1)
USABLE=CHUNK-FFT_SIZE
assert 2*HALF+HALF-HALF==FFT_SIZE
assert (USABLE-1)+3*HALF < CHUNK+FFT_SIZE
assert 'val vocalLeft = istft(inferred, 0)' in s
assert 'val vocalRight = istft(inferred, 2)' in s
assert s.count("val vocalsL = istft(inferred, 0, mixAlignment)")==1
assert s.count("val nextL = istft(inferred, 0, HALF)")==1
engine.write_text(s,encoding="utf-8")
gradle=root/"app/build.gradle.kts"
g=gradle.read_text(encoding="utf-8")
for old,new in [
    ("versionCode = 40","versionCode = 41"),
    ('versionName = "1.12.9"','versionName = "1.13.0"')
]:
    if g.count(old)!=1:raise RuntimeError(f"Base incompatível: {old}")
    g=g.replace(old,new,1)
gradle.write_text(g,encoding="utf-8")
print("BEAT flow 1.13.0: voz original preservada; playback corrigido em +2048 amostras e segunda inferência alinhada.")

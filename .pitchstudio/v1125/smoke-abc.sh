#!/usr/bin/env bash
set -euo pipefail
# Regressão completa: IA 18/180 s, WAV/MP3, YouTube e navegação.
source "$GITHUB_WORKSPACE/.pitchstudio/v1121/smoke-3min-corrected.sh" "$1"
adb shell input keyevent 4
sleep 2
visible "BEAT flow"
for _ in 1 2 3 4; do adb shell input swipe 500 510 500 1570 220; done
sleep 2
tap "Comparar A/B/C"
tap "C · Outra"
visible "C · Alternativa"
tap "A · Original"
visible "posição sincronizada"
tap "B · Atual"
visible "B · Atual"
tap "Configurar C"
visible "Configurar versão C"
tap "Guardar C"
visible "C · Alternativa"
for _ in 1 2 3; do adb shell input swipe 500 510 500 1570 200; done
tap "Comparar A/B/C"
visible "A/B:"
echo "PASSOU: A/B/C, ajuste de C e A/B original preservados."

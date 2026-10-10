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
# O rótulo da configuração fica abaixo da dobra em telas pequenas.
# Procurar no conteúdo completo, rolando antes de concluir que falhou.
for attempt in 1 2 3 4 5; do
  readui
  if grep -q 'C · Alternativa' "$OUT/current.xml"; then
    echo "PASSOU: C · Alternativa visível."
    break
  fi
  if [ "$attempt" -eq 5 ]; then
    echo "FALHA: C não foi ativada." >&2
    exit 1
  fi
  adb shell input swipe 500 1590 500 810 230
  sleep 1
done
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

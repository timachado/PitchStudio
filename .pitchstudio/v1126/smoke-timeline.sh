#!/usr/bin/env bash
set -euo pipefail
# Primeiro exercitar a regressão já aprovada de áudio/IA/exportação/ABC.
source "$GITHUB_WORKSPACE/.pitchstudio/v1125/smoke-abc.sh" "$1"
# Voltar ao editor ainda vinculado ao projeto de 180 s aberto no smoke legado.
for _ in 1 2 3 4; do adb shell input swipe 500 510 500 1570 220; done
sleep 2
visible "Linha do Tempo Inteligente"
tap "Marcar trecho"
visible "Introdução"
tap "Introdução"
visible "1 trecho marcado"
# Confirma persistência de bytes no JSON; não basta o estado visível na tela.
adb exec-out run-as "$PKG" cat "files/saved_audio_projects/$ID_LONG/project.json" > "$OUT/timeline_saved.json"
python3 - "$OUT/timeline_saved.json" <<'PY'
import json,sys
p=json.load(open(sys.argv[1],encoding='utf-8'))
assert p['schema']==1
marks=p['songSections']
assert len(marks)==1,marks
assert marks[0]['label']=='Introdução',marks
assert 0<=marks[0]['fraction']<1,marks
print('PASSOU: trechos persistidos em JSON do projeto original.')
PY
tap "Ver trechos"
visible "Introdução"
tap "Introdução"
visible "Ir para o trecho"
tap "Ir para o trecho"
# Reabrir a biblioteca deve restaurar marcações, sem copiar ou destruir PCM.
adb shell am force-stop "$PKG"
adb shell am start -W -n "$PKG/br.com.timachado.pitchstudio.MainActivity"
sleep 5
tap "Meus projetos"
tap "Teste Playback 180s"
tap "Abrir e continuar"
sleep 5
visible "1 trecho marcado"
echo "PASSOU: Linha do Tempo reaberta com marcação manual persistente."

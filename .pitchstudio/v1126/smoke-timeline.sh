#!/usr/bin/env bash
set -euo pipefail
# Primeiro exercitar a regressão já aprovada de áudio/IA/exportação/ABC.
source "$GITHUB_WORKSPACE/.pitchstudio/v1125/smoke-abc.sh" "$1"
# Voltar ao editor ainda vinculado ao projeto de 180 s aberto no smoke legado.
# O cartão está abaixo da dobra ao concluir A/B/C. tap() já rola até ele.
tap "Marcar trecho"
sleep 1
readui
# Em alguns tamanhos de tela, a caixa ainda está animando quando o próximo
# toque ocorre. Não esconder falha real; tentar abrir uma segunda vez e validar.
if ! grep -q 'text="Introdução"' "$OUT/current.xml"; then
  echo "QA: lista de tipos ainda não apareceu; repetindo abertura do diálogo."
  tap "Marcar trecho"
  sleep 2
  readui
fi
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
# Nova etapa: salvar uma automação por trecho e verificar os bytes reais do JSON.
tap "Ver trechos"
tap "Introdução"
tap "Ajustar tom e velocidade"
visible "Ajustes do trecho"
tap "Salvar ajuste"
adb exec-out run-as "$PKG" cat "files/saved_audio_projects/$ID_LONG/project.json" > "$OUT/section_overrides.json"
python3 - "$OUT/section_overrides.json" <<'PY'
import json,sys
data=json.load(open(sys.argv[1],encoding="utf-8"))
assert len(data["songSections"])==1
items=data["sectionOverrides"]
assert len(items)==1,items
assert abs(items[0]["fraction"]-data["songSections"][0]["fraction"])<1e-6
assert -12<=items[0]["semitones"]<=12
assert .5<=items[0]["speed"]<=2.0
print("PASSOU: ajuste por trecho persistido em JSON.")
PY
tap "▶ Prévia por trechos"
visible "■ Encerrar prévia por trechos"
tap "■ Encerrar prévia por trechos"
echo "PASSOU: prévia de trecho liga e desliga sem alterar PCM."

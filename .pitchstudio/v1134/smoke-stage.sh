#!/usr/bin/env bash
set -euo pipefail
APK="$1"
PKG="br.com.timachado.beatflow.waveqa"
TMP="${RUNNER_TEMP:-/tmp}/beatflow-stage-qa"
mkdir -p "$TMP"
UI="$TMP/window.xml"
EVIDENCE="$RUNNER_TEMP/beatflow-wave-1121-smoke"
mkdir -p "$EVIDENCE"
collect_evidence() {
  adb shell uiautomator dump /sdcard/beatflow-stage-diag.xml >/dev/null 2>&1 || true
  adb exec-out cat /sdcard/beatflow-stage-diag.xml > "$EVIDENCE/stage-failure.xml" 2>/dev/null || true
  adb shell screencap -p /sdcard/beatflow-stage-diag.png >/dev/null 2>&1 || true
  adb pull /sdcard/beatflow-stage-diag.png "$EVIDENCE/stage-failure.png" >/dev/null 2>&1 || true
  adb logcat -d -b main -b crash > "$EVIDENCE/stage-logcat.txt" 2>/dev/null || true
  adb shell dumpsys activity activities > "$EVIDENCE/stage-activities.txt" 2>/dev/null || true
  echo "QA Stage: ACTIVE TASK:"
  grep -Ei 'topResumedActivity|mResumedActivity|Resumed: ActivityRecord' "$EVIDENCE/stage-activities.txt" | tail -3 || true
  echo "QA Stage: POTENTIAL ERRORS:"
  grep -Ei 'FATAL EXCEPTION|Estrutura Expressive inesperada|AndroidRuntime|IllegalStateException|NullPointerException' "$EVIDENCE/stage-logcat.txt" | tail -16 || true
}
trap 'status=$?; if [ "$status" -ne 0 ]; then collect_evidence; fi' EXIT
refresh() {
  adb shell uiautomator dump /sdcard/beatflow-stage.xml >/dev/null
  adb exec-out cat /sdcard/beatflow-stage.xml > "$UI"
}
visible() {
  refresh
  python3 - "$UI" "$1" <<'PY'
import sys,xml.etree.ElementTree as ET
root=ET.parse(sys.argv[1]).getroot()
if not any(n.get('text','')==sys.argv[2] for n in root.iter('node')):
    print('QA Stage: rótulo não visível:',repr(sys.argv[2]),file=sys.stderr)
    raise SystemExit(1)
PY
}
click_text() {
  local label="$1" coords="" attempt
  # Primeiro testa o estado atual; depois procura acima e, por fim, abaixo.
  for attempt in $(seq 0 44); do
    refresh
    coords="$(python3 - "$UI" "$label" <<'PY'
import sys,xml.etree.ElementTree as ET,re
root=ET.parse(sys.argv[1]).getroot()
items=[]
for e in root.iter('node'):
    text=e.get('text','')
    desc=e.get('content-desc','')
    target=sys.argv[2]
    match=0 if text==target or desc==target else (1 if text.startswith(target) or desc.startswith(target) else 9)
    if match==9:continue
    bounds=list(map(int,re.findall(r'\d+',e.get('bounds',''))))
    if len(bounds)!=4:continue
    if bounds[2]<=bounds[0] or bounds[3]<=bounds[1]:continue
    items.append((match,0 if e.get('clickable')=='true' else 1,bounds))
if items:
    items.sort(key=lambda it:it[:2])
    a,b,c,d=items[0][2]
    print((a+c)//2,(b+d)//2)
PY
)"
    if [ -n "$coords" ]; then
      echo "QA Stage: TOQUE: $label -> $coords"
      adb shell input tap $coords
      sleep 1
      return 0
    fi
    if [ "$attempt" -lt 12 ]; then
      adb shell input swipe 500 480 500 1700 220
    else
      adb shell input swipe 500 1600 500 470 220
    fi
    sleep 0.3
  done
  echo "QA Stage: controle ausente após busca bidirecional: $label" >&2
  refresh || true
  cp "$UI" "$TMP/fail.xml" || true
  adb shell screencap -p /sdcard/beatflow-stage-fail.png || true
  adb pull /sdcard/beatflow-stage-fail.png "$TMP/fail.png" >/dev/null 2>&1 || true
  exit 1
}
adb install -r "$APK" >/dev/null
adb shell am force-stop "$PKG" || true
adb shell am start -W -n "$PKG/br.com.timachado.pitchstudio.MainActivity" >/dev/null
sleep 4
# Testar abertura real do Tom Ideal, sem confundir scroll com funcionalidade.
refresh
echo "QA Stage: STARTUP VISIBLE LABELS:"
python3 - "$UI" <<'PY'
import sys, xml.etree.ElementTree as ET
for node in ET.parse(sys.argv[1]).getroot().iter('node'):
    t=node.get('text') or node.get('content-desc')
    if t: print(' •', t[:95])
PY
echo "QA Stage: app process $(adb shell pidof "$PKG" || echo missing)"
click_text "Tom Ideal · Analisar minha voz"
visible "Analisar minha voz"
adb shell input keyevent 4
sleep 2
click_text "Modo Palco e Ensaio"
visible "BEAT flow · Palco & Ensaio"
# Controle de acompanhamento deve aparecer e não pode travar sem música aberta.
for scrollCount in 1 2 3 4 5 6 7; do
  refresh
  if grep -Fq 'Seguir cifras: desligado' "$UI"; then break; fi
  adb shell input swipe 500 1250 500 550 220
  sleep 1
done
visible "Seguir cifras: desligado"
click_text "Seguir cifras: desligado"
visible "Seguir cifras: desligado"
# Conferir controles novos sem afetar biblioteca nem PCM.
for scrollCount in 1 2 3 4 5 6; do
  refresh
  if grep -Fq 'Velocidade: Média' "$UI"; then break; fi
  adb shell input swipe 500 1250 500 540 260
  sleep 1
done
click_text "Velocidade: Média"
visible "Velocidade: Rápida"
click_text "Velocidade: Rápida"
visible "Velocidade: Lenta"
# Volta ao topo para trabalhar com os repertórios existentes.
for scrollCount in 1 2 3 4 5 6; do adb shell input swipe 500 480 500 1400 180; done
sleep 1
click_text "Novo repertório"
adb shell input text RepertorioQA
click_text "Criar"
visible "RepertorioQA · 0 músicas"
adb exec-out run-as "$PKG" cat files/stage_setlists.json > "$TMP/repertorios.json"
python3 - "$TMP/repertorios.json" <<'PY'
import sys,json
v=json.load(open(sys.argv[1],encoding='utf-8'))
assert v['schema']==1
assert len(v['setlists'])==1
s=v['setlists'][0]
assert s['title']=='RepertorioQA' and s['songs']==[]
print('PASSOU: repertório offline salvo sem copiar áudio.')
PY
click_text "Ativar Modo Palco"
visible "Sair do Modo Palco · Ensaio"
click_text "Sair do Modo Palco · Ensaio"
visible "Ativar Modo Palco"
adb shell am force-stop "$PKG"
echo 'PASSOU: Modo Palco e Ensaio abre, salva repertório offline e troca de modo.'

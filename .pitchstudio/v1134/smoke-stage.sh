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
    # Nem todo nó presente no XML está tocável: nunca enviar tap à
    # barra de gestos do Android (bug real do antigo smoke em y=2304).
    screen=list(map(int,re.findall(r'\d+',root.find('node').get('bounds',''))))
    screen_h=screen[3] if len(screen)==4 else 2340
    x,y=(a+c)//2,(b+d)//2
    if y>=screen_h-340:
        print('SCROLL_UP')
    elif y<=140:
        print('SCROLL_DOWN')
    else:
        print(x,y)
PY
)"
    if [ "$coords" = "SCROLL_UP" ]; then
      echo "QA Stage: rolando para revelar controle abaixo da área segura: $label"
      adb shell input swipe 1045 1730 1045 770 260
      sleep 0.45
      continue
    fi
    if [ "$coords" = "SCROLL_DOWN" ]; then
      echo "QA Stage: rolando para revelar controle acima da área segura: $label"
      adb shell input swipe 1045 760 1045 1750 260
      sleep 0.45
      continue
    fi
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
# A caixa de texto de um MaterialAlertDialog não recebe foco garantido.
# Clicar nela antes de digitar impede que o comando input text vá para a tela
# anterior; fechar primeiro o teclado evita o botão Criar sob a área de gestos.
refresh
name_bounds="$(python3 - "$UI" <<'PY'
import re,sys,xml.etree.ElementTree as ET
root=ET.parse(sys.argv[1]).getroot()
nodes=[n for n in root.iter('node') if n.get('class','').endswith('EditText') and n.get('enabled')=='true']
if len(nodes)!=1:
    raise SystemExit('QA Stage: caixa de nome não encontrada ou ambígua no diálogo Novo repertório')
bounds=list(map(int,re.findall(r'\\d+',nodes[0].get('bounds',''))))
if len(bounds)!=4 or bounds[0]>=bounds[2] or bounds[1]>=bounds[3]:
    raise SystemExit('QA Stage: limites inválidos do campo de nome')
print((bounds[0]+bounds[2])//2,(bounds[1]+bounds[3])//2)
PY
)"
adb shell input tap $name_bounds
adb shell input text RepertorioQA
sleep 0.5
refresh
python3 - "$UI" <<'PY'
import sys,xml.etree.ElementTree as ET
root=ET.parse(sys.argv[1]).getroot()
fields=[n for n in root.iter('node') if n.get('class','').endswith('EditText')]
if len(fields)!=1 or fields[0].get('text')!='RepertorioQA':
    raise SystemExit('QA Stage: nome do repertório não foi digitado no campo esperado')
PY
# O toque no EditText abriu o IME. Primeiro fechá-lo, depois localizar Criar.
# Não rolar a tela de fundo enquanto o diálogo modal está aberto.
adb shell input keyevent KEYCODE_BACK
sleep 0.7
visible "Criar"
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

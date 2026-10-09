#!/usr/bin/env bash
set -euo pipefail
APK="$1"
PKG="br.com.timachado.beatflow.waveqa"
TMP="${RUNNER_TEMP:-/tmp}/beatflow-stage-qa"
mkdir -p "$TMP"
UI="$TMP/window.xml"
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
  local label="$1" coords
  refresh
  coords="$(python3 - "$UI" "$label" <<'PY'
import sys,xml.etree.ElementTree as ET,re
root=ET.parse(sys.argv[1]).getroot()
for e in root.iter('node'):
    if e.get('text','')==sys.argv[2]:
        b=e.get('bounds','')
        a=list(map(int,re.findall(r'\d+',b)))
        if len(a)==4:
            print((a[0]+a[2])//2,(a[1]+a[3])//2)
            break
PY
)"
  if [ -z "$coords" ]; then
    echo "QA Stage: controle ausente: $label" >&2
    exit 1
  fi
  adb shell input tap $coords
  sleep 1
}
adb install -r "$APK" >/dev/null
adb shell am force-stop "$PKG" || true
adb shell am start -W -n "$PKG/br.com.timachado.pitchstudio.MainActivity" >/dev/null
sleep 4
for i in 1 2 3 4 5 6 7; do
  refresh
  if grep -Fq 'text="Modo Palco e Ensaio"' "$UI"; then break; fi
  adb shell input swipe 500 1350 500 550 250
  sleep 1
done
click_text "Modo Palco e Ensaio"
visible "BEAT flow · Palco & Ensaio"
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

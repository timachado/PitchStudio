#!/usr/bin/env bash
set -euo pipefail
APK="$1"
PKG="br.com.timachado.beatflow.waveqa"
OUT="$RUNNER_TEMP/beatflow-wave-1121-smoke"
mkdir -p "$OUT"
cleanup() {
  adb logcat -d -b main -b crash > "$OUT/logcat.txt" 2>/dev/null || true
  adb shell screencap -p /sdcard/tom-ideal-test.png >/dev/null 2>&1 || true
  adb pull /sdcard/tom-ideal-test.png "$OUT/screen.png" >/dev/null 2>&1 || true
  adb shell uiautomator dump /sdcard/final.xml >/dev/null 2>&1 || true
  adb shell cat /sdcard/final.xml > "$OUT/final.xml" 2>/dev/null || true
}
trap cleanup EXIT
adb wait-for-device
adb install -r "$APK"
# Permissão concedida explicitamente no teste; o fluxo de negativa
# continua implementado na Activity sem depender da língua do emulador.
adb shell pm grant "$PKG" android.permission.RECORD_AUDIO
adb shell am start -W -n "$PKG/br.com.timachado.pitchstudio.MainActivity"
sleep 5
readui() {
  for overlay_attempt in 1 2 3; do
    adb shell uiautomator dump /sdcard/view.xml >/dev/null 2>&1 || true
    adb shell cat /sdcard/view.xml > "$OUT/current.xml" || true
    if grep -qiE 'Quickstep (isn.t responding|keeps stopping)|System UI isn.t responding' "$OUT/current.xml"; then
      echo "Aviso de ANR do launcher do EMULADOR; fechando apenas a janela do sistema."
      adb shell input tap 530 1180 || true
      sleep 2
      adb shell am start -W -n "$PKG/br.com.timachado.pitchstudio.MainActivity" >/dev/null 2>&1 || true
      sleep 2
      continue
    fi
    break
  done
}
visible() {
  readui
  python3 - "$OUT/current.xml" "$1" <<'PY'
import sys
from xml.etree import ElementTree as ET
wanted=sys.argv[2]
nodes=list(ET.parse(sys.argv[1]).getroot().iter("node"))
if not any(wanted in (n.get("text","")+" "+n.get("content-desc","")) for n in nodes):
    raise SystemExit("Não visível: "+wanted)
print("VISÍVEL:",wanted)
PY
}
tap() {
  for attempt in 1 2 3 4; do
    readui
    if pos=$(python3 - "$OUT/current.xml" "$1" <<'PY'
import sys,re
from xml.etree import ElementTree as ET
wanted=sys.argv[2]
nodes=list(ET.parse(sys.argv[1]).getroot().iter("node"))
for exact in (True,False):
  for n in nodes:
    value=(n.get("text","")+" "+n.get("content-desc","")).strip()
    if (value==wanted if exact else wanted in value):
      box=list(map(int,re.findall(r"\d+",n.get("bounds",""))))
      if len(box)==4:
        a,b,c,d=box
        print((a+c)//2,(b+d)//2)
        raise SystemExit(0)
raise SystemExit(1)
PY
); then
      read -r X Y <<<"$pos"
      echo "TOQUE: $1 -> $X,$Y"
      adb shell input tap "$X" "$Y"
      sleep 2
      return 0
    fi
    adb shell input swipe 500 1400 500 600 250
    sleep 1
  done
  echo "Controle não localizado: $1"
  exit 1
}
# A imagem do emulador às vezes apresenta ANR no Pixel Launcher.
# Reabrir a Activity alvo ao invés de confundir a sobreposição com crash do app.
for attempt in 1 2 3 4; do
  if visible "BEAT flow"; then break; fi
  echo "Aguardando launcher do emulador (tentativa $attempt)"
  adb shell input keyevent 4 || true
  adb shell am start -W -n "$PKG/br.com.timachado.pitchstudio.MainActivity" || true
  sleep 5
done
visible "BEAT flow"
visible "Seu som. No seu ritmo."
tap "Tom Ideal"
visible "Tom Ideal"
visible "Analisar minha voz"
visible "Comparar voz e música"
visible "Analisar trecho selecionado"
# O novo botão pode ficar fora da dobra; tap() rola antes de tocar.
tap "Isolar voz com IA"
visible "Importe uma música"
tap "Analisar trecho selecionado"
visible "Importe uma música"
# O novo card de IA desloca o microfone para cima na tela:
# retornar ao topo antes de tentar tocar no botão.
for up in 1 2 3 4 5; do adb shell input swipe 520 500 520 1550 230; done
sleep 1
# A permissão fica reservada ao uso do microfone. Negar não pode encerrar a tela.
tap "Analisar minha voz"
# No emulador a captura termina sozinha após 12 segundos. Não exigir que
# "Concluir análise" ainda esteja visível depois da coleta.
sleep 14
visible "Analisar novamente"
# Após a introdução do seletor, os botões ficam abaixo da dobra.
# tap() localiza o controle e rola a tela antes de tocá-lo.
tap "Mais grave"
sleep 2
visible "BEAT flow"
# A indicação de semitons fica fora da primeira dobra do editor Expressive.
for attempt in 1 2 3 4 5 6 7; do
  readui
  if grep -q -- '-2 semitons' "$OUT/current.xml"; then
    echo "PASSOU: a seleção -2 semitons voltou ao editor."
    break
  fi
  if [ "$attempt" = 7 ]; then
    echo "ERRO: alteração de -2 semitons não localizada no editor" >&2
    exit 1
  fi
  adb shell input swipe 500 1500 500 500 280
  sleep 1
done
echo "PASSOU: retorno do Tom Ideal ao editor."
for back_to_top in 1 2 3 4 5 6; do
  adb shell input swipe 500 450 500 1550 230
done
sleep 1
tap "YouTube"
visible "EXPLORAR MÚSICAS"
echo "PASSOU: tela YouTube abre sem crash."
# Confere retorno de navegação sem deixar o player preso em segundo plano.
adb shell input keyevent 4
sleep 2
visible "BEAT flow"
echo "PASSOU: navegação volta do YouTube ao editor."
# Teste da inferência real com faixa longa, sem depender da busca YouTube.
echo "Obtendo áudio vocal real de referência do sherpa-onnx..."
curl --fail --location --retry 3 --connect-timeout 30 --max-time 150 \
  'https://github.com/k2-fsa/sherpa-onnx/releases/download/source-separation-models/qi-feng-le-zh.wav' \
  --output "$OUT/qi-feng-le-zh.wav"
python3 - "$OUT" <<'PY'
from pathlib import Path
import array, json, math, sys, struct, time, wave
directory=Path(sys.argv[1])
# Referência pública oficial do mesmo modelo, cantada, em lugar de uma
# senoide sintética sem características espectrais de uma voz humana.
with wave.open(str(directory/"qi-feng-le-zh.wav"),"rb") as wav:
    rate=wav.getframerate()
    channels=wav.getnchannels()
    width=wav.getsampwidth()
    total=wav.getnframes()
    assert rate==44100 and channels==2 and width==2, (rate,channels,width)
    frames=min(rate*21,total)
    start=max(0, min(rate*2, total-frames))
    assert frames >= rate*18, "A referência vocal é curta demais para validar 18 segundos."
    wav.setpos(start)
    data=wav.readframes(frames)
samples=array.array("h"); samples.frombytes(data)
if sys.byteorder!="little": samples.byteswap()
assert len(samples)==frames*2
energy=0.0; peak=0.0
with (directory/"stems_test.f32").open("wb") as out:
    for value in samples:
        floating=value/32768.0
        energy+=floating*floating
        peak=max(peak,abs(floating))
        out.write(struct.pack("<f",floating))
rms=math.sqrt(energy/len(samples))
assert rms>0.003,(rms,frames)
meta={
    "schema":1,"title":"Teste IA Musical","updatedAt":int(time.time()*1000),
    "sampleRate":rate,"channels":2,"frames":frames,"peak":peak,
    "waveform":[peak]*90,"semitones":0,"cents":0,"speed":1.0,
    "quality":"ALTA","position":0.0
}
(directory/"stems_test.json").write_text(json.dumps(meta),encoding="utf-8")
print(f"Faixa real: {frames/rate:.2f}s a {rate} Hz, RMS original {rms:.5f}")
PY
ID="223e4567-e89b-12d3-a456-426614174111"
adb push "$OUT/stems_test.f32" /data/local/tmp/pitchstudio-vocal-test.f32 >/dev/null
adb push "$OUT/stems_test.json" /data/local/tmp/pitchstudio-vocal-test.json >/dev/null
adb shell run-as "$PKG" mkdir -p "files/saved_audio_projects/$ID"
adb shell run-as "$PKG" cp /data/local/tmp/pitchstudio-vocal-test.f32 "files/saved_audio_projects/$ID/original.f32"
adb shell run-as "$PKG" cp /data/local/tmp/pitchstudio-vocal-test.json "files/saved_audio_projects/$ID/project.json"

adb shell am force-stop "$PKG"
adb shell am start -W -n "$PKG/br.com.timachado.pitchstudio.MainActivity"
sleep 4
tap "Meus projetos"
visible "Teste IA Musical"
tap "Teste IA Musical"
tap "Abrir e continuar"
sleep 6
tap "Tom Ideal"
# Exercitar duração máxima (18s), com múltiplas inferências e transições.
tap "Duração de isolamento: 6 s"
tap "Duração de isolamento: 12 s"
visible "Duração de isolamento: 18 s"
# O botão "Cancelar isolamento" só existe DURANTE a inferência;
# antes de iniciar o motor, validar o botão de início (não o de cancelamento).
visible "Isolar voz com IA"
adb logcat -c || true
tap "Isolar voz com IA"
echo "Executando separação neural no Android sobre gravação vocal de referência…"
SUCCESS=0
for attempt in $(seq 1 75); do
  readui
  if grep -qE 'Voz estimada por separação neural|A voz foi extraída, mas' "$OUT/current.xml"; then
    echo "PASSOU: modelo ONNX executado e arquivo vocal temporário processado."
    SUCCESS=1
    break
  fi
  if grep -q 'Separação vocal indisponível' "$OUT/current.xml"; then
    echo "FALHA: erro ao executar o modelo neural." >&2
    grep -o 'Separação vocal indisponível[^<]*' "$OUT/current.xml" | head -c 800 || true
    exit 1
  fi
  sleep 3
done
if [ "$SUCCESS" -ne 1 ]; then
  echo "FALHA: tempo de inferência excedido, ou resultado inacessível." >&2
  exit 1
fi
echo "PASSOU: teste de inferência do modelo ONNX em emulador Android."
# O trecho isolado dura 18 s. Pausar imediatamente, pois
# uiautomator dump + scroll pode consumir toda a reprodução.
tap "Ouvir voz isolada"
tap "Pausar prévia vocal"
visible "Continuar prévia vocal"
echo "PASSOU: prévia vocal temporária reproduziu e pausou via AudioTrack."
# O áudio temporário deve ser transformado em WAV ANTES de abrir o
# seletor Android. O onStop da Activity limpa a prévia, mas não o WAV.
tap "Salvar voz isolada"
sleep 3
DOCUMENT_ACTIVITY="$(adb shell dumpsys activity activities | grep -Ei 'mResumedActivity|topResumedActivity|Resumed: ActivityRecord' | tail -n 3 || true)"
echo "Tela do seletor de documentos: $DOCUMENT_ACTIVITY"
if ! echo "$DOCUMENT_ACTIVITY" | grep -Eiq 'documentsui|files|documents'; then
  readui
  if ! grep -Eiq 'save|salvar|downloads|recent|documents' "$OUT/current.xml"; then
    echo "FALHA: seletor de arquivos Android não abriu." >&2
    exit 1
  fi
fi
STAGE=$(adb shell run-as "$PKG" ls cache | tr -d '\r' | grep -E '^pitch_voice_export_.*\.wav$' | head -n1)
if [ -z "$STAGE" ]; then
  echo "FALHA: exportação não preparou WAV antes do seletor." >&2
  exit 1
fi
adb exec-out run-as "$PKG" cat "cache/$STAGE" > "$OUT/staged_voice.wav"
python3 - "$OUT/staged_voice.wav" <<'PY'
import sys,wave,os
path=sys.argv[1]
with wave.open(path,'rb') as w:
    rate=w.getframerate()
    channels=w.getnchannels()
    frames=w.getnframes()
    bits=w.getsampwidth()*8
    assert rate==44100 and channels==1 and bits==16,(rate,channels,bits)
    assert 17.9<frames/rate<=18.0,frames/rate
    raw=w.readframes(frames)
    assert any(b!=0 for b in raw),"WAV vocal silencioso"
print("PASSOU: WAV gerado é PCM16 mono",rate,"Hz,",frames,"frames,",
      os.path.getsize(path),"bytes")
PY
# Validar o caminho positivo de gravação, não apenas a geração e cancelamento.
# O Android DocumentsUI costuma iniciar em Recentes, onde não se pode salvar.
readui
if grep -qE '(text|content-desc)="Downloads"' "$OUT/current.xml"; then
  tap "Downloads"
fi
readui
# Evita selecionar sugestões de nome ou tocar em botões fora da janela SAF.
SAVE_POS=$(python3 - "$OUT/current.xml" <<'PY'
import sys,re
from xml.etree import ElementTree as ET
nodes=list(ET.parse(sys.argv[1]).getroot().iter("node"))
for n in nodes:
    value=(n.get("text","") or n.get("content-desc","")).strip().casefold()
    if value not in ("save","salvar"):
        continue
    if n.get("enabled")=="false":
        continue
    bounds=list(map(int,re.findall(r"\d+",n.get("bounds",""))))
    if len(bounds)==4:
        a,b,c,d=bounds
        print((a+c)//2,(b+d)//2)
        raise SystemExit(0)
raise SystemExit("FALHA: botão Salvar do seletor SAF não está habilitado")
PY
)
read -r SAVE_X SAVE_Y <<<"$SAVE_POS"
echo "Confirmando salvamento SAF em $SAVE_X,$SAVE_Y"
adb shell input tap "$SAVE_X" "$SAVE_Y"
# Status fica dentro de ScrollView e pode não aparecer no dump quando
# o Android devolve o foco após o seletor de arquivos. Em vez de depender
# do texto visível, validar o arquivo salvo (bytes abaixo) e o staging limpo.
SAVE_OK=0
for attempt in $(seq 1 20); do
  SAVED_REMOTE=$(adb shell find /sdcard/Download /sdcard/Documents /sdcard/Music -maxdepth 3 -type f -name 'BEATflow_Voz_Isolada*.wav' 2>/dev/null | tr -d '\r' | head -n1 || true)
  if [ -n "$SAVED_REMOTE" ] &&
     ! adb shell run-as "$PKG" ls cache | grep -q "$STAGE"; then
    SAVE_OK=1
    break
  fi
  sleep 1
done
if [ "$SAVE_OK" -ne 1 ]; then
  echo "FALHA: ContentResolver não gerou o WAV completo nem limpou o staging." >&2
  readui
  grep -Eo 'text="[^"]{0,140}"' "$OUT/current.xml" | tail -n 25 || true
  exit 1
fi
readui
if ! grep -q 'Voz isolada salva em WAV no local escolhido' "$OUT/current.xml"; then
  echo "AVISO: mensagem de conclusão fora da viewport; arquivo WAV salvo confirmado no Android."
fi
if adb shell run-as "$PKG" ls cache | grep -q "$STAGE"; then
  echo "FALHA: arquivo WAV de staging não foi apagado após salvar." >&2
  exit 1
fi
echo "PASSOU: salvamento externo SAF confirmado e WAV temporário descartado."
# No provedor de documentos local do emulador, validar também os bytes do arquivo.
SAVED_REMOTE=$(adb shell find /sdcard/Download /sdcard/Documents /sdcard/Music -maxdepth 3 -type f -name 'BEATflow_Voz_Isolada*.wav' 2>/dev/null | tr -d '\r' | head -n1 || true)
if [ -n "$SAVED_REMOTE" ]; then
  adb pull "$SAVED_REMOTE" "$OUT/confirmed_voice.wav" >/dev/null
  python3 - "$OUT/staged_voice.wav" "$OUT/confirmed_voice.wav" <<'PY'
from pathlib import Path
import hashlib,sys,wave
prepared,final=map(Path,sys.argv[1:])
assert final.read_bytes()==prepared.read_bytes(),"Arquivo salvo difere do WAV preparado"
with wave.open(str(final),"rb") as audio:
    assert audio.getframerate()==44100 and audio.getnchannels()==1
print("PASSOU: WAV salvo no destino SAF é byte a byte igual ao original temporário.")
PY
else
  echo "AVISO: provedor SAF confirmou gravação, mas não expôs caminho direto ao adb para comparação."
fi


# Regressão end-to-end: MP3 no editor a partir do projeto carregado,
# selecionando destino real via SAF e decodificando o arquivo final.
adb shell input keyevent 4
sleep 3
visible "BEAT flow"
# O cartão FINALIZAR fica no fim do editor Material Expressive:
# a rolagem deve atingir seu conteúdo antes de buscar o botão MP3.
for down in 1 2 3 4 5 6; do
  adb shell input swipe 520 1800 520 550 220
done
visible "MP3 (até 320 kbps)"
tap "MP3 (até 320 kbps)"
sleep 3
readui
if grep -qE '(text|content-desc)="Downloads"' "$OUT/current.xml"; then
  tap "Downloads"
fi
readui
MP3_SAVE_POS=$(python3 - "$OUT/current.xml" <<'PY'
import re,sys
from xml.etree import ElementTree as ET
for node in ET.parse(sys.argv[1]).getroot().iter("node"):
    label=(node.get("text","") or node.get("content-desc","")).strip().casefold()
    if label not in ("save","salvar") or node.get("enabled")=="false":
        continue
    coords=list(map(int,re.findall(r"\d+",node.get("bounds",""))))
    if len(coords)==4:
        a,b,c,d=coords
        print((a+c)//2,(b+d)//2)
        raise SystemExit(0)
raise SystemExit("FALHA: seletor MP3 não mostrou Salvar habilitado")
PY
)
read -r MP3_X MP3_Y <<<"$MP3_SAVE_POS"
adb shell input tap "$MP3_X" "$MP3_Y"
MP3_DONE=0
for attempt in $(seq 1 45); do
  readui
  if grep -q 'Exportação concluída' "$OUT/current.xml"; then
    MP3_DONE=1; break
  fi
  if grep -q 'Falha na exportação' "$OUT/current.xml"; then
    echo "FALHA: exportador MP3 apresentou erro." >&2
    grep -o 'Falha na exportação[^<]*' "$OUT/current.xml" | head -c 500 || true
    exit 1
  fi
  sleep 2
done
test "$MP3_DONE" = 1 || { echo "FALHA: MP3 não concluiu." >&2; exit 1; }
MP3_REMOTE=$(adb shell find /sdcard/Download /sdcard/Documents /sdcard/Music \
  -maxdepth 3 -type f -name '*_processado.mp3' 2>/dev/null | tr -d '\r' | head -n1 || true)
test -n "$MP3_REMOTE" || { echo "FALHA: MP3 exportado não localizado no Android." >&2; exit 1; }
adb pull "$MP3_REMOTE" "$OUT/confirmed_export.mp3" >/dev/null
python3 - "$OUT/confirmed_export.mp3" <<'PY'
import sys,shutil,subprocess,json
from pathlib import Path
raw=Path(sys.argv[1]).read_bytes()
assert len(raw)>100000, "MP3 exportado está vazio ou truncado"
pos=0
if raw.startswith(b"ID3"):
    assert len(raw)>=10
    tag=(raw[6]<<21)|(raw[7]<<14)|(raw[8]<<7)|raw[9]
    pos=10+tag
mpeg_frames=0
br_set=set()
rates=set()
modes=set()
duration=0.0
bitrates=[0,32,40,48,56,64,80,96,112,128,160,192,224,256,320,0]
while pos+4<=len(raw):
    h=int.from_bytes(raw[pos:pos+4],"big")
    assert (h>>21)&2047==2047, f"Frame MP3 inválido no byte {pos}"
    version=(h>>19)&3
    layer=(h>>17)&3
    br_idx=(h>>12)&15
    sr_idx=(h>>10)&3
    assert version==3 and layer==1 and 1<=br_idx<=14 and sr_idx<=2,hex(h)
    rate=(44100,48000,32000)[sr_idx]
    bitrate=bitrates[br_idx]
    channels=1 if ((h>>6)&3)==3 else 2
    length=144000*bitrate//rate+((h>>9)&1)
    assert pos+length<=len(raw), "MP3 termina no meio de um frame"
    br_set.add(bitrate);rates.add(rate);modes.add(channels)
    duration+=1152.0/rate
    mpeg_frames+=1
    pos+=length
assert pos==len(raw) or (len(raw)-pos==128 and raw[pos:pos+3]==b"TAG"),"Resíduo inválido no MP3"
assert mpeg_frames>=200,mpeg_frames
assert rates=={44100} and modes=={2} and br_set=={320},(rates,modes,br_set)
assert 20.7<=duration<=21.8,duration
print(f"PASSOU: MP3 SAF salvo, {mpeg_frames} quadros MPEG íntegros, "
      f"44,1 kHz, estéreo, 320kbps, duração {duration:.3f}s.")
# FFmpeg é opcional: nem todas as imagens Ubuntu do Actions o incluem.
# Quando disponível, decodificar todo o arquivo também.
if shutil.which("ffprobe") and shutil.which("ffmpeg"):
    probe=subprocess.run(["ffprobe","-v","error","-show_entries",
        "stream=codec_name,sample_rate,channels,bit_rate:format=duration",
        "-of","json",sys.argv[1]],capture_output=True,text=True,check=True)
    meta=json.loads(probe.stdout)
    audio=[s for s in meta.get("streams",[]) if s.get("codec_name")=="mp3"]
    assert len(audio)==1,meta
    assert int(audio[0]["sample_rate"])==44100
    subprocess.run(["ffmpeg","-v","error","-i",sys.argv[1],"-f","null","-"],
        check=True,capture_output=True)
    print("PASSOU: decodificação completa do MP3 pelo FFmpeg.")
else:
    print("AVISO: FFmpeg ausente no runner; quadros validados integralmente sem dependência externa.")
PY

# Provar que o cancelamento da separação longa interrompe o trabalho,
# libera botões e exclui os arquivos PCM temporários.
echo "Exercitando cancelamento explícito da separação vocal longa…"
for to_top in 1 2 3 4 5 6; do
  adb shell input swipe 520 500 520 1650 230
done
tap "Tom Ideal"
tap "Duração de isolamento: 6 s"
tap "Duração de isolamento: 12 s"
visible "Duração de isolamento: 18 s"
tap "Isolar voz com IA"
tap "Cancelar isolamento"
CANCEL_OK=0
for attempt in $(seq 1 40); do
  readui
  if grep -q 'Isolamento vocal cancelado' "$OUT/current.xml"; then
    CANCEL_OK=1
    break
  fi
  sleep 2
done
test "$CANCEL_OK" = 1 || {
  echo "FALHA: cancelamento vocal não finalizou." >&2
  exit 1
}
if adb shell run-as "$PKG" ls cache | grep -qE '^pitch_vocal_stem_.*\.f32$'; then
  echo "FALHA: áudio PCM temporário permaneceu após cancelar isolamento." >&2
  exit 1
fi
echo "PASSOU: cancelamento de IA 18s sem áudio temporário residual."
adb shell dumpsys meminfo "$PKG" | grep -Ei 'TOTAL PSS|TOTAL RSS|TOTAL SWAP' | tail -n 3 || true

# Novo recurso: playback real da música inteira acima de 18 segundos.
adb shell input keyevent 4
sleep 2
for to_top in 1 2 3 4 5 6; do
  adb shell input swipe 520 500 520 1650 220
done
visible "BEAT flow"
tap "Separação com IA"
visible "Separação com IA"
visible "O que você quer separar?"
visible "Música inteira"
tap "Processar música inteira"
DONE_PLAYBACK=0
for attempt in $(seq 1 90); do
  readui
  NAME=$(adb shell run-as "$PKG" ls cache | grep -E '^beat_playback_.*\.f32$' | head -n 1 || true)
  if [ -n "$NAME" ]; then
    BYTES=$(adb shell run-as "$PKG" stat -c%s "cache/$NAME" 2>/dev/null | tr -d '\r' || echo 0)
    # O indicador fica em ScrollView, então a confirmação vem do tamanho
    # efetivo do PCM temporário, checado novamente após sair do loop.
    if [ "${BYTES:-0}" -ge 7373520 ]; then
      DONE_PLAYBACK=1
      break
    fi
  fi
  sleep 3
done
test "$DONE_PLAYBACK" -eq 1 || {
  echo "FALHA: playback da música inteira não concluiu." >&2
  exit 1
}
PLAYBACK=$(adb shell run-as "$PKG" ls cache | grep -E '^beat_playback_.*\.f32$' | head -n 1)
adb exec-out run-as "$PKG" cat "cache/$PLAYBACK" > "$OUT/whole_playback.f32"
python3 - "$OUT/whole_playback.f32" <<'PY'
import os,sys,struct
length=os.stat(sys.argv[1]).st_size
assert length % 8 == 0,length
frames=length//8
duration=frames/44100
assert 20.9 < duration < 21.2, (frames,duration)
with open(sys.argv[1],'rb') as f:
    head=f.read(8192)
floats=struct.unpack("<%df"%(len(head)//4),head)
assert any(abs(x)>0.00001 for x in floats),"Playback gerado silencioso"
print("PASSOU: playback completo PCM float estéreo, %.3f s (%d frames)"%(duration,frames))
PY
# Checagem de QUALIDADE: a voz estimada precisa coincidir temporalmente com
# a mistura. A v1.12.9 passava em durações e falhava em áudio (2048 amostras).
python3 - "$OUT/stems_test.f32" "$OUT/whole_playback.f32" <<'PY'
import array,sys,math
def load(path):
    values=array.array("f")
    with open(path,"rb") as f:values.frombytes(f.read())
    if sys.byteorder!="little":values.byteswap()
    assert len(values)%2==0
    return values
source=load(sys.argv[1]); playback=load(sys.argv[2])
assert len(source)==len(playback)
frames=len(source)//2
# Música real de teste: 4s..17s; evitar silêncio/bordas da inferência.
start=4*44100; end=min(frames-4096,17*44100)
assert end>start
stride=16
s0=sDelayed=srcEnergy=removedEnergy=0.0
for t in range(start,end,stride):
    orig=(source[2*t]+source[2*t+1])*0.5
    beat=(playback[2*t]+playback[2*t+1])*0.5
    past=(source[2*(t-2048)]+source[2*(t-2048)+1])*0.5
    removed=orig-beat
    s0+=removed*orig
    sDelayed+=removed*past
    srcEnergy+=orig*orig
    removedEnergy+=removed*removed
normalizer=math.sqrt(srcEnergy*removedEnergy)+1e-12
c0=s0/normalizer
cDelayed=sDelayed/normalizer
print(f"QA sincronismo vocal: corr_sem_atraso={c0:.4f}; corr_atrasada_2048={cDelayed:.4f}")
assert removedEnergy>1e-5,"Motor devolveu vocal vazio."
assert c0>cDelayed+0.08,(
    f"FALHA: voz extraída continua atrasada 2048 amostras ({c0:.3f} vs {cDelayed:.3f})."
)
print("PASSOU: vazamento vocal não apresenta atraso de 2048 amostras.")
PY
# Resultados abaixo da dobra do aparelho: rolar até os botões reais.
for down in 1 2 3 4; do
  adb shell input swipe 520 1800 520 650 220
done
visible "Salvar WAV"
visible "Salvar MP3"
echo "PASSOU: playback da faixa inteira com exportação WAV/MP3 disponível."
adb shell dumpsys meminfo "$PKG" | grep -Ei 'TOTAL PSS|TOTAL RSS|TOTAL SWAP' | tail -n 3 || true

# Testar exportação real do NOVO playback, não apenas o botão disponível.
for FORMAT in WAV MP3; do
  tap "Salvar $FORMAT"
  sleep 3
  readui
  if grep -qE '(text|content-desc)="Downloads"' "$OUT/current.xml"; then tap "Downloads"; fi
  readui
  SAVE_POS=$(python3 - "$OUT/current.xml" <<'PY'
import re,sys
from xml.etree import ElementTree as ET
for e in ET.parse(sys.argv[1]).getroot().iter("node"):
    t=(e.get("text","")+" "+e.get("content-desc","")).strip().lower()
    if t not in ("salvar","save") or e.get("enabled")=="false": continue
    p=list(map(int,re.findall(r"\d+",e.get("bounds",""))))
    if len(p)==4:
        print((p[0]+p[2])//2,(p[1]+p[3])//2);raise SystemExit(0)
raise SystemExit("FALHA: seletor não exibiu Salvar")
PY
)
  read -r SX SY <<<"$SAVE_POS"
  adb shell input tap "$SX" "$SY"
  case "$FORMAT" in WAV) EXT=wav; MINBYTES=3700000;; MP3) EXT=mp3; MINBYTES=700000;; esac
  FINISHED=0
  for attempt in $(seq 1 45); do
    TARGET=$(adb shell find /sdcard/Download /sdcard/Documents /sdcard/Music -maxdepth 3 -type f -name "BEATflow_Playback*.$EXT" 2>/dev/null | tr -d '\r' | head -n1 || true)
    if [ -n "$TARGET" ]; then
      BYTES=$(adb shell stat -c%s "$TARGET" 2>/dev/null | tr -d '\r' || echo 0)
      if [ "$BYTES" -ge "$MINBYTES" ]; then FINISHED=1; break; fi
    fi
    sleep 2
  done
  test "$FINISHED" = 1 || { echo "FALHA: exportação nova $FORMAT não concluiu.";exit 1; }
  adb pull "$TARGET" "$OUT/playback_export.$EXT" >/dev/null
  if [ "$FORMAT" = WAV ]; then
    python3 - "$OUT/playback_export.wav" <<'PY'
import sys,wave
with wave.open(sys.argv[1],"rb") as w:
    assert w.getnchannels()==2 and w.getframerate()==44100 and w.getsampwidth()==2
    assert abs(w.getnframes()-926100)<4410,w.getnframes()
    assert any(w.readframes(4096)),"WAV sem sinal"
print("PASSOU: playback novo WAV estéreo, 21 segundos, exportação SAF real.")
PY
  else
    python3 - "$OUT/playback_export.mp3" <<'PY'
from pathlib import Path
import sys,shutil,subprocess
b=Path(sys.argv[1]).read_bytes()
assert len(b)>700000,len(b)
assert b'\xff\xfb' in b[:4096],"MP3 sem sincronização"
if shutil.which("ffprobe"):
    raw=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
      "-of","default=noprint_wrappers=1:nokey=1",sys.argv[1]],
      check=True,capture_output=True,text=True).stdout.strip()
    assert 20.7<float(raw)<21.7,raw
print("PASSOU: playback novo MP3 320 kbps exportado via SAF.")
PY
  fi
done
# Teste real de 3 minutos usando a mesma amostra vocal local do projeto;
# a faixa é replicada, sem baixar ou extrair áudio de YouTube.
python3 - "$OUT" <<'PY'
import json,sys,time
from pathlib import Path
p=Path(sys.argv[1])
src=(p/"stems_test.f32").read_bytes()
remaining=180*44100*8
with (p/"stems_180.f32").open("wb") as w:
    while remaining:
        buf=src[:remaining];w.write(buf);remaining-=len(buf)
meta=json.loads((p/"stems_test.json").read_text())
meta.update(title="Teste Playback 180s",frames=180*44100,
            updatedAt=int(time.time()*1000))
(p/"stems_180.json").write_text(json.dumps(meta))
assert (p/"stems_180.f32").stat().st_size==63504000
print("FAIXA 180 SEGUNDOS GERADA")
PY
ID_LONG="435e4567-e89b-12d3-a456-426614174112"
adb push "$OUT/stems_180.f32" /data/local/tmp/beatflow-180.f32 >/dev/null
adb push "$OUT/stems_180.json" /data/local/tmp/beatflow-180.json >/dev/null
adb shell run-as "$PKG" mkdir -p "files/saved_audio_projects/$ID_LONG"
adb shell run-as "$PKG" cp /data/local/tmp/beatflow-180.f32 "files/saved_audio_projects/$ID_LONG/original.f32"
adb shell run-as "$PKG" cp /data/local/tmp/beatflow-180.json "files/saved_audio_projects/$ID_LONG/project.json"
adb shell am force-stop "$PKG"
adb shell am start -W -n "$PKG/br.com.timachado.pitchstudio.MainActivity"
sleep 5
tap "Meus projetos"
tap "Teste Playback 180s"
tap "Abrir e continuar"
sleep 4
tap "Separação com IA"
visible "Música inteira"
tap "Processar música inteira"
# Auditoria independente: não confiar no texto da UI sem os bytes reais.
EXPECTED_180=$((180*44100*2*4))
COMPLETE=0
TESTFILE=""
COPIED=0
probe_cache() {
  local candidate bytes
  while IFS= read -r candidate; do
    candidate="${candidate//$'\r'/}"
    case "$candidate" in beat_playback_*.f32) ;; *) continue ;; esac
    bytes=$(adb shell run-as "$PKG" stat -c%s "cache/$candidate" 2>/dev/null | tr -cd '0-9' || true)
    [[ "$bytes" =~ ^[0-9]+$ ]] || bytes=0
    if [ "$bytes" -gt "${LARGEST:-0}" ]; then LARGEST="$bytes"; fi
    if [ "$bytes" -gt "$EXPECTED_180" ]; then echo "FALHA: playback maior que 180s ($bytes)" >&2; exit 1; fi
    if [ "$bytes" -eq "$EXPECTED_180" ]; then TESTFILE="$candidate"; return 0; fi
  done < <(adb shell run-as "$PKG" ls -1 cache 2>/dev/null | tr -d '\r' || true)
  # Alguns emuladores retornam tamanho correto em ls -l mas não em stat.
  # Aceita apenas o candidato cujo arquivo TRANSFERIDO for validado no host.
  while IFS= read -r row; do
    candidate="${row##* }"
    case "$candidate" in beat_playback_*.f32) ;; *) continue ;; esac
    bytes=$(printf '%s\n' "$row" | awk '{print $5}')
    if [ "${bytes:-0}" -eq "$EXPECTED_180" ] 2>/dev/null; then
      TESTFILE="$candidate"
      return 0
    fi
  done < <(adb shell run-as "$PKG" ls -l cache 2>/dev/null | tr -d '\r' || true)
  return 1
}
for attempt in $(seq 1 300); do
  LARGEST=0
  if probe_cache; then COMPLETE=1;break;fi
  if (( attempt % 12 == 0 )); then
    echo "Processamento 180s: verificação $attempt/300, maior arquivo ${LARGEST:-0}/$EXPECTED_180 bytes."
    adb shell dumpsys meminfo "$PKG" | grep -Ei "TOTAL PSS|TOTAL RSS" | tail -n 2 || true
    readui
    if grep -q 'Falha:' "$OUT/current.xml"; then
      echo "FALHA: aplicativo mostrou erro durante o processamento." >&2
      grep -Eo 'text="[^"]{0,170}"' "$OUT/current.xml" | tail -n 25 || true
      exit 1
    fi
    if grep -qE 'Processado: 180[.,]0 s' "$OUT/current.xml"; then
      echo "UI terminou 180s: conferindo cache via leitura binária (sem aceitar só o status)."
      while IFS= read -r candidate; do
        candidate="${candidate//$'\r'/}"
        case "$candidate" in beat_playback_*.f32) ;; *) continue ;; esac
        tmp="$OUT/probe-180.f32"
        if adb exec-out run-as "$PKG" cat "cache/$candidate" > "$tmp" 2>/dev/null;then
          bytes=$(stat -c%s "$tmp" 2>/dev/null || echo 0)
          echo "Auditoria binária: $candidate = $bytes bytes"
          if [ "$bytes" -eq "$EXPECTED_180" ]; then
            mv "$tmp" "$OUT/playback_180.f32"
            TESTFILE="$candidate"
            COPIED=1
            COMPLETE=1
            break
          fi
        fi
        rm -f "$tmp"
      done < <(adb shell run-as "$PKG" ls -1 cache 2>/dev/null | tr -d '\r' || true)
      if [ "$COMPLETE" -eq 1 ]; then break; fi
    fi
  fi
  sleep 3
done
if [ "$COMPLETE" != 1 ]; then
  echo "FALHA: nenhum arquivo PCM integral de 180s foi comprovado." >&2
  adb shell run-as "$PKG" ls -l cache || true
  adb shell input swipe 520 1800 520 600 250
  readui
  grep -Eo 'text="[^"]{0,180}"' "$OUT/current.xml" | tail -n 25 || true
  adb logcat -d -s BEATflow-Separation:E AndroidRuntime:E | tail -n 100 || true
  exit 1
fi
if [ "$COPIED" -ne 1 ]; then
  adb exec-out run-as "$PKG" cat "cache/$TESTFILE" > "$OUT/playback_180.f32"
fi
test "$(stat -c%s "$OUT/playback_180.f32")" -eq "$EXPECTED_180" || {
  echo "FALHA: arquivo transferido não tem exatamente 180s." >&2
  exit 1
}
python3 - "$OUT/playback_180.f32" <<'PY'
import os,sys,struct
n=os.stat(sys.argv[1]).st_size
assert n==180*44100*8,n
with open(sys.argv[1],"rb") as f:v=struct.unpack("<200f",f.read(800))
assert any(abs(x)>0.0001 for x in v),"Resultado instrumental silencioso"
print("PASSOU: separação integral de 180 segundos, estéreo e sem truncamento.")
PY
adb shell dumpsys meminfo "$PKG" | grep -Ei 'TOTAL PSS|TOTAL RSS|TOTAL SWAP' | tail -n 3 || true

if adb logcat -d -b crash -t 1500 | grep -E 'FATAL EXCEPTION|Process: br.com.timachado.beatflow.waveqa'; then
 echo "FALHA: crash identificado no logcat" >&2
 exit 1
fi

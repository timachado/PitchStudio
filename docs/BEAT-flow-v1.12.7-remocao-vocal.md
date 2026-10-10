# BEAT flow v1.12.7 — foco em instrumental sem voz

**Problema relatado:** a separação `Voz` funciona, mas o modo `Playback` mantém voz audível em uma música de 209,5 segundos. Na captura enviada, **Voz** está visualmente selecionado; verificar o modo `Playback` na mesma faixa antes de avaliar a saída.

## Correção incremental
- O sistema continua usando o mesmo MDX-Net e preserva o áudio `Voz` calculado antes.
- Antes, o instrumental era apenas `mixagem - stem_vocal` (ganho fixo 1,0). Quando o modelo subestima uma voz, parte dela permanece.
- Agora o instrumental usa subtração vocal **adaptativa e limitada**: a cada 16.384 frames, mede a correlação entre a mistura e o stem vocal e ajusta o ganho de remoção entre 1,0 e 1,6, suavizando cada amostra para evitar estalos.
- Preserva a imagem estéreo usando um ganho comum aos canais, evita aumentar a voz se a correlação é insuficiente e impede NaN/inf nos samples.
- Não remove nem muda o modo `Voz`, não altera download, player, UI, autosave, comparação A/B/C, timeline ou exportação.
- Nenhuma configuração existente ou áudio original é modificado; os stems precisam ser regenerados para usar a melhoria.

## Verificação
- Testes de unidade `PlaybackVocalReducerTest.kt`: reduzir vazamento de voz atenuada em mistura sintética, respeitar ausência de voz, ganho limitado e finitude.
- QA no emulador e exportação WAV/MP3 são regressões; teste físico com a **mesma música relatada** ainda é exigido.
- Corrigida verificação do cache PCM de 180 s no CI para usar tamanho obtido por `ls -l` quando o `stat` via ADB é inconsistente. A saída é transferida e auditada por bytes antes de passar.
- Como qualquer separador por IA, esta melhora **não garante remoção vocal perfeita** em todos os arranjos; ecos, reverberações, backing vocals e sobreposição espectral podem exigir outro modelo de separação.

**Compatibilidade:** v1.12.7 (continuação da v1.12.6, branch atual), distribuição APK independente.

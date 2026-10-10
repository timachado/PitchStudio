# BEAT flow v1.12.6 — Linha do Tempo Inteligente (1ª etapa)

Base aprovada: v1.12.5, mantendo identidade BEAT flow, Material 3 Expressive, A/B/C, biblioteca, Tom Ideal, motor MDX-Net, importação, pesquisa, prévia e opção existente de baixar músicas.

## Alterações verificáveis
- Card **AGORA NO ESTÚDIO**: seção discreta **Linha do Tempo Inteligente**, com **Marcar trecho** e **Ver trechos**.
- Na posição atual do player, marcar **Introdução / Verso / Refrão / Ponte / Solo / Final** sem editar samples.
- Marcadores aparecem sobre o waveform existente; lista ordenada oferece **Ir para o trecho / Repetir este trecho / Renomear / Excluir marcação**.
- A repetição utiliza o mesmo loop A–B anterior, limitado pelo início do próximo trecho, ou fim da música.
- Até 64 marcações por faixa; validação de posição, rótulo e remoção de duplicatas próximas.
- Marcadores persistidos em `songSections` no JSON de cada projeto salvo, via `AtomicFile`, mantendo compatibilidade com schema 1. Ao reabrir um projeto, as marcas retornam. Projetos ainda não salvos guardam marcadores em memória; após o primeiro salvamento eles também são persistidos.
- Arquivo PCM original, exportações WAV/MP3 e motor de IA não foram modificados.

## Limites explícitos
- **Identificação manual**: esta etapa não afirma identificar automaticamente refrões nem detectar acordes/BPM. Automação musical e edição segmentada ficam para fases seguintes.
- Testar marcações e loops com uma música local; persistência após fechamento/abertura; regressão completa no Android 15; testes em Motorola g34 5G ainda necessários.
- Novo APK de QA não é lançamento de produção até finalizar a CI e homologação física.

## Testes
- `TimelineSectionsTest` cobre ordenação, posições inválidas, duplicatas próximas, limite de 64 e limites de trecho.
- `.pitchstudio/v1126/smoke-timeline.sh` executa smoke anterior (IA 18/180 s, exportação WAV/MP3, YouTube, A/B/C), adiciona marcação de introdução, confere bytes reais do JSON e recarrega o mesmo projeto.
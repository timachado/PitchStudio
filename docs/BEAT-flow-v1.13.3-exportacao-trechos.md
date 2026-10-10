# BEAT flow v1.13.3 — exportação WAV/MP3 com ajustes por trecho

Objetivo: completar a renderização por seção da Linha do Tempo, sem alterar o processamento de voz e instrumental aprovado, YouTube, downloads, Tom Ideal, comparação A/B/C, biblioteca ou os botões de exportação anteriores.

## Implementação
- Adicionados **WAV por trechos** e **MP3 por trechos** imediatamente abaixo dos botões WAV/MP3 normais, que continuam idênticos.
- O exportador lê **somente o PCM original**, segmenta nas marcações do usuário e processa cada seção pelo mesmo DspEngine (qualidade DSP global).
- Seções com ajuste aplicam tom (±12 semitons) e velocidade (0,5x–2x) locais; seções sem ajuste usam a configuração global existente. Um crossfade de 12ms entre segmentos ameniza estalos.
- Faz renderização em arquivos temporários por segmento (sem manter a música inteira em RAM), combina PCM estéreo e disponibiliza salvar WAV 24-bit ou MP3 via SAF. Calcula frames/peak finais, limpa temporários e mantém o original intacto.
- Só habilita o fluxo quando existem configurações por trecho; mantém os ajustes dos projetos na biblioteca como já implementado.
- A renderização alterará a duração total se algum trecho tiver velocidade diferente; não é erro de truncamento.
- Teste Kotlin local executou dois trechos de música sintética: resultado de 11.904 frames, original 16.000 frames, sem perda/corrupção do original e sem arquivos temporários residuais.
- Incluído `SectionDspRendererTest` no Gradle; compilação e QA Android são etapas separadas antes da aprovação.

## Riscos e validação
- Processar muitas seções pode demorar, gerar arquivos grandes e consumir bateria no Motorola g34 5G; verificar 3/5/10 minutos e armazenamento baixo.
- Auditar transições sem clique, amostras finitas, sinal estéreo íntegro, WAV/MP3 íntegros, Cancelar no seletor SAF, fechamento do app durante exportação.
- O teste da v1.13.2 parava após processamento de 180s e A/B/C ao não encontrar o tipo Introdução; adicionada validação/reabertura explícita do diálogo sem mascarar erro de app.
- NUNCA substituir os antigos botões ou remover os fluxos YouTube/download, MP3 e Voz.

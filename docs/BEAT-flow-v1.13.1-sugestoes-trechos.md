# BEAT flow v1.13.1 — Linha do Tempo Inteligente: sugestões automáticas

**Escopo aprovado:** avançar etapa seguinte sem alterar Playback, separação de voz, YouTube/download, Tom Ideal, projetos, A/B/C ou identidade Material 3 Expressive. Pendência do Playback #5 encerrada por aprovação expressa do usuário.

## Funcionalidades
- O cartão **Linha do Tempo Inteligente** ganha somente o botão **Sugerir trechos automaticamente**; botões de marcação e visualização existentes permanecem.
- Analisa áudio PCM original OFFLINE em blocos, medindo intensidade RMS e variações de energia/atividade; sem enviar áudio à nuvem, sem sobrecarregar a RAM e sem modificar samples.
- Propõe até 12 **possíveis transições** com tempo correspondente, sem afirmar que detecta de fato verso/refrão/ponte.
- O usuário toca um ponto, navega à posição e escolhe **Introdução, Verso, Refrão, Ponte, Solo ou Final** para aceitar uma marcação.
- Não altera marcações manuais já existentes e não persiste sugestões descartadas. Se o projeto foi salvo, a confirmação usa o JSON/AtomicFile já implementado.
- Cancelamento indireto ao abrir outra música e confirmação de leitura válida, limite de duração e PCM completo.

## Verificações
- Testes Kotlin JUnit para mudanças conhecidas em 20/42 s, ordenação, respeito a marcações existentes, faixas curtas/estáveis e cancelamento.
- Testes locais com compilador Kotlin 1.9: transições detectadas em 20.0, 42.0 e 56.0 s, 6 verificações aprovadas. A CI executa testDebugUnitTest e assembleDebug.
- A identificação automática de estrutura real da música (verso ou refrão) com modelo especializado continua como evolução futura; o algoritmo de mudança de energia não deve ser chamado detector de refrão.

**Distribuição:** APK Android independente; homologação no dispositivo físico ainda pendente.

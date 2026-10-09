# BEAT flow v1.13.6 — Inteligência Musical I: BPM e metrônomo

- Analisar BPM estima o pulso entre 60 e 200 BPM a partir do PCM original de uma música da Biblioteca Inteligente. Usa até 75 segundos, processamento local assíncrono e memória limitada. Não precisa internet.
- Estimativa aproximada por ataques de energia e autocorrelação; não garante precisão em gravações ao vivo, ritmos sincopados ou com mudanças de andamento.
- Tap BPM com ao menos três toques; controles +1 e -1 BPM; opção manual disponível mesmo sem música selecionada.
- Salvar BPM somente após confirmação explícita; armazena mapa de tempos por ID de música em stage_setlists.json, no esquema 1 compatível com projetos/repertórios antigos.
- Metrônomo utiliza som audível no stream de música do Android e relógio monotônico. Exclusivo do Modo Ensaio. Para ao mudar de faixa, entrar no Modo Palco, sair do app e encerrar Activity.
- O BPM da música NÃO muda automaticamente a velocidade do playback nem afeta exportações WAV/MP3.
- Testes locais JVM: 75, 90, 100, 120 e 160 BPM sintéticos detectados com tolerância de 3 BPM; silêncio retorna sem detecção; Tap e intervalos testados.
- Faixa real de 45 segundos produziu estimativa, porém sem verdade de referência validada: confirmá-la pelo ouvido. Não afirmar que o algoritmo identifica acordes nesta versão.
- JUnit StageTempoAnalyzerTest integra a compilação Android; testes físicos de latência e som no Motorola g34 5G ainda pendentes.
- Código de Playback aprovado, Voz, YouTube com pesquisa/prévia/download/salvar arquivo, Tom Ideal, biblioteca, A/B/C e exportações permanece preservado.

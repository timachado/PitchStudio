# BEAT flow v1.12.9 — Playback: segunda inferência de remoção vocal

**Motivo:** o usuário confirmou vocal audível no Playback mesmo após v1.12.8. Uma soma/subtração com ganho maior não assegura remoção e pode danificar instrumentos.

## Motor v1.12.9
- Na saída instrumental (PLAYBACK ou parte instrumental de AMBOS), o motor MDX-Net gera a separação primária e usa a **mesma sessão ONNX** para inspecionar o residual em uma segunda inferência.
- A segunda estimativa só é subtraída se estiver alinhada com o primeiro stem vocal e contiver menos energia. Filtros de coerência, limite de 85% e rampa suave impedem alterações descontroladas.
- A saída VOZ não é reprocessada. A interface, Biblioteca Inteligente, YouTube/download, Linha do Tempo, A/B/C e exportação seguem preservados.
- A segunda inferência **pode aumentar significativamente o tempo de processamento e consumo de bateria**.
- Dependendo da gravação, pode deixar vazamento de voz ou reduzir instrumentos semelhantes ao canto. Sem o original e o instrumental exportado da faixa relatada, não há validação auditiva específica nem garantia de remoção total.

## QA
- Quatro testes unitários da porta de confiança: segunda voz coerente, instrumento não correlato, voz estéreo em antifase e valores inválidos.
- Compilação e teste de áudio no emulador pela CI.
- Corrigido teste de rolagem no cartão A/B/C (anteriormente verificava rótulo fora da tela e marcava falha com a separação de 180s aprovada).
- Teste na música real de 209,5 s e em Motorola g34 5G ainda pendentes.

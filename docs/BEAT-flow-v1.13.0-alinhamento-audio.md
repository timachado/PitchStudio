# BEAT flow v1.13.0 — correção do sincronismo STFT/iSTFT

## Evidência concreta da música enviada pelo usuário
Arquivos analisados localmente, não adicionados ao repositório:
- `Gamadinho à Vontade - Instinto.m4a` (original), 209,513651s, estéreo, 44.100Hz.
- `BEATflow_Playback.wav` (exportação do BEAT flow), mesma duração e frequência.
- A diferença (original menos playback) apresenta pico de correlação com o original em **+2048 amostras**, repetidamente entre 15s e 140s da faixa. Equivale a **46,44ms**.
- Nos trechos cantados, a energia RMS da banda central 250–3800Hz estava **1,19 a 1,37 vez** maior no playback antigo do que no original, contrariando a intenção de remover canto.
- Uma reconstrução experimental deslocando o stem extraído em 2048 amostras reduziu essa razão para **0,35 a 0,69** nesses mesmos trechos; melhora mensurável, mas não prova remoção vocal perfeita.

## Origem técnica do erro
- `readResampled` posiciona o áudio de entrada em `offset-FFT_SIZE` (pré-contexto).
- `stft` usa janela centralizada `frame*HOP+i-HALF`.
- A função `istft` cortava em `i+2*HALF`, correspondendo ao sinal de entrada em `i+HALF`.
- O código de playback o subtraía de `left[i+FFT_SIZE]` = `left[i+2*HALF]`.
- Ou seja, **subtração estava 2048 amostras fora de fase temporal**, causando cancelamento incorreto e possível aumento de energia do canto.

## Correção
- `istft(..., alignmentOffset=HALF)` faz o stem da separação integral/Playback coincidir com o sample original subtraído, sem deslocar a mistura nem cortar o fim da música.
- A segunda inferência do modo Playback recebe a mesma correção. O modo de isolamento vocal dedicado `separate()` e o modo somente VOICE continuam com o offset anterior.
- Sem alteração de arquivos originais, download/YouTube, layout, exportações, biblioteca ou A/B/C.
- Teste de regressão no Android compara a correlação do vocal estimado no tempo correto com a correlação deslocada em 2048; somente gerar WAV/MP3 não é suficiente para garantir separação.

## Pendências de qualidade
- A mesma faixa precisa ser processada novamente com **v1.13.0** para avaliação auditiva definitiva.
- Mesmo perfeitamente sincronizado, MDX-Net pode deixar reverberação, coro e artefatos. Não prometer zero voz em todas as gravações.
- O WAV de demonstração reparado a partir dos arquivos enviados pode ser comparado separadamente; não substitui o processamento completo do aplicativo.

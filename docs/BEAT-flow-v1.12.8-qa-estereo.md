# BEAT flow v1.12.8 — remover vazamento vocal com estéreo antifase

A correção complementa v1.12.7 em gravações em que a voz foi panoramizada com polaridade invertida entre L/R.

**Falha anterior:** a estimativa do ganho de subtração somava canais (`L+R`) antes de computar a energia; uma voz presente em L e -R desaparece na soma e a remoção vocal adaptativa não entra em ação.

**Nova operação:** cálculo de energia e correlação em cada canal e soma escalar dos produtos, compartilhando um único ganho calibrado para a imagem estéreo. Mantém o mesmo limite de ganho 1.0–1.6, rampa de suavização e todos os arquivos/pipelines anteriores. **A voz isolada é intocada.**

**Teste novo:** `stereoAntiPhaseVocalRemainsDetectable` verifica sinal sintético com voz em fases opostas nos dois canais, acompanhamento e vocal subestimado em 30%. A versão anterior falha; a nova deve diminuir energia residual vocal em relação ao controle.

**Pendências:** teste real na música de 209,5 s do usuário, comparação auditiva, QA no Motorola g34 5G, teste com reverberações/backing vocals. A separação por IA pode manter artefatos mesmo após esta melhoria.

**Não alterado:** tela, bibliotecas de projetos, histórico, YouTube/download, identidade, composição do modelo MDX-Net, exportação e funções legadas.

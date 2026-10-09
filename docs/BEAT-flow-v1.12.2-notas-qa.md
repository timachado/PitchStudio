# BEAT flow — evolução 1.12.2 (QA)
## Escopo desta rodada
- Base: v1.12.1, branch feature/beatflow-playback-polish-1121.
- SeekBar Android real no resultado (0–100%) e contador de tempo MM:SS / MM:SS derivado da faixa processada.
- Busca aplicada apenas ao soltar o dedo; evita recriar AudioTracks repetidamente ao arrastar.
- Atualização do relógio em 250 ms enquanto a Activity está em primeiro plano, com liberação de callbacks no ciclo de vida.
- Rótulo do player corrigido ao sair para seletor de arquivos e voltar ao aplicativo.
- Motor MDX-Net, interface anterior, modos Voz/Playback/Ambos, exportação MP3/WAV preservados.

## QA pendente
1. CI: sintaxe Python, testes Android, build e smoke em Android 15 com música de três minutos.
2. QA físico no Motorola g34 5G: avançar para 50%, 95%, pausar e alternar Voz/Playback.
3. Testar músicas estéreo/mono, cancelamento e exportações WAV/MP3.
4. Testar acessibilidade TalkBack e telas menores.

Esta é uma versão de homologação, não um lançamento de produção.

# BEAT flow v1.13.2 — parâmetros independentes por trecho

- No cartão atual **Linha do Tempo Inteligente**, a opção **Ver trechos** passa a oferecer **Ajustar tom e velocidade** para cada marcação.
- Semitons -12 a +12 e velocidade de 0,5x a 2,0x. Cada ajuste vale do seu marcador até o próximo, nunca na música inteira.
- Botão **Prévia por trechos** usa o áudio original e aplica parâmetros ao AudioTrack, preservando a posição entre as mudanças. Ao sair, retorna à versão global anterior.
- O ajuste é salvo no JSON do projeto em `sectionOverrides` com `AtomicFile`, sem copiar ou editar o PCM. Projetos antigos continuam abrindo. Remover um marcador também remove seu ajuste.
- A/B/C e ajustes globais suspendem a prévia por trechos para evitar estados contraditórios.
- **Limite expresso:** esta versão contempla a audição da automação por trechos; WAV/MP3 exportados ainda refletem os ajustes globais. Renderização multiperfil com transições suaves e exportação segmentada é a próxima fase da Linha do Tempo.
- Motor Playback/IA, aba Voz, YouTube/pesquisa/prévia/importação/download, biblioteca, identidade visual e tela de edição existente preservados.
- Verificações Kotlin locais passaram; CI inclui JUnit de validação dos segmentos e smoke Android para salvar/ler JSON e alternar o modo de prévia.
- O teste de v1.13.1 havia concluído áudio 180s e A/B/C, mas falhou por rolar o cartão para fora da tela. Corrigida a navegação do QA nesta etapa.
- Antes de produção, testar no Motorola g34 5G: mudanças sem estalos, estabilidade de PlaybackParams, recuperação de projeto e efeitos dos parâmetros na prévia.

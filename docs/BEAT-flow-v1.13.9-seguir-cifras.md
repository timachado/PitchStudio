# BEAT flow v1.13.9 — Cifras acompanhando a reprodução

Nova melhoria incremental no **Modo Palco e Ensaio**; não reimplementa DSP nem remove funcionalidades aprovadas.

- Rótulos **Acorde atual** e **Próximo acorde** usam os acordes já analisados/corrigidos e armazenados no repertório. O tempo vem da posição real do player e é atualizado em intervalos de 650 ms; avançar/voltar na linha do tempo recalcula imediatamente o próximo estado.
- Botão **Seguir cifras: ligado/desligado**: ao ativar, realça apenas a linha da letra associada ao acorde atual e rola o painel de letras para a linha. Sem vínculo, informa o acorde e não desloca a letra.
- Acompanhamento é opt-in. A rolagem livre de letras continua disponível e desliga automaticamente o acompanhamento caso iniciada. Uma vez desligado, restaura o texto anotado normal, preservando cada verso e cifra como estavam.
- Após trocar de música, a visualização usa os acordes daquela faixa; evita deslocamentos de callbacks antigos em trocas rápidas.
- **Nenhuma letra, configuração musical, arquivo PCM, repertório ou seção de áudio é gravado** por esse recurso. As dicas continuam sendo aproximações; acordes não possuem acompanhamento automatizado de palavra ou posição silábica.
- Quatro testes JUnit cobrem início/fim e seek em acordes, tempos inválidos, vínculo com linhas repetidas/acordes simultâneos e preservação do texto original.
- Teste JVM local: compila StageHarmonyAnalyzer + StageChordLyrics + StageChordFollow e valida seleção, limites e posição dos trechos da letra.
- Smoke no emulador confere novo controle e sua proteção sem música aberta; as regressões de edição e voz continuam no pipeline.
- **Pendente:** validação no dispositivo físico, visibilidade do destaque em canções longas e correção do problema antigo do teste de navegação até Tom Ideal. Um APK compilado não equivale à homologação funcional.
- Código YouTube (pesquisa, player, download, salvar arquivo), Playback instrumental e Voz, Tom Ideal, Biblioteca Inteligente, WAV/MP3 e demais ferramentas não sofre alterações.

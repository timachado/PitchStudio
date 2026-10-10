# BEAT flow v1.13.10 — estabilização dos testes Android

- A v1.13.9 compilou e passou no JUnit, mas o smoke no emulador falhou ao navegar até Modo Palco; a v1.13.8 abriu Modo Palco e gravou repertório, mas falhou depois na localização do Tom Ideal.
- Ajustada busca por rótulo exato e prefixo na interface para privilegiar botões clicáveis. Ao não encontrar, procura voltando ao topo antes de percorrer até o fim; produz captura da tela e XML para erros do Modo Palco.
- A busca do teste legado para Tom Ideal, biblioteca, YouTube, PCM, WAV/MP3 e Linha do Tempo também passa a ser bidirecional.
- O AndroidManifest e a interface de produção não são modificados. Apenas versionCode 51 e versionName 1.13.10, para rastrear o candidato de QA.
- Não altera Playback instrumental, Voz, modelo MDX-Net, YouTube com download, Tom Ideal, biblioteca ou projetos salvos.
- A aprovação final depende de Gradle + JUnit + emulador Android 15. Se os testes falharem novamente, investigar a evidência e não afirmar homologação.

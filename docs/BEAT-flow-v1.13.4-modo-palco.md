# BEAT flow v1.13.4 — Modo Palco e Ensaio, primeira entrega

A nova área **Modo Palco e Ensaio** é acessível dentro do cartão **COMECE POR AQUI**, sem reorganizar nem substituir nenhum botão atual.

## Recursos implementados
- Repertórios locais nomeados, com até 40 listas / 120 músicas em cada lista. Adicionar, remover, reordenar e excluir repertórios. Excluir um repertório nunca apaga os projetos da biblioteca.
- Músicas vêm diretamente da Biblioteca Inteligente, sem copiar PCM, duplicar download ou exigir rede.
- Reprodução offline da faixa original, com tom e velocidade do projeto aplicados pelo player Android; próximo e anterior manuais, inclusive depois de a música acabar.
- Letra/anotações locais por música, editáveis, com fonte aumentada no **Modo Palco**, botões grandes e tela acesa enquanto o modo estiver ativado. O Modo Ensaio usa as mesmas letras e repertórios.
- Metadados gravados em `stage_setlists.json` por `AtomicFile`, esquema 1, sob armazenamento privado do Android. Projeto ausente não pode bloquear o aplicativo e aparece identificado.
- Pausa a reprodução do estúdio ao entrar no módulo Palco para evitar sobreposição de áudio; ao sair ou ir para background, a reprodução é pausada.
- Esta fase **não** inclui busca automática de letras, sincronização da letra com tempo, modo pedal Bluetooth ou metrônomo/contagem de entrada; ficam para próximas versões.
- O player de Palco usa pitch/tempo de prévia `PlaybackParams`, e não re-renderiza a música por DSP para este módulo. Ao desejar arquivo de palco com qualidade final, exportar no estúdio.

## Garantias e QA
- Não são alterados código de separação vocal/Playback aprovado, YouTube/download, Tom Ideal, DSP ou exportações WAV/MP3.
- Quatro testes JUnit da ordem dos repertórios (deduplicação, limites, remoção e mudança de posição). Teste Kotlin JVM local: PASS.
- Smoke Android: abrir Modo Palco, criar repertório offline, verificar bytes no armazenamento privado, alternar Modo Palco / Ensaio; em seguida rodar regressões antigas.
- Android CI com Gradle, APK universal e ARM64. Testes físicos, acessibilidade, retomar estado e preservação da assinatura continuam pendentes de homologação final.

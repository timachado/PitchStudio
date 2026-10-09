# BEAT flow v1.12.4 — Biblioteca Inteligente (incremental)

Base: v1.12.3. Nenhuma modificação intencional no YouTube, motor MDX-Net, paleta e tela principal.

## Implementado no código
- Autosave com debounce de 1,5 s para **projetos já salvos e reabertos**.
- Gravação imediata dos ajustes ao pausar/sair do editor e antes de trocar de projeto.
- Persiste sem duplicar arquivos PCM: tom, cents, velocidade, qualidade, A-B, posição.
- Salva metadados por `android.util.AtomicFile` (restauração atômica em erros de escrita).
- Histórico com até 20 revisões dos ajustes; atualizações apenas da posição não criam nova revisão.
- Em `Meus projetos`, abre `Histórico de ajustes` e pode restaurar uma configuração antiga.
- A restauração é não destrutiva: substitui apenas os ajustes e registra os anteriores como histórico.
- O armazenamento continua privado e offline.

## Delimitação e QA
- Para impedir cópias automáticas grandes sem autorização, áudios que ainda não foram salvos pela primeira vez **não** são adicionados automaticamente à biblioteca. Depois do primeiro `Salvar projeto`, os ajustes têm autosave.
- Não há migração de arquivos originais ou mudança na estrutura do PCM existente; compatibilidade com projetos JSON `schema=1`.
- Teste estático do patch executado sobre projeto Android Studio v1.12.3 reconstruído; validação de build e testes Android pela CI.
- Aceites físicos pendentes: salvar projeto > mudar tom/velocidade > fechar e reabrir > conferir valores > histórico > restaurar; repetir com armazenamento quase cheio, queda do processo e faixa de 5+ minutos.
- Não tratar como recurso concluído para produção até passar nesses testes.

# BEAT flow v1.13.8 — Correção individual de acordes e cifras sobre letras

Esta atualização é **incremental** na branch feature/beatflow-playback-polish-1121, sem refazer o app.

- No **Modo Ensaio**, após análise de tonalidade ou com harmonia previamente salva, **Editar acordes** lista os marcadores existentes. Cada marcador pode ser corrigido para uma tríade maior/menor, removido ou deslocado no tempo (0–3600 segundos e dentro da duração).
- **Adicionar acorde** registra um marcador na posição de reprodução atual, com escolha manual de tríade. Limite de 12 acordes por música, consistente com a etapa anterior.
- **Vincular à linha da letra** oferece escolha manual da linha (até 500 linhas), ou remoção de vínculo. As cifras são mostradas **acima** da linha correspondente, entre colchetes, sem modificar o texto original nem sincronizar automaticamente canto/palavras.
- Os vínculos permanecem **rascunho** até o usuário selecionar **Salvar harmonia**. O armazenamento `stage_setlists.json` inclui o campo opcional `line` por acorde; esquema 1 permanece compatível com repertórios antigos e acordes já salvos.
- Ao editar a letra e mover linhas, verifique os vínculos novamente, porque eles são baseados no índice da linha. Vínculos inválidos são descartados ao salvar; o texto não é sobrescrito.
- Os menus de correção e inclusão são bloqueados no Modo Palco para evitar edições inesperadas durante apresentações; ouvir o ponto apenas desloca a reprodução ao marcador escolhido.
- Ao trocar de repertório ou música, a análise pendente é invalidada para evitar associar acordes a outro projeto.
- A qualidade das cifras automáticas continua aproximada. Não foi implementado reconhecimento de sétimas, sus, inversões ou alinhamento temporal da letra com IA nesta rodada.
- Quatro novos testes JVM/JUnit cobrem o alinhamento, ausência de letra, vínculos inválidos e ordenação/remoção de acordes. Rodaram localmente com Kotlin; Android CI executará `testDebugUnitTest` e `assembleDebug`.
- **Preservados:** Playback instrumental aprovado e aba Voz, YouTube com busca/prévia/download/Salvar arquivo, tom/velocidade, Tom Ideal, projetos, WAV/MP3, comparação A/B/C, BPM e metrônomo, repertórios e modo palco.
- QA no Motorola g34 5G ainda necessário antes de declarar a versão final homologada.

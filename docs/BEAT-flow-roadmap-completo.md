# BEAT flow — Plano mestre de evolução (T.I. Machado)

**Atualização:** 2026-10-09  
**Base preservada:** `timachado/PitchStudio`, branch `feature/beatflow-playback-polish-1121`, v1.12.2 QA.  
**Distribuição:** APK Android independente; não há requisito de publicar na Google Play.  
**Diretriz inegociável:** evoluir incrementalmente; não reiniciar o projeto, substituir a identidade aprovada, retirar ferramentas existentes nem remover a funcionalidade de salvar/baixar áudio já presente. Respeitar direitos autorais, permissões e termos de fontes externas.

## Escopo funcional do BEAT flow (não confundir com BEAT flow Music)
O **BEAT flow** é o estúdio para carregar músicas, alterar tom/velocidade, analisar voz, gerar playback, editar e preparar apresentações. **BEAT flow Music** é um projeto futuro separado de player/biblioteca com referência a experiências de streaming. Não incluir a construção do segundo aplicativo no aceite do primeiro.

### A. Funcionalidades prioritárias citadas pelo usuário
| Código | Módulo | Experiência-alvo | Situação verificada |
|---|---|---|---|
| BF-01 | Tom Ideal — Assistente Vocal | Gravar alguns segundos, estimar região vocal, comparar notas da música, recomendar até 3 tonalidades, ouvir e aplicar a favorita | **Parcial**: `VoicePitchAnalyzer.kt`, `TomIdealActivity.kt`, `SongPhraseAnalyzer.kt` e integração v1.9.9; audição imediata das três versões e refinamento de precisão ainda exigem validação/implementação |
| BF-02 | Biblioteca Inteligente de Projetos | Salvar música original, versões, tons favoritos, parâmetros, histórico, rascunhos, autosave com recuperação após interrupção | **Parcial**: `ProjectLibrary.kt` persiste original e parâmetros; histórico, autosave e versões vinculadas não confirmados |
| BF-03 | Comparação A/B/C sincronizada | Três combinações de tom, velocidade e qualidade; alternar mantendo a mesma posição musical e fazer comparação perceptiva | **Nova evolução**: A/B relatado como existente; A/B/C não confirmado |
| BF-04 | Linha do Tempo Inteligente | Waveform com navegação, marcadores da introdução, verso, refrão, ponte e final; ajustes por trecho, loop A/B, desfazer/refazer e edição não destrutiva | **Parcial**: waveform/seek da v1.12.2 e loop anterior; detecção/rotulagem de seções e automações por trecho não confirmadas |
| BF-05 | Modo Palco | Letras grandes quando fornecidas/permitidas, repertórios ou setlists, troca de faixas, controles simplificados, arquivos locais offline | **Nova evolução**: implementação não identificada |
| BF-06 | Preservação Vocal Avançada | Transposição de tom com preservação de timbre/formantes, alteração de tempo independente do pitch, perfis conforme conteúdo; comparar artefatos A/B | **Nova evolução do DSP**: preservar o motor atual como fallback e testar qualidade objetivamente; não afirmar que formant-shifting já existe |
| BF-07 | Separação de Voz e Instrumentos | Além de Voz / Instrumental / Ambos, stems de bateria, baixo e acompanhamento, com possibilidade de silenciar/mixar cada parte | **Parcial**: MDX-Net para vocal/instrumental presente; stems multi-instrumento precisam de modelo, controles e validação adicionais |

### B. Complementos musicais do print e integração entre módulos
| Código | Módulo | Experiência-alvo | Situação |
|---|---|---|---|
| BF-08 | Detecção de tonalidade, acordes e andamento | Mostrar tonalidade sugerida, acordes com posições aproximadas, BPM e compasso com indicador de confiança | **Planejado**, sem implementação confirmada |
| BF-09 | Metrônomo inteligente | Click sincronizado ao BPM/compasso com subdivisão opcional, contagem inicial, uso no ensaio e no Modo Palco | **Planejado**, sem implementação confirmada |
| BF-10 | Modo Ensaio | Loop de trechos, alteração de velocidade independente do tom, acesso a favoritos e comparação com a música original | **Parcial**: loop/tom/velocidade possuem base; fluxo completo não confirmado |
| BF-11 | Presets e configurações | Guardar presets de tom, velocidade, qualidade e stem; compartilhar ajustes entre músicas sem sobrescrever arquivos | **Planejado**; integração com biblioteca necessária |
| BF-12 | Integração de ponta a ponta | Abrir stem, música editada ou exportação diretamente no editor, Tom Ideal, biblioteca e repertório preservando metadados/versões | **Parcial**, integração completa não validada |
| BF-13 | Exportação profissional | WAV/MP3 completos; nome com música/versão/stem; guardar arquivo gerado e poder reabrir ou compartilhar | **Parcial**: exportadores existem; homologação completa pendente |

### C. Recursos já construídos que NÃO devem regredir
- Marca e visual aprovados **BEAT flow**, Material 3 Expressive.
- Pesquisa e prévia de músicas, importação e opção existente de salvar/baixar áudio, observados direitos, permissões e condições da origem.
- Carregamento de faixas locais, player, controles de tom e velocidade.
- Tom Ideal e biblioteca já integrados, mesmo que ainda incompletos.
- Prévia de stems 6/12/18 s e opção de faixa completa, modos Voz / Instrumental / Ambos, waveform e controle de progresso/cancelamento.
- Exportação WAV/MP3, autonomia offline dos recursos locais.
- Não alterar o layout existente sem solicitação; novas funções por superfícies discretas e consistentes com os mockups aprovados. Preservar ID e assinatura quando viável nas entregas instaláveis; validar migração de dados.

## Critérios funcionais mínimos por fase

### Fase 0 — Estabilizar o motor existente (bloqueadora)
- Investigar a falha da CI **37881292642** (v1.12.2): o teste de aproximadamente **3 minutos** terminou com `FALHA: processamento de 3 min não gerou áudio completo`. Build/APK passam, mas o teste de áudio longo **não passa**.
- Capturar logs, avaliar se falha no emulador ou app, verificar duração, canais, memória e caches; corrigir sem mascarar o smoke test.
- Rodar casos curtos (6, 12, 18 s) e longos (3, 5, 10 min), WAV/MP3 e cancelamento.
- Validar no Motorola g34 5G e guardar evidências antes de declarar homologação concluída.

### Fase 1 — Inteligência vocal e edição
- BF-01: 3 recomendações fundamentadas no perfil e na música, com aviso de incerteza; escuta comparativa e aplicação no editor.
- BF-03: troca A/B/C realmente sincronizada (sem reset do tempo), presets persistentes e teste de latência ao alternar.
- BF-04: marcações de seções podem ser adicionadas/editadas manualmente primeiro; detecção automática deve permitir correção de rótulos.
- BF-06: perfis DSP e preservação de formantes com fallback para o algoritmo original; testes com voz masculina/feminina, fala, instrumentos.

### Fase 2 — Projetos e ensaios
- BF-02, BF-10, BF-11 e BF-12: gravação automática transacional, recuperação após encerramento, histórico de versões editáveis, presets/loops e abertura de stems sem duplicar originais.
- Garantir que perda de energia/armazenamento cheio nunca apague o original.

### Fase 3 — Recursos de palco e instrumentos
- BF-05: setlist, letras fornecidas pelo usuário/permitidas, tipografia grande, offline, controles grandes e troca previsível.
- BF-07: avaliar modelo multi-stem adequado para Android e memória; não prometer qualidade perfeita nem inferência instantânea. Preservar modo vocal/instrumental como fallback.
- BF-08, BF-09: BPM, acordes com confiança e metrônomo com sincronização precisa; aceitar ajuste manual.

### Fase 4 — Aceite da versão completa
- Regressão da interface e funções originais, permissões de arquivos, privacidade, compatibilidade Android, tratamento de falhas e navegação acessível.
- APK independente de distribuição, assinatura estável, migração de dados e documentação.
- Ensaios reais com pelo menos um aparelho físico; CI Android 15 sem falhas reproduzíveis.

## Classificações e limites
- **Implementado** = existe código, não garante aprovação de QA.
- **Parcial** = existe base técnica, integração/experiência ou testes ainda pendentes.
- **Planejado** = funcionalidade detalhada para desenvolver, não atribuída incorretamente à versão atual.
- A lista acima contém os quatro módulos que o usuário descreveu e as funções lembradas pelo print (Modo Palco, Preservação Vocal, multi-stem, detecção de acordes/metrônomo); os complementos estão separados para priorização.
- Estimativas anteriores de 80% cobrem somente o escopo reduzido da v1.12.x. Não reutilizar essa porcentagem para todo este plano sem reestimar esforço e aceites.

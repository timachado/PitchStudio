# BEAT flow — Escopo funcional v1.12.0
**Produto:** BEAT flow · by T.I. Machado  
**Status:** ESCOPO APROVADO PARA IMPLEMENTAÇÃO; **NÃO É BUILD FUNCIONAL ENTREGUE**  
**Base técnica:** v1.11.0 (branch `feature/beatflow-brand-1110`)  
**Objetivo:** reproduzir os mockups aprovados e permitir a criação de **playback/instrumental de uma música inteira**, sem o limite anterior de 6/12/18 segundos. Manter Tom Ideal, efeitos, biblioteca, prévias, exportação WAV/MP3, cancelamento e identidade BEAT flow.

## 1. Definição do produto e termos
- **Voz:** componente vocal extraído por IA.
- **Instrumental / Playback:** música sem a voz principal na medida do possível, obtida pela subtração controlada do stem vocal da mixagem; podem restar artefatos/vozes, dependendo da gravação.
- **Ambos:** resultados vocais e instrumentais gerados na mesma execução, de forma consistente e sincronizada.
- **Prévia:** processar um trecho selecionado com 6, 12 ou 18 segundos.
- **Música inteira:** processar do primeiro ao último frame da faixa, independentemente de ter 1, 3, 5 ou mais minutos. O processamento é local para músicas que o usuário tem direito de utilizar, sem necessidade de upload. Mensagem de limite apenas em caso de recursos insuficientes/arquivo incompatível, não limitação artificial a 18s.

## 2. Navegação
### 2.1 Home BEAT flow
- Continuar com identidade Material 3 Expressive aprovada: base azul-noite, lima elétrica, ciano, coral e lilás, bordas arredondadas e tipografia atual.
- Expor ações `Explorar músicas`, `Importar do dispositivo`, `Tom Ideal`, `Separação com IA`, `Meus projetos`.
- Nome comercial visível: **BEAT flow**. Assinatura: **by T.I. Machado**.
- Permitir abrir Separação com IA com áudio local já carregado.

### 2.2 Explorar músicas / YouTube (conforme mockup)
- Header estilizado BEAT flow, back button, título `YouTube`, subtítulo, campo de pesquisa com lupa, botão `Buscar`.
- Estado vazio orientado à busca e estados de carregamento/sem resultados/erro/reconexão.
- Resultados em cards: thumbnail oficial quando fornecida, título, artista/canal, duração quando disponível, ações `Prévia` e `Abrir no YouTube`.
- Prévia por **player oficial incorporado do YouTube**, respeitando identidade da plataforma e controles, sem simular vídeo com player de áudio.
- Não apresentar ficticiamente resultados reais durante buscas em branco. Mockups representam estado **ilustrativo**, não dados reais já carregados.
- Separação/extração de áudio, download/offline ou processamento de conteúdo vindo diretamente do YouTube **não entram neste escopo sem autorização específica aplicável**. `Usar áudio` deve aparecer apenas para uma fonte **local ou devidamente licenciada**: não habilitar extração de trilhas de vídeos do YouTube.
- Integração de busca real depende de API, autenticação/chave segura, limites de quota e conformidade; falhas devem ser comunicadas sem fechar o aplicativo.

### 2.3 Separação com IA (mockup aprovado)
- Cabeçalho `Separação com IA`, subtítulo e card da faixa (capa quando houver, título, origem local, duração, formato).
- Seletor visível `Voz | Instrumental | Ambos`; modo instrumental também pode ser identificado como **Gerar playback**.
- Seletor independente de alcance `Prévia | Música inteira`; no modo Prévia, chips `6 s | 12 s | 18 s`; no modo Música inteira, chips ocultos ou inativos e duração real exibida.
- Botão principal `Processar` com estados `Pronto | Processando | Cancelando | Concluído | Falhou`.
- Durante o processo: progresso 0–100% baseado nos frames efetivamente processados, tempo já processado, status de cancelamento, desabilitar múltiplos inícios concorrentes.
- `Cancelar`: interromper em pontos seguros, liberar buffers/sessões e limpar temporários de outputs incompletos sem modificar a faixa original.
- Resultado: card com ondas/waveform calculada do **arquivo resultante**, duração real, controles `Ouvir/Pausar`, seletor Voz/Instrumental se `Ambos` e ação `Salvar instrumental`, `Salvar voz` ou `Salvar ambos`.
- Respeitar acessibilidade, textos PT-BR, áreas de toque, telas pequenas e estados sem permissão/sem espaço.

### 2.4 Biblioteca e editor
- Importar arquivos locais via Storage Access Framework e manter o projeto original sem mutações destrutivas.
- Criar item de projeto derivado identificado como `Playback` e metadados da origem.
- Permitir ouvir o resultado, comparar com original, abrir Tom Ideal e ajustar tom/velocidade no áudio derivado sem apagar o original.
- Cancelamento de uma separação não apaga projetos previamente salvos.

## 3. Motor real de separação de música inteira
- Usar o modelo ONNX local MDX-Net já integrado (ou substituí-lo somente com comparação objetiva de qualidade), reutilizando sessão durante uma música.
- Converter/desserializar entrada em streaming/janelas com sobreposição; **não carregar o áudio inteiro em float arrays** nem criar um tensor para a faixa completa.
- Cada janela deve preservar continuidade do tempo; crossfade/overlap-add para reduzir ruídos nas emendas; instrumental como residual `mix - vocal` com cuidado com clipping e canais.
- **Preservar estéreo** quando a entrada possuir dois canais. Não converter o playback final em mono automaticamente; saída mono aceitável para entrada mono.
- Decodificar/processar/gravar incrementalmente em arquivo temporário local com uso de RAM aproximadamente constante em relação à duração da música; verificar espaço disponível antes de iniciar e durante o processamento.
- Fornecer status de progresso e cancelamento real; não prometer processamento instantâneo (inferência pode demorar em modelos de smartphone).
- Ao concluir, conferir duração e frames; saída precisa corresponder à duração integral da entrada, tolerância máxima de **100 ms**, e não incluir truncamentos, lacunas ou emendas audíveis grosseiras.
- Invariantes: original intocado, sem vazamento de cache, sem crash/OOM; lidar com encerramento da Activity/rotação/interrupção do app sem declarar sucesso falso.
- Processar fonte local somente; músicas longas ficam sujeitas ao espaço disponível e à capacidade do aparelho, com mensagens claras.

## 4. Exportação
- Exportar instrumental completo **WAV PCM16** (44,1 kHz por padrão; preservar taxa de entrada quando tecnicamente viável) e **MP3 até 320 kbps** com seletor Android SAF.
- Se `Ambos`, exportar dois arquivos separadamente ou no mesmo fluxo de destino devidamente escolhido.
- Nomes de arquivo sugeridos: `BEATflow_<faixa>_Playback.wav`, `BEATflow_<faixa>_Voz.wav`; evitar colidir/substituir sem confirmação.
- Conferir arquivo real escrito e expor `Abrir arquivo`/local escolhido; nunca mostrar `Concluído` antes da finalização da gravação.
- Formato MP3/WAV de prévia continua disponível para trechos; nenhuma regressão nas exportações v1.11.0.

## 5. Padrão visual fiel aos mockups
- Manter a **linguagem visual** (hierarquia, paleta, cards, raio dos cantos, tipografia, estados, botões, waveform) dos dois mockups aprovados: `Explorar YouTube` e `Separação com IA`.
- O layout é responsivo; os elementos se reorganizam para Motorola g34 5G e outros formatos sem sobreposição, clipping ou barra horizontal.
- Imagens de músicas/artistas mostradas no mockup são **exemplos ilustrativos**; na interface funcional usar metadados/imagens efetivos das fontes apropriadas, sem inventar catálogo ou endosso.
- O player de vídeo deve ser funcional, não apenas uma imagem com botão play. O waveform/percentual devem representar o progresso real, não uma animação decorativa.

## 6. Critérios de aceite obrigatórios para a v1.12.0
1. App instala em paralelo com a versão 1.11.0 de QA; abre com nome e ícone BEAT flow; não perde funções aprovadas.
2. Com WAV/MP3 local de cerca de **3 a 5 minutos**, escolhe `Instrumental > Música inteira > Processar`. Obtém WAV com duração da faixa completa (±100 ms) e playback audível; não apenas 18s.
3. Mesma fonte gera `Voz` e `Ambos`; `Ambos` gera dois arquivos sincronizados e corretamente nomeados.
4. O modo `Prévia` continua com 6/12/18s e não fica confundido com `Música inteira`.
5. Testar música estéreo e mono; verificar integridade de header/duração/canais, e absence de lacunas claras nas emendas.
6. Após salvar via SAF, validar bytes reais do WAV e decodificação do MP3; testar destino cancelado e erro de permissão/armazenamento.
7. Cancelar a separação da música inteira em andamento: interface recuperada, nenhuma gravação parcial marcada como pronta, cache incompleto eliminado.
8. Medir RSS/PSS de memória e tempo real num Motorola g34 5G com faixas de 1, 3, 5 e 10 minutos, inclusive repetição; não aprovar exclusivamente pelo emulador.
9. Tela YouTube abre/volta sem crash; validar busca real apenas com credenciais/infraestrutura adequada e prévia no player incorporado oficial. Nenhum recurso que extrai áudio de vídeos YouTube sem direitos.
10. Inspeção visual lado a lado dos dois mockups e screenshot de cada estado: inicial, busca, resultados, prévia, processando, concluído e erro, com rótulos em PT-BR.

## 7. Ordem de implementação — versão 1.12.0
**Fase A — motor**: implementar processamento integral em streaming, estéreo e stem residual, progress/cancel e testes de duração.  
**Fase B — produto**: desenvolver tela `Separação com IA` e conectar modo local `Voz | Instrumental | Ambos` a prévia e música inteira.  
**Fase C — interface YouTube**: replicar identidade visual do mockup e usar preview oficial; não realizar extração/download de áudio da plataforma sem autorização.  
**Fase D — exportação / homologação**: WAV/MP3 completos, integração com biblioteca, testes CI/emulador e instalação/testes físicos.

### Não confundir estados
O mockup indica aparência e intenção, **não** prova que um player YouTube ao vivo, processamento da música inteira ou o motor instrumental já estão implementados. **O escopo v1.12.0 ainda precisa ser programado, compilado e homologado**.

## 8. Questões comerciais
- Marca BEAT flow escolhida para o produto; a titularidade/exclusividade jurídica não foi confirmada e exige busca INPI/assessoria antes de divulgação comercial.
- Publicação na Play Store, assinatura estável e plano de serviços musical são etapas posteriores.

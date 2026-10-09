# BEAT flow v1.12.5 — Comparação A/B/C (etapa inicial)

- Atualização incremental da v1.12.4. Sem alterações no motor MDX-Net ou nos caminhos de busca e download de músicas.
- Preservado o botão A/B legado; criado controle adicional **Comparar A/B/C** no cartão AGORA NO ESTÚDIO.
- A Original: tom 0, velocidade 1.00x.
- B Atual: fotografia dos ajustes do editor quando a comparação começa.
- C Alternativa: ajustável com sliders de tom e velocidade, sem alterar os parâmetros do editor.
- Troca A/B/C pelo mesmo arquivo local e mesma posição de leitura usando AudioTrack PlaybackParams; não procura o começo de novo a cada mudança. Na entrada/saída do modo há uma única troca de projeto mantendo a fração da posição.
- Ao sair, retorna ao modo anterior do A/B.
- Motor de qualidade DSP: preservado sem afirmação falsa de troca instantânea entre qualidades; perfis de qualidade e comparações de renders pré-processados ainda são pendência de outra etapa.
- Versões A/B/C ainda não são persistidas na Biblioteca Inteligente; esse será um incremento futuro.
- Validar no Motorola g34 5G: clique rápido entre A/B/C durante reprodução, áudio no ponto certo, qualidade subjetiva, restauração do estado e ausência de crackle.

Implementação em patch Python compactado (`.pitchstudio/v1125/patch_v1125.py.gz`); descompactar com `gzip -dc` para inspecionar o código. O pipeline expõe todo o fonte expandido no artefato Android Studio.

# BEAT flow v1.13.5 — rolagem de letras e controles de ensaio

Novos controles exclusivos do **Modo Palco e Ensaio**, preservando a área de edição e o motor de áudio.

- Letras em painel próprio com rolagem manual ou automática. O movimento é puramente visual e não modifica áudio.
- Iniciar/parar rolagem, alternar entre Lenta/Média/Rápida e voltar ao topo. A rolagem para ao sair do app, trocar de faixa ou ao chegar ao final.
- Painel de letra ampliado quando o Modo Palco está ativo, mas a tela mantém transporte e repertórios acessíveis.
- Saltos de 10 segundos para trás e para a frente; botão **Ver letra ↓** para chegar ao painel.
- No Ensaio: **Marcar A**, **Marcar B** e **Limpar A/B** para repetir um trecho. Marcadores inválidos ou invertidos são rejeitados. No Palco a repetição é bloqueada para evitar surpresas.
- Não sincroniza palavras automaticamente com o canto nem faz busca de letras. A velocidade de rolagem é independente da velocidade da música.
- Retém projetos, repertórios offline, letras originais, playback aprovado, YouTube/download, exportações, A/B/C e Tom Ideal.
- Testes JUnit de limites de salto, duração inválida, marcadores A/B e velocidades de rolagem.
- CI executa smoke Palco (persistência de repertório, alternância de modo, velocidade de letras), e regressão antiga. A regressão antiga ainda depende de uma navegação UI na tela Tom Ideal, que já causou falhas mesmo com o Modo Palco aprovado; não confundir essas falhas.
- Verificação no Motorola g34 5G necessária antes de concluir acessibilidade, fluidez de rolagem e consumo de bateria.

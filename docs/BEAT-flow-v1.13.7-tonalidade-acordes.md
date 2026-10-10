# BEAT flow v1.13.7 — tonalidade e acordes sugeridos

## Mudança incremental (nenhuma regressão intencional)

- Modo Palco e Ensaio recebe painel **Tonalidade e acordes · sugestões offline**, com ações **Analisar tonalidade**, **Corrigir tom** e **Salvar harmonia**.
- Analisa no dispositivo até 36 segundos do PCM float32 original, limitado a 120 janelas de 4096 amostras, sem tocar nos arquivos de áudio e sem internet.
- Usa FFT radix-2, agregação de cromas de 12 semitons, perfis maior/menor para tonalidade, e comparação de tríades para acordes com marcação aproximada a cada cinco segundos.
- O algoritmo é experimental: pode confundir inversões, acordes de sétima, vozes, harmonias complexas, modulações e peças em que o baixo não define claramente a tonalidade. Sem sinal confiável retorna **indeterminada**; acorde incerto é omitido.
- Correção manual de tom maior/menor e confirmação explícita para salvar. Resultados de acordes aparecem como **sugestões (?)**, não cifras garantidas.
- Somente após confirmar salva tonalidade e até 12 acordes em **harmonies** dentro de stage_setlists.json (schema 1), compatível com repertórios antigos. Não duplica PCM, não altera a reprodução nem reprocessa o Playback.
- Ao selecionar outra música e ao deixar a Activity, invalida resultados pendentes; consultas assíncronas não substituem a música selecionada.
- Testes unitários cobrem progressão sintética C–F–G–C, silêncio inválido e arquivo PCM 8 segundos com Dó maior, verificando que o arquivo de entrada não é modificado.
- Próximas etapas possíveis: tocar o acorde de referência, edição manual das sugestões de acordes, sincronização com letras e reconhecimento de inversões/harmonias avançadas.
- Todos os recursos do estúdio e YouTube (pesquisa/prévia/download e Salvar arquivo), separação de voz/playback aprovado, pitch, Tom Ideal, Biblioteca Inteligente, exportações e modo de palco anterior permanecem.
- Compilação e homologação no Motorola g34 5G ainda são validações necessárias antes da versão estável.

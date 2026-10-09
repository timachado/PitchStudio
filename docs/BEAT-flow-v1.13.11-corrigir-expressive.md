# BEAT flow v1.13.11 — Restaurar Material Expressive e Tom Ideal

## Causa confirmada com fonte Android Studio e evidências do emulador v1.13.10
O editor passou de 32 para 34 filhos diretos após adicionar o botão Modo Palco (índice 2) e exportação WAV/MP3 por trechos (índice 31). A função reflowExpressiveUi só aceitava 32 e retornava silenciosamente, deixando de criar os cartões Material 3 Expressive, Tom Ideal, Biblioteca Inteligente, IA de separação vocal, comparação A/B/C e Linha do Tempo. O APK compilava, mas faltavam funcionalidades visíveis.

## Correção incremental
Mapeia os 34 filhos sem duplicar ou perder qualquer elemento. Preserva acesso Modo Palco e exportações por trechos, restaura o cartão Comece Por Aqui com Tom Ideal e separação com IA e o cartão Agora no Estúdio com A/B/C e Linha do Tempo. Registra falhas estruturais inesperadas no logcat.

A CI passa a validar estaticamente 34 componentes, e o smoke do emulador exige o cartão Material e abertura de Tom Ideal antes de entrar no Modo Palco. DSP, IA, Playback, Voz, YouTube/prévia/download/Salvar arquivo, dados de projetos e repertórios não mudaram. Aprovação final depende de Gradle, testes de interface e validação física em Android.

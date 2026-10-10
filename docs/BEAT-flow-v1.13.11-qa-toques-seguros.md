# BEAT flow v1.13.11 — teste da interface confirmado e gesto do sistema corrigido

A v1.13.11 restaurou o Material 3 Expressive; o emulador confirmou o cartão COMEÇE POR AQUI, abriu o Tom Ideal e retornou ao Modo Palco. No mesmo smoke, o teste tocou em Velocidade: Média nas coordenadas (785,2304), junto à barra de gestos Android, abrindo a tela Recents. Não foi crash do app nem falha do DSP.

O localizador de controles agora conhece os limites seguros do display via bounds da hierarquia UI. Quando um nó fica perto da navegação inferior ou cabeçalho, rola o ScrollView pela margem lateral e só envia tap após entrar na área segura. Mantém coleta de logcat, XML e screenshot em falhas. Nenhuma funcionalidade nem APK de produção foi modificada por este ajuste de QA.

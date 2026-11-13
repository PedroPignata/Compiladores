# Adivinha o trem, sô!

Jogo de adivinhação escrito em **mineirês**, a linguagem do MiniForge.
O programa completo está em [adivinha.mini](adivinha.mini): leitura, mensagens,
comparações, contagem e repetição ficam nesse arquivo. Não há aplicativo Python
específico para conduzir a partida.

Projeto do grupo: Pedro Dutra, Pedro Pignata, Lucas Rocha Dantas e Renato Portilho.
Compiladores 2026.2, professora Lorena Bezerra.

## Começar a jogar

Abra um terminal na pasta `Compiladores/MiniForge` e execute:

```bash
python3 -m miniforge exemplos/adivinha/adivinha.mini --executar
```

No Windows ou com ambiente virtual ativo, use `python` no lugar de `python3`.
O compilador exige Python 3.10+. Não é necessário instalar pytest para jogar.
A instalação completa e o guia dos dois programas estão em
[exemplos/README.md](../README.md).

O segredo é **sorteado entre 1 e 100**, incluindo os dois extremos, quando a
partida começa. Não é mais fixo em 65. Cada nova execução faz outro sorteio;
repetir um número por acaso é possível e não indica falha.

## Regras da partida

1. Digite um inteiro e pressione Enter após a pergunta do palpite.
2. Se for menor que o segredo, a dica pede um número maior.
3. Se for maior, a dica pede um número menor.
4. Ao acertar, o jogo mostra o total de tentativas e encerra.
5. Digite **0** a qualquer momento de leitura de palpite para sair.

Palpites abaixo do mínimo ou acima do máximo são recusados e não contam.
Textos e decimais também não contam: o leitor de inteiros solicita outra entrada.
Um palpite válido repetido conta novamente, mesmo que já tenha sido tentado.
O jogo não altera seu intervalo automaticamente depois de cada dica.

Exemplo ilustrativo de uma partida **caso o sorteio dê 65**:

| Entrada | Resposta relevante |
|---|---|
| 40 | `Tá pequeno demais, sô! Tenta um maior.` |
| 80 | `Passou da conta, uai! Tenta um menor.` |
| 65 | `Acertou, trem bão!` e quantidade 3 |

O contador aparece na linha seguinte à mensagem `Quantidade de tentativas:`.
A linguagem não tem interpolação de texto: mensagem e número são comandos de
saída separados. Para jogar novamente, execute o mesmo comando no terminal.

## Entender como o programa foi construído

### Configuração e estado

```text
trem minimo: inteirim = 1;
trem maximo: inteirim = 100;
trem segredo: inteirim = 0;
trem tentativas: inteirim = 0;
trem jogando: booleanim = eh_memo;
```

`minimo` e `maximo` definem o intervalo. `segredo` começa em zero e recebe
o sorteio após validar os limites. `tentativas` registra palpites válidos;
`jogando` controla o laço. A inicialização é obrigatória na linguagem.
O fonte exige mínimo positivo e mínimo não maior que máximo; configuração
inválida mostra mensagem e encerra sem ler palpites nem sortear.

```text
uai (jogando) {
    segredo = sorteia_so(minimo, maximo);
}
```

Essa chamada fica **fora do laço de palpites**: o segredo não muda durante a
partida. O sorteio acontece no executor, não no parser nem no otimizador.

### Leitura, escopo e repetição

```text
enquanto_tiver (jogando) {
    trem palpite: inteirim = 0;
    mostra_so("Qual é seu palpite, sô?");
    le_so(palpite);
    // O restante do bloco valida e compara o palpite.
}
```

Esse trecho é um recorte didático; o programa completo inclui as atribuições
que encerram o laço. O palpite pertence ao bloco da rodada. O contador e o
segredo ficam no escopo externo, por isso continuam disponíveis nas rodadas
seguintes. `le_so` só pode receber uma variável inteira declarada.

### Contagem e dicas

Após verificar o intervalo, o programa incrementa `tentativas`. Condicionais
`uai`/`sinao` distinguem menor, maior e igual. Ao acertar ou escolher zero,
`jogando = num_eh` faz a próxima verificação do laço terminar a partida.
Não é necessário `break`, funções, vetores ou operadores lógicos adicionais.

## Alterar o jogo

### Mudar o intervalo de sorteio

Edite as duas declarações iniciais. Para jogar de 10 até 50:

```text
trem minimo: inteirim = 10;
trem maximo: inteirim = 50;
```

A chamada `segredo = sorteia_so(minimo, maximo);` passa a escolher um número
nesse intervalo e as mensagens exibem os novos limites automaticamente.
Mantenha o mínimo maior ou igual a 1, pois zero é reservado para sair.
Salve e reinicie o programa: a partida já compilada não lê suas edições.

### Preparar uma demonstração previsível

Para demonstrar um acerto garantido, use temporariamente `minimo = 42` e
`maximo = 42` nas declarações. O sorteio num intervalo de um elemento resulta
em 42. Isso permite mostrar contagem e encerramento sem revelar ou fixar o
segredo da versão normal. Depois restaure 1 e 100 antes de rodar os testes.
Não mova o sorteio para dentro de `enquanto_tiver`: isso mudaria o segredo a
cada palpite e alteraria as regras do jogo.

### Mudar as frases ou o visual

Altere o conteúdo entre aspas de `mostra_so("mensagem");`. Acentos e símbolos
de moldura são permitidos dentro das aspas. Preserve aspas duplas e ponto e
vírgula. Não há escapes, quebras de linha dentro do literal ou concatenação.
Cada linha do menu precisa de seu próprio comando de saída.

### Experimentar uma regra diferente

A contagem fica em `tentativas = tentativas + 1;`. Mover essa linha para antes
da validação do intervalo faria palpites fora do intervalo contarem também.
Se fizer isso, atualize as regras no README e os testes. Para manter o programa
original, não mova a linha. Limite de tentativas é uma ideia possível, mas **não está implementado**.
O sorteio aleatório já faz parte desta versão.

## Inspecionar a compilação

```bash
python -m miniforge exemplos/adivinha/adivinha.mini --verificar
python -m miniforge exemplos/adivinha/adivinha.mini --tokens
python -m miniforge exemplos/adivinha/adivinha.mini --ast
python -m miniforge exemplos/adivinha/adivinha.mini --tipos
python -m miniforge exemplos/adivinha/adivinha.mini --tac
python -m miniforge exemplos/adivinha/adivinha.mini --tac -O
python -m miniforge exemplos/adivinha/adivinha.mini --executar -O
```

Inspeções não pedem palpites. O TAC contém `read` para entrada, `texto` e
`print` para saída, além de rótulos e saltos para laço e condições. Na execução,
o MiniForge interpreta essas instruções genéricas. A opção `-O` aplica os
cinco passes antes de executar. Não combine `--executar` com inspeções.

## Testar e demonstrar

```bash
python -m pytest -q tests/test_adivinha.py
python -m pytest -q
```

Os testes verificam dicas, contagem, saída com zero, limites, texto/decimal
inválido, EOF, personalização, configuração inválida, rótulos, idempotência e
execução com/sem otimização. Não introduzem um executor separado do compilador.

Demonstração sugerida: mostrar `sorteia_so` fora do laço; executar e seguir as
dicas; repetir com `-O`; demonstrar 101 como palpite recusado e 0 para sair.
Para um acerto previsível, usar temporariamente intervalo 42 a 42. Não prometer
que 40/80/65 acertam no intervalo normal: o segredo agora é aleatório.
Os testes controlam o gerador para conferir dicas e contagem de forma repetível,
mas o programa de uso normal não recebe semente ou segredo fixos.

## Limites e erros comuns

- O sorteio é realizado em cada execução, não em cada palpite; números podem se repetir entre partidas.
- Não há limite de tentativas nem reinício automático depois de vencer.
- EOF sem escolher sair produz erro com código 1; Ctrl+C retorna 130.
- `No module named miniforge`: execute a partir da pasta `MiniForge/`.
- `uai (palpite)` não é válido: condições exigem booleanos, como `palpite == 0`.
- Se configurar limites inválidos, a própria validação impede a partida
  antes do sorteio. Não é um erro de tipos.

Veja também a [Calculadora Mineira](../calculadora/README.md) e o
[guia para usar e modificar os dois programas](../README.md).

## Sorteio e otimização

Mesmo com limites constantes, `sorteia_so` não pode virar uma constante durante
a compilação. O TAC contém uma instrução de sorteio, executada quando a partida
começa. Os cinco passes preservam a chamada e suas possíveis falhas. Testes e
medições vigentes estão em [otimizacao.md](../../docs/otimizacao.md) e
[testes.md](../../docs/testes.md).

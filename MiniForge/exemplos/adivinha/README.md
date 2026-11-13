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

O número secreto padrão é **65**, no intervalo de **1 a 100**. Ele é fixo no
código, não sorteado. Para jogar sem saber a resposta, peça a um colega para
alterá-lo antes de iniciar a partida e não abra o fonte durante o jogo.

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

Exemplo real de caminho de jogo, com segredo 65:

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
trem segredo: inteirim = 65;
trem minimo: inteirim = 1;
trem maximo: inteirim = 100;
trem tentativas: inteirim = 0;
trem jogando: booleanim = eh_memo;
```

Os três primeiros valores definem a partida. `tentativas` registra palpites
válidos; `jogando` controla o laço. A inicialização é obrigatória na linguagem.
O fonte verifica a configuração antes de pedir palpites: mínimo positivo,
mínimo não maior que máximo e segredo dentro do intervalo. Caso contrário,
mostra uma mensagem e encerra sem consumir entrada.

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

### Mudar o segredo

Edite somente esta declaração e salve o arquivo UTF-8:

```text
trem segredo: inteirim = 42;
```

Execute novamente. O segredo precisa estar no intervalo configurado. Alterar
o arquivo durante uma execução não muda a partida que já foi compilada.

### Mudar o intervalo

Para jogar de 10 até 50, use:

```text
trem segredo: inteirim = 32;
trem minimo: inteirim = 10;
trem maximo: inteirim = 50;
```

O texto do programa mostra `minimo` e `maximo` por comandos de saída, então os
limites exibidos acompanham essas alterações sem editar mensagens. Mantenha o
mínimo maior ou igual a 1: zero é o comando reservado para abandonar a partida.

### Mudar as frases ou o visual

Altere o conteúdo entre aspas de `mostra_so("mensagem");`. Acentos e símbolos
de moldura são permitidos dentro das aspas. Preserve aspas duplas e ponto e
vírgula. Não há escapes, quebras de linha dentro do literal ou concatenação.
Cada linha do menu precisa de seu próprio comando de saída.

### Experimentar uma regra diferente

A contagem fica em `tentativas = tentativas + 1;`. Mover essa linha para antes
da validação do intervalo faria palpites fora do intervalo contarem também.
Se fizer isso, atualize as regras no README e os testes. Para manter o programa
original, não mova a linha. Limite de tentativas e sorteio aleatório são ideias
possíveis, mas **não estão implementados** nesta versão.

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

Demonstração sugerida: mostrar o `.mini`; executar e tentar 40, 80 e 65; repetir
com `-O`; demonstrar 101 como palpite recusado e 0 para sair; mudar segredo para
42, verificar o fonte e jogar outra partida. A sequência 40/80/65 só é válida
para o segredo padrão 65. Desfaça personalizações antes de rodar os testes que
usam a configuração padrão, ou atualize expectativas deliberadamente.

## Limites e erros comuns

- Não existe sorteio: o segredo é fixo em cada compilação.
- Não há limite de tentativas nem reinício automático depois de vencer.
- EOF sem escolher sair produz erro com código 1; Ctrl+C retorna 130.
- `No module named miniforge`: execute a partir da pasta `MiniForge/`.
- `uai (palpite)` não é válido: condições exigem booleanos, como `palpite == 0`.
- Se escolher um segredo fora dos limites, o programa compila, mas sua própria
  validação de configuração impede a partida. Não é um erro de tipos.

Veja também a [Calculadora Mineira](../calculadora/README.md) e o
[guia para usar e modificar os dois programas](../README.md).

## Evidência de otimização

Na configuração padrão, o TAC tem 66 instruções antes e 46 depois da otimização,
excluindo rótulos: redução estática de 30,30%. A configuração conhecida permite
simplificar verificações iniciais; os palpites continuam sendo recebidos em
execução. Isso não é medição de velocidade. A forma de medir e os resultados
executados estão no [registro dos programas](../../docs/testes-programas.md).

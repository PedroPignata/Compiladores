# Calculadora Mineira

Aplicação interativa que usa **mineirês**, a linguagem do MiniForge,
para compilar as contas. A interface de teclado é implementada em Python. Autores do projeto: Pedro Dutra, Pedro Pignata, Lucas Rocha Dantas
e Renato Portilho. Disciplina: Compiladores, professora Lorena Bezerra.

## Usar a calculadora interativa

Na pasta `MiniForge/`, execute:

```bash
python3 -m exemplos.calculadora.interativa
```

No Windows ou com ambiente virtual ativo, use `python` no lugar de `python3`.
Não é necessário instalar pytest para abrir a calculadora.
Escolha 1 para soma, 2 para subtração, 3 para multiplicação ou 4 para divisão.
Digite os dois inteiros quando solicitado. A resposta aparece imediatamente;
o menu volta para permitir outra conta. Digite 0 no menu para sair.

Exemplo de sessão (trecho):

```text
Escolha a operação: 1
Primeiro número: 18
Segundo número: 6
Resultado: 18 + 6 = 24
```

Números negativos são aceitos. Entradas como `abc` e `2.5` são rejeitadas e o
mesmo número é solicitado novamente. Divisão por zero mostra uma mensagem e
volta ao menu. Ctrl+C ou fim de entrada encerram sem traceback.
A divisão continua inteira: `-7 / 2 = -3`, pois a linguagem usa `inteirim`.

### Mostrar o trabalho do compilador durante a conta

```bash
python3 -m exemplos.calculadora.interativa --detalhes
```

Esse modo mostra o programa mineirês gerado, o TAC original e o TAC otimizado,
além do resultado. É o modo recomendado para apresentar à professora.
Para 18 + 6, o fonte criado em memória é:

```text
trem primeiro: inteirim = 18;
trem segundo: inteirim = 6;
mostra_so(primeiro + segundo);
```

A interface chama o lexer, o parser, a semântica (pela API de geração), o
gerador TAC e o otimizador reais. Com operandos já conhecidos, os passes
reduzem a expressão e produzem `print 24`. A interface apresenta esse literal.
Ela não calcula a operação por um dicionário de funções Python, não usa `eval`
e não interpreta programas ou saltos TAC. Se o resultado não for uma constante
inteira no formato esperado, a interface reporta falha em vez de recalcular.

**Distinção para explicar na apresentação:** a interação acontece no aplicativo
Python. O programa mineirês gerado recebe literais, não lê teclado. O resultado
vem do dobramento de constantes durante a compilação, não de uma máquina virtual.
A CLI `python -m miniforge` mantém seu comportamento de geração de TAC.
O modo interativo não altera os arquivos `.mini` nem os `.tac` de referência.

## Exemplos fixos em mineirês: objetivo e funcionamento

A calculadora recebe sua configuração nas três primeiras declarações do fonte:
dois números inteiros e um código de operação. O programa seleciona a conta com
condicionais e registra se a solicitação é válida. Nesse exemplo fixo não há leitura pelo teclado.
Altere o arquivo, salve e compile novamente para experimentar outra conta.

Este programa demonstra o uso do compilador, cujo produto é **TAC**, código de
três endereços. O comando `mostra_so` vira uma instrução `print` nesse código.
O MiniForge não executa o TAC: ver `print 24` significa ver uma instrução gerada,
e não uma conta executada pelo programa. O dobramento de constantes pode calcular
uma operação durante a compilação, sem executar o programa inteiro.

## Arquivos

| Arquivo | Finalidade |
|---|---|
| `interativa.py` | Menu, leitura de inteiros, chamada ao compilador e apresentação do literal |
| `calculadora.mini` | Calculadora com seleção e proteção da divisão |
| `constantes.mini` | Contas diretas para demonstrar precedência e otimização |
| `calculadora-original.tac` | TAC da configuração padrão da calculadora |
| `calculadora-otimizado.tac` | Mesmo fonte após os cinco passes |
| `constantes-original.tac` | TAC das contas diretas |
| `constantes-otimizado.tac` | TAC com contas constantes dobradas |

Os `.tac` são evidências de compilação, não fontes aceitos pela CLI. Foram gerados
da versão atual; se modificar os `.mini`, gere novamente os arquivos de referência.

## Preparar o ambiente

No Linux/macOS, a partir da pasta `MiniForge/` (não de `miniforge/`):

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

No Windows, crie o ambiente com `py -m venv .venv` e ative no PowerShell com
`.venv\Scripts\Activate.ps1`. Os próximos comandos usam `python` com esse
ambiente ativo. O compilador só requer Python 3.10 ou superior e biblioteca
padrão. A instalação de pytest é necessária para os testes, não para compilar.

## Escolher a conta

```text
trem primeiro: inteirim = 18;
trem segundo: inteirim = 6;
trem operacao: inteirim = 1;
```

| Código | Conta | Significado matemático com 18 e 6 |
|---|---|---|
| 1 | Soma | 24 |
| 2 | Subtração | 12 |
| 3 | Multiplicação | 108 |
| 4 | Divisão inteira | 3 |
| Outro | Solicitação inválida | Validade falsa, sem resultado |

Esses números são referências calculadas manualmente, não saídas de execução.
A divisão trunca para zero: `-7 / 2` representa `-3`. Não há casas decimais.
O sinal de negativo é o operador unário, não parte do token numérico.

## Entender o fonte

1. `trem` declara variáveis inicializadas; `inteirim` indica inteiros.
2. `resultado` começa em zero. `valido`, do tipo `booleanim`, começa em `eh_memo`.
3. `uai` compara `operacao` com cada código. `sinao` conduz à próxima alternativa.
4. Na divisão, outro `uai` exige `segundo != 0` antes da expressão de divisão.
5. Operação desconhecida ou divisor zero na operação 4 faz `valido = num_eh`.
6. `mostra_so(valido)` representa a indicação de validade. O resultado só é
   representado por `mostra_so(resultado)` quando `valido` é verdadeiro.

Zero é um resultado válido, por isso não serve como código de erro. A variável
booleana separa a validade da resposta numérica. O teste de zero é do **programa**;
o frontend do compilador verifica tipos e não rejeita toda divisão por zero.

## Compilar e inspecionar cada fase

Todos os comandos abaixo partem de `MiniForge/`:

```bash
python -m miniforge exemplos/calculadora/calculadora.mini --verificar
python -m miniforge exemplos/calculadora/calculadora.mini --tokens
python -m miniforge exemplos/calculadora/calculadora.mini --ast
python -m miniforge exemplos/calculadora/calculadora.mini --tipos
python -m miniforge exemplos/calculadora/calculadora.mini --tac
python -m miniforge exemplos/calculadora/calculadora.mini --tac -O
```

`--verificar` confirma ausência de erros. `--tokens` mostra lexemas com posições.
`--ast` mostra o agrupamento sintático; `--tipos` mostra a árvore anotada.
`--tac` representa a seleção com rótulos e saltos. `-O` pode remover os caminhos
que a configuração constante torna inalcançáveis. Sem opções, o padrão é TAC
original. Com `-O` sozinho, o padrão é TAC otimizado.

Para gravar os resultados novamente:

```bash
python -m miniforge exemplos/calculadora/calculadora.mini --tac > exemplos/calculadora/calculadora-original.tac
python -m miniforge exemplos/calculadora/calculadora.mini --tac -O > exemplos/calculadora/calculadora-otimizado.tac
python -m miniforge exemplos/calculadora/constantes.mini --tac > exemplos/calculadora/constantes-original.tac
python -m miniforge exemplos/calculadora/constantes.mini --tac -O > exemplos/calculadora/constantes-otimizado.tac
```

Na configuração padrão o TAC otimizado termina em `print eh_memo` e `print 24`.
No exemplo complementar, as instruções finais são `print 24`, `print 12`,
`print 108`, `print 3`, `print -3`, `print 14` e `print 20`. Compare as duas
últimas: a multiplicação tem prioridade, mas os parênteses mudam o agrupamento.

## Resultados estáticos

Contamos todas as instruções exceto `label`. A redução é
`100 * (antes - depois) / antes`. Não medimos tempo nem instruções executadas.

| Fonte padrão | Antes | Depois | Redução |
|---|---:|---:|---:|
| `interativa.py` | Menu, leitura de inteiros, chamada ao compilador e apresentação do literal |
| `calculadora.mini` | 34 | 8 | 76,47% |
| `constantes.mini` | 19 | 9 | 52,63% |

Na calculadora, constantes permitem escolher a soma e remover alternativas
inalcançáveis. Nas contas diretas, propagação e dobramento substituem operações
por literais e a eliminação retira temporários sem uso. Cópias para variáveis
do usuário podem permanecer: o otimizador é conservador.

## Testar e apresentar

```bash
python -m pytest -q tests/test_calculadora.py tests/test_calculadora_interativa.py
python -m pytest -q
```

Os testes usam fontes configurados em memória para não modificar os exemplos.
Cobrem as quatro operações, números negativos, divisor zero, operação inválida,
TAC de referência, alvos de saltos, idempotência e compilação pela CLI.
São evidências estruturais, sem executor de TAC e sem prova geral de equivalência.

Roteiro sugerido: abrir a interface com `--detalhes`, fazer uma conta e mostrar
as representações geradas; depois mostrar as configurações do exemplo fixo; validar o fonte; abrir tokens e AST
tipada; comparar os dois TAC; trocar operação para 4 e divisor para 0; explicar
o ramo de validade falsa; mostrar a suíte. Mudar um tipo para `booleanim` com
inicializador inteiro demonstra erro semântico com `--contexto` (desfaça depois).

## Limitações e problemas comuns

- A interface interativa é de terminal. Não há interface gráfica nem ponto flutuante.
- A linguagem mineirês não ganhou um comando de entrada: o aplicativo Python prepara o fonte.
- Rode os comandos na raiz `MiniForge/`: em outra pasta pode ocorrer
  `No module named miniforge`. Confirme também o ambiente Python ativo.
- Use `inteirim`, `booleanim`, `uai` e `sinao`, não as palavras de Python.
- Condições exigem booleanos. `uai (operacao)` é inválido; escreva uma comparação.
- Código de saída 0 significa compilação bem-sucedida, não operação válida:
  operação 9 é um programa bem tipado que representa uma solicitação inválida.
- Código 1 indica leitura ou análise com erro. Código 2 indica uso incorreto
  da CLI, como `--tipos -O` sem `--tac`.

Relatório do projeto: [relatorio-final.md](../../docs/relatorio-final.md).

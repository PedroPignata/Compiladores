# Calculadora Mineira

Aplicação escrita em **mineirês**, a linguagem do MiniForge.
O programa é compilado e executado pelo MiniForge. Autores do projeto: Pedro Dutra, Pedro Pignata, Lucas Rocha Dantas
e Renato Portilho. Disciplina: Compiladores, professora Lorena Bezerra.

## Usar a calculadora em mineirês

O programa completo é [interativa.mini](interativa.mini). Execute na pasta
MiniForge/, com Python 3.10+ instalado:

```bash
python3 -m miniforge exemplos/calculadora/interativa.mini --executar
```

O menu é impresso pelo próprio programa. Escolha 1 para soma, 2 para subtração,
3 para multiplicação, 4 para divisão ou 0 para sair. Digite os dois inteiros.
O resultado aparece e o menu volta. Negativos são aceitos, e a divisão trunca
para zero: -7 / 2 resulta em -3. Texto ou decimal no lugar de inteiro gera uma
mensagem e solicita novamente a mesma entrada. Divisor zero gera a mensagem
escrita no fonte e volta ao menu. Fim inesperado da entrada retorna código 1;
Ctrl+C interrompe a execução com código 130.

### Visual do menu

```text
╭────────────────────────────────────────────────╮
│            CALCULADORA MINEIRA, SÔ!            │
├────────────────────────────────────────────────┤
│        [1] Somar          [2] Subtrair         │
│         [3] Multiplicar    [4] Dividir         │
│                    [0] Sair                    │
╰────────────────────────────────────────────────╯
Escolhe a operação aí, sô:
```

Depois dos números, a calculadora mostra `Tá na mão, sô! Resultado:` e o valor.

### Divisão que seria truncada para zero

O programa interativo rejeita uma divisão quando o numerador é diferente de
zero, mas o quociente inteiro seria zero. Por exemplo, `2 / 5`, `-2 / 5` e
`2 / -5` mostram `Resultado inválido, sô! Essa fração num cabe em inteirim.`
e voltam ao menu, sem apresentar um zero enganoso.

`0 / 5` continua sendo zero válido, e `10 / 2` produz 5. A regra geral da
linguagem não foi alterada: outras frações ainda são truncadas (`7 / 2 = 3`).
Essa proteção pertence ao programa `.mini` interativo e não aos exemplos fixos.
Divisor zero continua recebendo mensagem própria: `Uai, dividir por zero num dá, sô!`.

### Onde está cada parte do programa?

- `enquanto_tiver (opcao != 0)` mantém o menu ativo.
- `mostra_so("texto")` imprime as mensagens literais.
- `le_so(opcao)` e `le_so(primeiro)` recebem valores do teclado.
- `uai` e `sinao` validam a opção e selecionam as operações.
- A verificação de `segundo == 0` evita uma divisão inválida.
- `mostra_so(resultado)` apresenta o valor calculado em execução.

A linguagem recebeu `le_so`, que exige uma variável inteira já declarada.
Literais entre aspas duplas só são aceitos em `mostra_so`; não há variáveis
string, concatenação ou interpolação. Menu e lógica estão no `.mini`, não em
uma interface específica escrita em Python. `miniforge/execucao.py` é o executor
genérico do código TAC, implementado em Python como as demais fases.
O antigo `interativa.py`, que gerava contas fechadas, foi removido.

### Compilar, otimizar e executar

```bash
python -m miniforge exemplos/calculadora/interativa.mini --verificar
python -m miniforge exemplos/calculadora/interativa.mini --tokens
python -m miniforge exemplos/calculadora/interativa.mini --ast
python -m miniforge exemplos/calculadora/interativa.mini --tipos
python -m miniforge exemplos/calculadora/interativa.mini --tac
python -m miniforge exemplos/calculadora/interativa.mini --tac -O
python -m miniforge exemplos/calculadora/interativa.mini --executar -O
```

Só `--executar` roda o programa. Os outros comandos permitem estudar cada
representação sem consumir teclado. `--executar` não pode ser combinado com
inspeções como `--tokens` ou `--tac`: a CLI retorna código 2. `-O` é permitido.
Em execução, `read` substitui o valor da variável por um novo inteiro; o
otimizador invalida a constante anterior e preserva a leitura como efeito.
Isso impede que números lidos em rodadas diferentes sejam congelados.

## Exemplos fixos em mineirês: objetivo e funcionamento

A calculadora recebe sua configuração nas três primeiras declarações do fonte:
dois números inteiros e um código de operação. O programa seleciona a conta com
condicionais e registra se a solicitação é válida. Nesse exemplo fixo não há leitura pelo teclado.
Altere o arquivo, salve e compile novamente para experimentar outra conta.

Este programa demonstra o uso do compilador, cujo produto é **TAC**, código de
três endereços. O comando `mostra_so` vira uma instrução `print` nesse código.
Nesse modo de compilação, o MiniForge não executa o TAC: ver `print 24` significa ver uma instrução gerada,
e não uma conta executada pelo programa. O dobramento de constantes pode calcular
uma operação durante a compilação, sem executar o programa inteiro.

## Arquivos

| Arquivo | Finalidade |
|---|---|
| `interativa.mini` | Programa interativo completo escrito em mineirês |
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
| `interativa.mini` | Programa interativo completo escrito em mineirês |
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
Os exemplos fixos têm testes estruturais. O programa interativo tem testes de
execução com e sem otimização, sem constituir prova geral de equivalência.

Roteiro sugerido: executar `interativa.mini`, fazer uma conta e depois mostrar
o TAC em uma chamada separada; depois mostrar as configurações do exemplo fixo; validar o fonte; abrir tokens e AST
tipada; comparar os dois TAC; trocar operação para 4 e divisor para 0; explicar
o ramo de validade falsa; mostrar a suíte. Mudar um tipo para `booleanim` com
inicializador inteiro demonstra erro semântico com `--contexto` (desfaça depois).

## Limitações e problemas comuns

- A interface interativa é de terminal. Não há interface gráfica nem ponto flutuante.
- A linguagem agora possui `le_so` para inteiros; o menu é parte do programa mineirês.
- Rode os comandos na raiz `MiniForge/`: em outra pasta pode ocorrer
  `No module named miniforge`. Confirme também o ambiente Python ativo.
- Use `inteirim`, `booleanim`, `uai` e `sinao`, não as palavras de Python.
- Condições exigem booleanos. `uai (operacao)` é inválido; escreva uma comparação.
- Código de saída 0 significa compilação bem-sucedida, não operação válida:
  operação 9 é um programa bem tipado que representa uma solicitação inválida.
- Código 1 indica leitura ou análise com erro. Código 2 indica uso incorreto
  da CLI, como `--tipos -O` sem `--tac`.

Relatório do projeto: [relatorio-final.md](../../docs/relatorio-final.md).

## Editar e entender a calculadora passo a passo

1. Abra `exemplos/calculadora/interativa.mini` num editor e salve como UTF-8.
2. Localize o trecho a alterar usando o mapa abaixo.
3. Salve e rode `python -m miniforge exemplos/calculadora/interativa.mini --verificar`.
4. Se não houver erro, rode com `--executar` e experimente os casos afetados.
5. Repita com `--executar -O` para conferir a versão otimizada.
6. Rode os testes e mantenha expectativas coerentes com as regras documentadas.

| Parte | Como encontrar | O que pode mudar |
|---|---|---|
| Moldura e menu | Primeiros `mostra_so` dentro do laço | Textos entre aspas, mantendo opções coerentes |
| Leitura da opção | `le_so(opcao);` | A variável precisa continuar inteira e declarada |
| Encerrar | `enquanto_tiver (opcao != 0)` e teste de `opcao != 0` | Se mudar a opção de saída, atualize ambos e o menu |
| Soma | `uai (opcao == 1)` | A expressão atribuída a resultado |
| Subtração | `uai (opcao == 2)` | Idem, respeitando os tipos |
| Multiplicação | `uai (opcao == 3)` | Idem |
| Divisão | Alternativa final e teste `segundo == 0` | Preserve a proteção de zero antes da conta |
| Rejeitar fração truncada | `primeiro != 0` e `resultado == 0` | Regra específica da aplicação, não do compilador |
| Exibir resposta | `uai (valido)` | Mensagem e apresentação do valor |

Exemplo de edição só de texto:

```text
mostra_so("Qual é o primeiro número, sô?");
```

Pode virar `mostra_so("Manda o primeiro inteiro aí, sô:");`, mantendo a leitura
logo depois. Isso não exige alterar lexer, parser ou executor. Não use uma
quebra de linha literal dentro das aspas; adicione outro `mostra_so`.

Para experimentar uma nova operação, não basta criar a opção 5 no menu:
a validação `opcao > 4`, os ramos de seleção, as mensagens, este README e os
testes precisam mudar juntos. A linguagem não tem operador de potência ou
resto, portanto escrever `**` ou `%` não cria esse recurso automaticamente.

Os valores iniciais de `primeiro` e `segundo` no programa interativo são
substituídos por `le_so` a cada rodada. Para configurar contas fixas sem teclado,
use `calculadora.mini`, conforme a seção de exemplos fixos acima.

Próximo programa: [Adivinha o trem, sô!](../adivinha/README.md).
Guia conjunto com instalação, comandos e criação de fontes:
[exemplos/README.md](../README.md).

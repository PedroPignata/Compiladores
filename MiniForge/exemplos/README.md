# Guia dos programas em mineirês

Este guia ensina a **instalar, executar, estudar e modificar** os dois programas
interativos do projeto MiniForge. Todo o comportamento das aplicações está nos
fontes `.mini`. Python implementa o compilador e o executor genérico de TAC.

| Programa | Código | Manual detalhado |
|---|---|---|
| Calculadora Mineira | [calculadora/interativa.mini](calculadora/interativa.mini) | [README da calculadora](calculadora/README.md) |
| Adivinha o trem, sô! | [adivinha/adivinha.mini](adivinha/adivinha.mini) | [README do jogo](adivinha/README.md) |

## 1. Preparar o ambiente

Instale Python 3.10 ou superior e Git. Para obter uma cópia nova:

```bash
git clone https://github.com/PedroPignata/Compiladores.git
cd Compiladores/MiniForge
```

Se o projeto já estiver na sua máquina, abra essa pasta em vez de clonar
novamente. Todos os comandos deste guia partem de **MiniForge/**. Não entre
na subpasta `miniforge/` do pacote nem na pasta de cada programa para rodar a CLI.

Ambiente isolado no Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

No Windows, usando PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

O compilador não precisa de bibliotecas externas para rodar os programas.
A dependência pytest é para os testes. Nos comandos seguintes, `python` deve
ser o Python do ambiente ativado. Sem ambiente, no Linux, use `python3`.

## 2. Abrir e usar a calculadora

```bash
python -m miniforge exemplos/calculadora/interativa.mini --executar
```

Escolha 1 para soma, 2 para subtração, 3 para multiplicação, 4 para divisão ou
0 para sair. Após uma operação válida, digite dois inteiros, um por linha.
A resposta aparece e o menu volta. Negativos são permitidos.

| Experimento | O que observar |
|---|---|
| Operação 1, números 18 e 6 | Resultado 24 |
| Operação 4, números 10 e 2 | Resultado 5 |
| Operação 4, números 2 e 5 | Resultado inválido: a fração seria truncada para zero |
| Operação 4, números 0 e 5 | Zero verdadeiro, portanto válido |
| Operação 4, números 10 e 0 | Mensagem de divisão por zero, retorno ao menu |
| Operação 9 | Opção inexistente, retorno ao menu |

A linguagem tem inteiros, não decimais. A regra de divisão trunca para zero,
por isso `7 / 2` dá 3. A calculadora interativa acrescenta uma proteção para
frações com numerador não nulo e quociente inteiro zero. Não se trata de um
novo tipo numérico. Os exemplos fixos em `calculadora/` não são o programa
interativo: foram mantidos para estudar geração e otimização de contas constantes.

## 3. Abrir e usar o jogo

```bash
python -m miniforge exemplos/adivinha/adivinha.mini --executar
```

O segredo é sorteado entre 1 e 100 a cada partida. Faça palpites e siga as
dicas de maior ou menor até acertar; o jogo mostra quantas tentativas válidas usou.
Digite 0 para abandonar. Texto, decimal e palpites fora do intervalo não contam.
Para uma nova partida, repita o comando. Um mesmo número pode reaparecer por acaso entre partidas.

## 4. Compilar e executar são comandos diferentes

```bash
python -m miniforge exemplos/adivinha/adivinha.mini --verificar
python -m miniforge exemplos/adivinha/adivinha.mini --tac
python -m miniforge exemplos/adivinha/adivinha.mini --tac -O
python -m miniforge exemplos/adivinha/adivinha.mini --executar -O
```

`--verificar` só analisa o programa. `--tac` imprime código intermediário;
`--tac -O` imprime o código otimizado. `--executar` roda o TAC e permite teclado
e saída. `--executar -O` otimiza antes de rodar. Sem opções, o padrão é mostrar
TAC, não abrir o programa. Esses comandos também servem para a calculadora,
substituindo o caminho do arquivo. Não combine `--executar` com `--tac`,
`--tokens`, `--ast`, `--tipos` ou `--verificar`.

Para examinar outras representações:

```bash
python -m miniforge exemplos/calculadora/interativa.mini --tokens
python -m miniforge exemplos/calculadora/interativa.mini --ast
python -m miniforge exemplos/calculadora/interativa.mini --tipos
```

## 5. Como mexer nos programas

Abra o `.mini` em um editor, mantenha UTF-8, edite, salve e compile novamente.
A execução já iniciada usa o código compilado antes da alteração: encerre e
abra outra vez para ver o efeito da edição.

| Objetivo | Onde alterar | Cuidado |
|---|---|---|
| Mudar frases ou moldura | Literais de `mostra_so("...");` nos dois fontes | Não remover aspas e `;`; uma linha por mensagem |
| Sortear o segredo | `segredo = sorteia_so(minimo, maximo);` no jogo | Manter a chamada fora do laço de palpites |
| Mudar intervalo | `minimo` e `maximo` no jogo | Mínimo positivo; 0 é reservado para sair |
| Alterar dica de palpite | Ramos `palpite < segredo` e `palpite > segredo` | Não inverter o sentido da dica |
| Mudar contagem | `tentativas = tentativas + 1;` no jogo | Hoje só conta palpites dentro do intervalo |
| Mudar uma conta | Atribuições a `resultado` na calculadora | Usar inteiros e preservar a validação de zero |
| Mudar saída do menu | Comparações com `opcao` na calculadora | Hoje a opção 0 encerra |

O [manual da calculadora](calculadora/README.md) tem uma seção de edição passo
a passo. O [manual do jogo](adivinha/README.md) inclui exemplos completos de
personalização e o comportamento de configurações inválidas.

## 6. Construir seu próprio programa

As instruções básicas já usadas pelos dois exemplos são suficientes para
muitas aplicações de terminal. Este programa mínimo lê um inteiro e mostra o
dobro:

```text
trem numero: inteirim = 0;
mostra_so("Digite um inteiro, sô:");
le_so(numero);
mostra_so("O dobro desse trem é:");
mostra_so(numero * 2);
```

Salve, por exemplo, em `exemplos/meu_programa.mini`. Depois execute:

```bash
python -m miniforge exemplos/meu_programa.mini --verificar
python -m miniforge exemplos/meu_programa.mini --executar
```

Esse caminho é uma sugestão para seu arquivo, não um terceiro programa entregue.
Use `trem` para declarar antes de ler, `inteirim` para inteiros e `booleanim`
para `eh_memo`/`num_eh`. `uai` e `enquanto_tiver` precisam de condições booleanas
e chaves. Variáveis de bloco deixam de ser visíveis ao sair dele.
Não há funções definidas pelo usuário, strings em variáveis ou números decimais.
O sorteio inteiro existe pela expressão `sorteia_so(minimo, maximo)`. Textos
literais só são aceitos como saída `mostra_so("texto");`.

## 7. Conferir depois de editar

```bash
python -m pytest -q tests/test_calculadora.py tests/test_calculadora_interativa.py tests/test_adivinha.py
python -m pytest -q
```

Os testes dos exemplos usam a configuração padrão. Se personalizar limites,
mensagens ou regras, algumas expectativas podem deixar de corresponder à sua
versão. Restaure o padrão para conferir o projeto original ou atualize os
casos conscientemente, mantendo testes de erros e de comportamento.

Para alterações somente em texto, não modifique lexer ou parser. Para um novo
recurso de linguagem, será necessário definir e testar todas as fases afetadas,
não apenas escrever uma palavra nova no fonte.

## 8. Problemas comuns

- **O programa só mostra instruções:** faltou `--executar`.
- **`No module named miniforge`:** entre em `Compiladores/MiniForge`.
- **`No module named pytest`:** instale `requirements-dev.txt` no mesmo Python.
- **Caminho inexistente:** os caminhos são relativos à pasta em que você está.
- **Entrada inválida:** forneça um inteiro decimal; não use vírgula nem ponto.
- **EOF durante `le_so`:** a entrada acabou antes de o programa terminar; use
  o comando de saída do programa ou forneça os dados que ele solicita.
- **Erro sintático:** confira aspas, parênteses, chaves e ponto e vírgula.
- **Erro semântico:** confira declaração, visibilidade e tipos das variáveis.
- **Símbolos de moldura estranhos:** use terminal e fonte com suporte a UTF-8;
  se necessário, troque só os caracteres das mensagens por `+`, `-` e `|`.

Códigos de retorno: 0 para término normal, 1 para erro de leitura/análise/execução,
2 para argumentos inválidos e 130 para Ctrl+C durante a execução.

## 9. Arquitetura para encontrar cada parte

Os `.mini` e estes READMEs ficam em `exemplos/`. Os módulos do compilador ficam
em `miniforge/`, os testes em `tests/` e os contratos e relatórios em `docs/`.
Os programas usam o mesmo pipeline, sem alterar os outros projetos do repositório.
Consulte a [arquitetura técnica](../docs/arquitetura.md) e o
[README principal](../README.md).

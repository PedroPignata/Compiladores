# MiniForge — compilador de mineirês, sô!

Projeto do grupo **Pedro Dutra, Pedro Pignata, Lucas Rocha Dantas e Renato
Portilho**, disciplina Compiladores 2026.2, professora Lorena Bezerra.
Documentação revisada em 13/11/2026.

O MiniForge compila a linguagem própria **mineirês**: texto, tokens, AST,
análise de nomes e tipos, código de três endereços (TAC) e otimização. A main
atual também executa TAC explicitamente, lê inteiros e sorteia números.
Python implementa o compilador e o executor; os dois programas interativos
estão escritos em mineirês, nos arquivos .mini.

## Instalar e começar

Requer Python 3.10+; o compilador só usa a biblioteca padrão. Para instalar
uma cópia nova, a partir de uma pasta de sua escolha:

```bash
git clone https://github.com/PedroPignata/Compiladores.git
cd Compiladores/MiniForge
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

No Windows, use `py -m venv .venv` e `.venv\Scripts\Activate.ps1` no PowerShell.
Depois da ativação, os comandos usam `python`. Sem ambiente virtual, no Linux,
use `python3`. Pytest é necessário para os testes, não para jogar ou compilar.
Se já tiver o repositório, abra sua pasta MiniForge/ em vez de clonar novamente.

Todos os comandos abaixo partem de **Compiladores/MiniForge/**, não da pasta
miniforge/ do pacote nem das pastas dos programas.

## Os dois programas

| Programa | Comando | Manual |
|---|---|---|
| Calculadora Mineira | `python -m miniforge exemplos/calculadora/interativa.mini --executar` | [Usar e editar](exemplos/calculadora/README.md) |
| Adivinha o trem, sô! | `python -m miniforge exemplos/adivinha/adivinha.mini --executar` | [Jogar e editar](exemplos/adivinha/README.md) |

A calculadora oferece quatro operações e opção 0 para sair. A divisão segue
a regra inteira da linguagem: 7 / 2 dá 3. O próprio programa recusa divisor
zero e numerador não nulo cujo quociente seria truncado para zero, como 2 / 5.
Zero real, como 0 / 5, continua válido.

O jogo sorteia um segredo entre 1 e 100 no início de cada partida. Dá dicas,
conta apenas palpites válidos e aceita 0 para sair. O segredo não muda durante
os palpites; partidas diferentes podem sortear o mesmo número por acaso.

O [guia conjunto](exemplos/README.md) ensina a instalar, rodar, editar as frases,
regras e limites, inspecionar cada fase e criar um novo programa mínimo.
Para rodar TAC otimizado, acrescente `-O` ao comando com `--executar`.

## Linguagem

| Palavra | Significado | Exemplo |
|---|---|---|
| trem | Declara variável inicializada | `trem n: inteirim = 5;` |
| inteirim | Tipo inteiro | `trem x: inteirim = -7;` |
| booleanim | Tipo booleano | `trem ok: booleanim = eh_memo;` |
| eh_memo | Verdadeiro | `ok = eh_memo;` |
| num_eh | Falso | `ok = num_eh;` |
| uai | Condicional | `uai (ok) { mostra_so(1); }` |
| sinao | Alternativa | `uai (ok) { mostra_so(1); } sinao { mostra_so(0); }` |
| enquanto_tiver | Repetição | `enquanto_tiver (n > 0) { n = n - 1; }` |
| mostra_so | Saída de valor ou mensagem literal | `mostra_so("Bão demais!");` |
| le_so | Leitura para variável inteira declarada | `le_so(n);` |
| sorteia_so | Sorteio inteiro inclusivo em execução | `n = sorteia_so(1, 100);` |

Não há coerção entre inteiros e booleanos. Condições precisam de booleanim,
blocos exigem chaves, declarações têm inicializador e comparações não podem ser
encadeadas. `//` inicia comentário. Texto entre aspas só é aceito na saída;
não há variáveis string. Especificação e precedência: [especificacao.md](docs/especificacao.md).

## CLI: compilar, inspecionar ou executar

```bash
python -m miniforge exemplos/fatorial.mini
python -m miniforge exemplos/constantes.mini --tac -O
python -m miniforge exemplos/adivinha/adivinha.mini --verificar
python -m miniforge exemplos/adivinha/adivinha.mini --tipos
python -m miniforge exemplos/adivinha/adivinha.mini --executar -O
```

| Opção | Comportamento |
|---|---|
| Sem opções | Valida e imprime TAC original, sem executar |
| -O | Imprime TAC otimizado no fluxo padrão |
| --tokens | Tokens com posições |
| --ast | AST sintática |
| --tipos | Semântica e AST anotada |
| --verificar | Só validação do frontend e mensagem de sucesso |
| --contexto | Contexto nos diagnósticos semânticos; sozinho mantém geração padrão |
| --tac | Validação e impressão do TAC |
| --tac -O | Validação e impressão do TAC otimizado |
| --executar | Compilação e execução do TAC |
| --executar -O | Compilação, otimização e execução |

Inspeções podem ser combinadas, na ordem tokens, AST, tipos, verificação e TAC.
A fase mais profunda solicitada determina até onde analisar. Uma falha impede
as fases seguintes; saídas de fases anteriores podem já ter sido mostradas.
Com inspeção explícita, TAC só aparece quando --tac também é pedido.
`--tipos --tac -O` é válido; `--tipos -O` é inválido, pois não pede geração.

`--executar` não aceita --tokens, --ast, --tipos, --verificar ou --tac na mesma
chamada. Aceita -O e --contexto. --pilha, --vm-pilha e --stats não existem.

Códigos: 0 para sucesso; 1 para leitura, análise ou erro de execução tratado;
2 para argumentos inválidos; 130 para Ctrl+C durante execução. Diagnósticos
vão para stderr e saídas do programa para stdout. Entrada que não é inteira
é recusada por le_so, que solicita novamente; EOF durante leitura retorna 1.

## Organização

```text
MiniForge/
  miniforge/  tokens.py, lexer.py, ast.py, parser.py, simbolos.py,
              semantica.py, ir.py, otimizador.py, constantes.py,
              execucao.py, __init__.py, __main__.py
  tests/      testes por fase e por programa, casos de referência
  exemplos/   README.md, calculadora/, adivinha/, demais fontes .mini
  docs/       documentação vigente e registros históricos identificados
  README.md, pytest.ini, requirements-dev.txt
```

A árvore segue a separação do roteiro da professora. O nome minilang do exemplo
corresponde ao pacote miniforge. execucao.py exerce o papel de executor/backend
simples de TAC; não há arquivo vm.py copiado do ZIP nem bytecode de pilha.
A correspondência completa está em [arquitetura.md](docs/arquitetura.md).

## Testar e conferir a otimização

```bash
python -m pytest -q
python -m pytest -q tests/test_calculadora.py tests/test_calculadora_interativa.py tests/test_adivinha.py tests/test_sorteio.py
```

A suíte vigente passou com **817 testes**. Ambiente, resultados, comandos e
limitações estão em [testes.md](docs/testes.md). Testes usam o executor real e
controlam o gerador apenas quando precisam de expectativas repetíveis. O uso
normal não fixa semente nem segredo. Não se exige diversidade aleatória como
condição para aprovar testes.

O jogo gera 62 instruções e 48 após otimização, excluindo rótulos (22,58%).
A instrução de sorteio permanece em execução. Medições de todos os exemplos e
convenção de contagem: [otimizacao.md](docs/otimizacao.md). Não são benchmarks
nem contagem de instruções executadas, e não há prova geral de equivalência.

## Documentação e histórico

- [Índice da documentação](docs/README.md).
- [Relatório final atualizado](docs/relatorio-final.md).
- [Especificação](docs/especificacao.md), [gramática](docs/gramatica.md), [arquitetura](docs/arquitetura.md).
- [Execução](docs/execucao.md), [sorteio](docs/sorteio.md), [otimização](docs/otimizacao.md).
- [Demonstração](docs/demonstracao.md), [requisitos](docs/matriz-requisitos.md), [checkpoint](docs/checkpoint.md).
- [Guias dos dois programas](exemplos/README.md).

A tag v0.5-otimizacao-sem-vm preserva a entrega antiga sem executor. A main já
inclui os recursos interativos e aleatórios. Registros com contagens antigas
estão identificados como históricos e não substituem o estado vigente.

Limites: sem funções definidas pelo usuário, floats, vetores, variáveis string,
operadores lógicos, bytecode de pilha ou métricas de desempenho. Fontes patológicos,
profundidade extrema e limites de conversão decimal do Python são limitações
registradas. Apresentações ficam locais e fora do Git.

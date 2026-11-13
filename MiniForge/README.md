# MiniForge - compilador de mineirês, sô

Revisão interativa de **13/11/2026**.
Marco anterior de compilação: **v0.5-otimizacao-sem-vm**.
Pedro Dutra, Pedro Pignata, Lucas Rocha Dantas e Renato Portilho.
Professora Lorena Bezerra, Compiladores 2026.2.

O projeto valida o fonte, gera código de três endereços (TAC) e pode otimizá-lo.
A revisão atual acrescenta entrada e execução explícita para a calculadora
inteiramente em mineirês. A tag v0.5-otimizacao-sem-vm preserva o marco anterior,
sem execução; a main atual inclui o executor descrito em docs/execucao.md.

## Instalar e conferir

Requer Python 3.10+. Dentro de MiniForge/:

```bash
python3 -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\activate
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m miniforge exemplos/fatorial.mini
python -m miniforge exemplos/constantes.mini --tac -O
```

O compilador usa a biblioteca padrão; pytest é dependência de desenvolvimento.
A suíte atual tem **766 testes**, incluindo entrada e execução. Resultado
em docs/testes-calculadora.md.
O registro histórico da integração está em docs/testes.md; a execução atual
está em docs/testes-calculadora.md.

## Linguagem

| Palavra | Papel | Exemplo |
|---|---|---|
| le_so | leitura de inteiro | le_so(n); |
| trem | declaração inicializada | trem x: inteirim = 1; |
| inteirim | inteiro | trem n: inteirim = 5; |
| booleanim | booleano | trem ok: booleanim = eh_memo; |
| eh_memo / num_eh | verdadeiro / falso | ok = num_eh; |
| uai / sinao | condicional | uai (ok) { mostra_so(1); } sinao { mostra_so(0); } |
| enquanto_tiver | repetição | enquanto_tiver (n > 0) { n = n - 1; } |
| mostra_so | comando de saída no TAC | mostra_so(n); |

Sem coerção int/bool. Chaves obrigatórias, comentários //, comparações não
encadeadas. Tipos internos continuam int e bool. Nenhuma extensão de linguagem
foi adicionada: operadores lógicos permanecem proposta futura na gramática.

## Organização e pipeline

```text
MiniForge/
  miniforge/ __init__.py, __main__.py, tokens.py, lexer.py,
             ast.py, parser.py, simbolos.py, semantica.py,
             ir.py, otimizador.py, constantes.py, execucao.py
  tests/     casos e testes por fase
  exemplos/  programas .mini
  docs/      especificacao.md, gramatica.md, arquitetura.md,
             otimizacao.md, matriz-requisitos.md e relatórios
  README.md, pytest.ini, requirements-dev.txt

fonte -> tokens -> AST -> AST tipada -> TAC -> [otimização]
```

A estrutura corresponde ao slide inicial 4/5 (página física 5). O pacote
genérico minilang do exemplo corresponde a MiniForge/miniforge. Não há
exigência de renomear nossa linguagem. O executor atual está em execucao.py; vm.py do ZIP não foi copiado.
Não foram alterados os demais projetos de Compiladores.

## CLI e combinações

Sem opções, gera e imprime TAC original. -O sozinho imprime TAC otimizado.
Essa é a evolução do padrão anterior, que apenas informava sucesso semântico.

| Opção | Comportamento |
|---|---|
| --executar | Compila e executa o TAC; aceita -O, rejeita inspeções combinadas |
| --tokens | Léxico e tokens |
| --ast | Parser e AST sintática |
| --tipos | Semântica e AST anotada |
| --verificar | Só frontend, mensagem de sucesso |
| --contexto | Acrescenta contexto aos diagnósticos semânticos |
| --tac | Frontend e impressão do TAC |
| --tac -O | Frontend e impressão do TAC otimizado |

Inspeções combinadas são cumulativas, na ordem tokens, AST sintática, tipos,
mensagem de verificação e TAC. O pipeline avança até a fase mais profunda
pedida. Saídas de fases anteriores podem aparecer antes de erro posterior.
Com uma inspeção explícita, TAC só aparece se --tac também for pedido.
-O junto de inspeção exige --tac: combinações sem geração são erro de uso 2,
para não ignorar silenciosamente a otimização. --contexto sozinho mantém o
padrão de geração. Há testes das 128 combinações de sete sinalizadores.

0: sucesso; 1: erro de leitura/compilação; 2: argumentos inválidos.
Diagnósticos e avisos vão para stderr; uma fase com erro bloqueia as seguintes.
--pilha, --vm-pilha e --stats são rejeitados. Não há estatísticas de execução.

## Documentação e limites

- [Especificação](docs/especificacao.md), [gramática](docs/gramatica.md).
- [Arquitetura](docs/arquitetura.md), [matriz](docs/matriz-requisitos.md).
- [Otimizações e resultados estáticos](docs/otimizacao.md).
- [Integração e revisão](docs/integracao.md), [testes](docs/testes.md).
- [Demonstração conferida](docs/demonstracao.md).

Há execução explícita de TAC em execucao.py, sem bytecode de pilha.
Não há prova geral de equivalência; os testes exercitam os casos cobertos. O atalho interno parse() pressupõe fonte lexicamente válido;
para compilar arquivos use a CLI. Entradas patológicas, profundidade extrema
e limite decimal do Python continuam limitações. Funções, strings, vetores e
tipos de variável não foram acrescentados; texto literal só é permitido em mostra_so. Apresentações ficam locais, fora do Git.

## Calculadora interativa escrita em mineirês

O programa está em [interativa.mini](exemplos/calculadora/interativa.mini).
O próprio fonte contém menu, leitura dos números, seleção, operações,
tratamento de divisor zero e repetição. O menu tem moldura e mensagens mineiras.
Divisões como 2 / 5 recebem resultado inválido, em vez de exibir zero truncado;
0 / 5 continua válido. A regra inteira da linguagem permanece a mesma. Não há aplicativo Python específico
fazendo as contas ou gerando fontes no lugar do programa.

Na raiz MiniForge/:

```bash
python3 -m miniforge exemplos/calculadora/interativa.mini --executar
```

Escolha 1, 2, 3 ou 4, digite os dois inteiros e veja o resultado. Use 0 no
menu para sair. No Windows ou com ambiente virtual ativo, use `python`.
Para executar TAC otimizado, acrescente `-O`. Para estudar as fases:

```bash
python -m miniforge exemplos/calculadora/interativa.mini --tokens
python -m miniforge exemplos/calculadora/interativa.mini --tipos
python -m miniforge exemplos/calculadora/interativa.mini --tac
python -m miniforge exemplos/calculadora/interativa.mini --tac -O
```

A extensão `le_so(nome);` lê um inteiro para uma variável `inteirim` já
declarada. `mostra_so("texto");` imprime uma mensagem literal. Textos não são
um novo tipo de variável: só são aceitos nessa forma de saída.
O Python implementa o compilador e o executor genérico, enquanto o programa
está escrito em mineirês. Detalhes no [README da calculadora](exemplos/calculadora/README.md)
e em [execução e entrada](docs/execucao.md).

## Exemplos fixos da Calculadora Mineira

O programa [calculadora.mini](exemplos/calculadora/calculadora.mini) usa a nossa
linguagem para selecionar soma, subtração, multiplicação ou divisão inteira.
Altere `primeiro`, `segundo` e `operacao` no início do fonte. Os códigos das
operações são 1, 2, 3 e 4, respectivamente. Há verificação de divisor zero e
indicação booleana de validade. A aplicação não lê dados do teclado: os valores
são configurados no arquivo antes da compilação.

O [README da aplicação](exemplos/calculadora/README.md) explica o programa,
cada decisão, os arquivos TAC de referência, alterações possíveis, testes e
roteiro de apresentação. O [relatório final](docs/relatorio-final.md) descreve
todo o trabalho, da motivação ao otimizador e às evidências da aplicação.

### Obter o projeto e escolher a pasta correta

Para uma instalação nova:

```bash
git clone https://github.com/PedroPignata/Compiladores.git
cd Compiladores/MiniForge
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

Se já tiver o repositório, use a pasta `MiniForge/` do checkout existente.
No Windows, use `py -m venv .venv` e ative com `.venv\Scripts\Activate.ps1`
no PowerShell. Execute os comandos seguintes com o ambiente ativo. Não é preciso
instalar o pacote nem ajustar `PYTHONPATH` para usar a CLI a partir dessa pasta.

### Acompanhar a calculadora pelas fases

```bash
python -m miniforge exemplos/calculadora/calculadora.mini --verificar
python -m miniforge exemplos/calculadora/calculadora.mini --tokens
python -m miniforge exemplos/calculadora/calculadora.mini --ast
python -m miniforge exemplos/calculadora/calculadora.mini --tipos
python -m miniforge exemplos/calculadora/calculadora.mini --tac
python -m miniforge exemplos/calculadora/calculadora.mini --tac -O
python -m miniforge exemplos/calculadora/constantes.mini --tac -O
```

Observe, nessa ordem, a validação, os lexemas com posições, a estrutura dos
comandos, a anotação de tipos, os saltos de seleção e as simplificações.
Na configuração inicial, o TAC otimizado termina em `print eh_memo` e `print 24`.
São instruções do código gerado, não saída de execução da calculadora.
O exemplo de contas diretas também mostra `-7 / 2`, precedência e parênteses.

### Testes e interpretação dos resultados

```bash
python -m pytest -q tests/test_calculadora.py tests/test_calculadora_interativa.py
python -m pytest -q
```

A primeira chamada testa a aplicação; a segunda inclui a suíte do compilador.
Os testes cobrem representações e contratos e agora também sessões reais
de programas mineirês pelo executor, com e sem otimização. Resultado atualizado e ambiente estão em
[registro de testes da calculadora](docs/testes-calculadora.md).

O fonte padrão da calculadora gera 34 instruções e 8 após otimização, redução
estática de 76,47%, excluindo rótulos. As contas diretas passam de 19 para 9,
redução de 52,63%. Não são medidas de desempenho de execução. Arquivos `.tac`
no diretório da aplicação permitem conferir os números e o código linha a linha.

### Dificuldades frequentes

- `No module named miniforge`: entre em `Compiladores/MiniForge` e confirme
  que está usando o Python do ambiente ativado.
- `No module named pytest`: instale `requirements-dev.txt` nesse ambiente.
- Arquivo não encontrado: os caminhos dos exemplos são relativos à pasta atual.
- `--tipos -O` retorna código 2: use `--tipos --tac -O` para pedir geração.
- O programa com operação 9 compila: a escolha inválida é tratada pelo próprio
  programa, não é um erro de tipos da linguagem.
- Divisão não produz decimal: `inteirim` usa divisão truncada para zero.

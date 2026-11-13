# Registro de validação da Calculadora Mineira

Data: 13/11/2026. Linux, Python 3.12.3, pytest 8.4.2.
Ambiente isolado: `/tmp/miniforge-relatorio-venv`, criado para a revisão.
Instalação: `python3 -m venv /tmp/miniforge-relatorio-venv` e
`/tmp/miniforge-relatorio-venv/bin/python -m pip install -r requirements-dev.txt`.
Os comandos abaixo usam `python` para representar o Python desse ambiente.

## Validação inicial dos exemplos fixos

| Comando a partir de MiniForge/ | Resultado real |
|---|---|
| `python -m pytest -q` | 715 passed in 11.42s |
| `python -m pytest -q tests/test_calculadora.py` | 19 passed in 0.43s |
| `python3 -m compileall -q miniforge tests` | Código 0, sem diagnóstico |
| `python3 -m miniforge exemplos/calculadora/calculadora.mini --verificar` | Código 0, mensagem de sucesso léxico/sintático/semântico |
| `python3 -m miniforge exemplos/calculadora/constantes.mini -O` | Código 0, TAC com sete instruções print constantes |

A execução da suíte ocorreu com uma edição local preexistente em
`tests/test_casos.py`: remoção de texto de documentação e alteração de comentário,
sem mudança de asserções. Essa edição foi preservada e não faz parte desta entrega.
Não houve skips ou xfails na saída da suíte.

## O que os 19 novos testes verificam

- Dois testes comparam os quatro arquivos TAC com a geração atual, verificam
  não mutação, idempotência, unicidade de rótulos e destinos de saltos existentes.
- Dez cenários comparam as instruções print otimizadas com expectativas manuais:
  soma, subtração, multiplicação, divisão, sinais negativos, zero como resposta,
  divisor zero e dois códigos de operação inválidos. Não há executor nos testes.
- Um teste verifica as sete contas diretas e a diferença de agrupamento.
- Seis testes invocam a CLI por subprocesso: verificação, tokens, AST, tipos,
  TAC e TAC otimizado. Exigem sucesso, stdout preenchido e stderr vazio.
  O último também compara o texto completo com a referência otimizada.

As divisões inválidas da calculadora são evitadas pela lógica do programa.
Isso não torna divisão por zero um erro semântico geral do compilador.
A suíte anterior continua verificando a preservação de divisões potencialmente
falhas e a não eliminação de efeitos observáveis alcançáveis.

## Medição reproduzível

As referências foram geradas com `gerar_tac`, `otimizar` e `formatar_tac`.
Para repetir a contagem sem implementar execução:

```bash
python - <<'PY'
from pathlib import Path
from miniforge.lexer import Lexer
from miniforge.parser import Parser
from miniforge.ir import gerar_tac
from miniforge.otimizador import otimizar
for nome in ('calculadora', 'constantes'):
    fonte = Path(f'exemplos/calculadora/{nome}.mini').read_text(encoding='utf-8')
    lexer = Lexer(fonte)
    tokens = lexer.tokens()
    assert not lexer.erros
    original = gerar_tac(Parser(tokens).programa())
    novo = otimizar(original)
    a = sum(i.op != 'label' for i in original)
    b = sum(i.op != 'label' for i in novo)
    print(nome, a, b, round(100 * (a - b) / a, 2))
PY
```

Saída medida:

```text
calculadora 34 8 76.47
constantes 19 9 52.63
```

## Alcance

Os resultados comprovam as expectativas dos casos testados e os invariantes
estruturais verificados. Não são prova geral de equivalência, medição de tempo
de execução nem saída de programa mineirês executado. A instalação e a suíte
foram testadas em Linux; não houve validação desta revisão em Windows.


## Validação da interface interativa (13/11/2026)

Mesmo ambiente Python 3.12.3 e pytest 8.4.2.

| Comando | Resultado real |
|---|---|
| `python -m pytest -q tests/test_calculadora_interativa.py` | 25 passed in 0.45s |
| `python -m pytest -q` | 740 passed in 11.81s |
| `python3 -m exemplos.calculadora.interativa --detalhes` | Sessão real em terminal: soma 18 + 6 apresentou 24; divisão 10 / 0 mostrou mensagem e voltou ao menu; divisão -7 / 2 apresentou -3; opção 0 encerrou com código 0 |

Os 25 testes novos verificam dez contas (incluindo inteiro grande), quatro
entradas inválidas na API, rejeição de TAC não reduzido, oito sessões por
subprocesso, modo detalhado e Ctrl+C. A suíte total tem 740 casos, sendo 44 da
aplicação e interface. Os resultados de 715/19 acima registram a revisão anterior.

A interface mostra a constante inteira produzida pelo compilador para um fonte
com operandos literais. A interação foi exercitada; não foi adicionado executor
geral de TAC. O teste que fornece um resultado não dobrado exige falha, garantindo
que a interface não recalcule a operação fora do pipeline para contornar isso.


## Revisão: programa interativo realmente em mineirês

A interface específica interativa.py e seus testes foram substituídos por
interativa.mini e testes das fases e da execução real. O registro anterior de
740 testes descreve a abordagem substituída, não a implementação atual.

Execução completa com Python 3.12.3 e pytest 8.4.2:
`python -m pytest -q`: **754 passed in 12.63s**.

As extensões foram verificadas no lexer, parser, semântica, geração de TAC,
otimizador e executor. Cobertura inclui leitura em variável inteira, nomes
inválidos, mensagens restritas à saída, posição e texto sem fechamento,
sessões das quatro operações com/sem -O, entradas inválidas, repetição,
invalidação de constantes por read, preservação de leitura sem uso, EOF,
divisão por zero e argumentos incompatíveis. As contagens de vocabulário e nós
AST foram atualizadas preservando os testes de correspondência completos.

Segunda execução da revisão interativa: **754 passed in 14.58s**.
Sessão de terminal com --executar -O conferida: soma 18 + 6 apresentou 24,
divisão -7 / 2 apresentou -3 e divisor zero mostrou mensagem e retornou ao menu.

## Revisão de comentários e apresentação do terminal

Foram retiradas referências a aulas, slides e desafios dos comentários dos
módulos, testes e exemplos. Docstrings longas foram substituídas por contratos
curtos. Comentários sobre escopos, invalidação de constantes, posições e efeitos
foram mantidos ou ajustados. Uma comparação das ASTs Python, ignorando docstrings,
confirmou que a lógica dos módulos do compilador não mudou.

A calculadora recebeu menu com moldura e mensagens mineiras. O programa
interativo agora rejeita divisões de numerador não nulo cujo quociente inteiro
seria zero: 2 / 5 e suas variantes de sinal mostram resultado inválido. 0 / 5
continua válido. Não se alterou o operador de divisão da linguagem; a verificação
é feita no próprio fonte mineirês, antes de mostrar o resultado.

Novos cenários foram executados com e sem otimização, incluindo retorno ao menu
e nova conta após uma fração rejeitada. O teste de posição dos tokens do fatorial
foi atualizado para a linha 1, pois o comentário inicial do exemplo foi removido;
a verificação de coluna e EOF foi preservada.

Execução completa: `python -m pytest -q`: **766 passed in 14.66s**.
`python3 -m compileall -q miniforge tests` e `git diff --check`: código 0.
Sessão real com --executar -O confirmou mensagem inválida para 2 / 5,
resultado zero para 0 / 5 e encerramento normal pelo menu.

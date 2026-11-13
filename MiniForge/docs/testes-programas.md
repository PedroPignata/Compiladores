# Validação conjunta dos programas mineirês

## Ambiente e estado inicial

Revisão de 13/11/2026 em Linux, Python 3.12.3, pytest 8.4.2, ambiente
`/tmp/miniforge-relatorio-venv`. Base local `5661019`, main limpa no início.
A base contém a mudança da despedida da calculadora para “Até mais, sô!”.

A primeira execução dos testes dos programas detectou 30 falhas de expectativas
na calculadora: todas ainda exigiam a frase anterior “Inté mais, sô!”. A frase
atual foi preservada e as expectativas atualizadas, mantendo as verificações
de contas, erros e retorno ao menu. Não se tratava de 30 falhas aritméticas.
Os 26 testes do jogo passaram já nessa execução inicial.

## Execução final

Comando na pasta MiniForge/:

```bash
python -m pytest -q
```

Resultado executado: **792 passed in 14.21s**, sem skips ou xfails.
O Python usado foi `/tmp/miniforge-relatorio-venv/bin/python`.

A suíte acrescentou 26 casos em `tests/test_adivinha.py`:

| Grupo | Casos | Evidência |
|---|---:|---|
| Sessões por CLI, com/sem -O | 12 | Acerto direto, dicas, contagem, faixa, entrada inválida, abandono e extremos |
| Segredos personalizados | 3 | 1, 100 e 42, equivalência observada de saídas, não mutação, idempotência e alvos |
| Configuração inválida | 4 | Segredo fora da faixa e limites inválidos, sem solicitar entrada |
| Inspeção por fase | 6 | Tokens, AST, tipos, verificação e TAC original/otimizado sem consumir teclado |
| Fim de entrada | 1 | EOF durante palpite retorna código 1 com diagnóstico |

O executor usado é o de produção, `miniforge/execucao.py`. Não foi criado um
interpretador exclusivo nos testes. A comparação de saídas aplica-se aos casos
cobertos, não constitui prova geral de equivalência de qualquer programa.

## Sessão real de terminal

Comando executado:

```bash
python3 -m miniforge exemplos/adivinha/adivinha.mini --executar -O
```

Entradas: 40, 80 e 65. Saídas conferidas: dica para aumentar, dica para reduzir,
mensagem de acerto, quantidade de tentativas 3 e despedida. Processo encerrou
com código 0. O segredo padrão dessa sessão era 65.

## Métrica estática do jogo

Contagem das instruções de `gerar_tac`, excluindo `label`: **66 antes** e
**46 depois** de `otimizar`, redução estática de **30,30%**. As constantes da
configuração permitem simplificar suas verificações e remover caminhos
inalcançáveis, mas leituras e controle de fluxo da partida continuam presentes.
Não se mediram velocidade nem instruções executadas.

Reprodução da métrica:

```bash
python - <<'PY'
from pathlib import Path
from miniforge.lexer import Lexer
from miniforge.parser import Parser
from miniforge.ir import gerar_tac
from miniforge.otimizador import otimizar
fonte = Path('exemplos/adivinha/adivinha.mini').read_text(encoding='utf-8')
lexer = Lexer(fonte)
tokens = lexer.tokens()
assert not lexer.erros
original = gerar_tac(Parser(tokens).programa())
novo = otimizar(original)
a = sum(i.op != 'label' for i in original)
b = sum(i.op != 'label' for i in novo)
print(a, b, round(100 * (a - b) / a, 2))
PY
```

Resultado: `66 46 30.3`. Alterações no fonte podem mudar essa contagem.

## Organização e limites

A árvore foi comparada ao slide “Estrutura do repositório”, página física 5
(4/5). Pacote, testes, exemplos e documentos permanecem separados. As novas
subpastas de aplicações ficam dentro de exemplos/, sem mover outros projetos.
O papel do executor e a correspondência de nomes estão em arquitetura.md.
O jogo não adicionou funcionalidades ao compilador. Não há sorteio aleatório,
limite de tentativas ou reinício automático. A personalização de segredos e
limites foi exercitada em memória nos testes; não altera o fonte padrão.
Não houve teste desta revisão em Windows.

## Verificações de documentação

`python3 -m compileall -q miniforge tests` e `git diff --check` terminaram com
código 0. Links locais dos READMEs e documentos novos/revisados foram conferidos.
O programa mínimo de dobro ensinado no guia foi compilado e executado em memória:
entrada 18 produziu 36, sem criar outro aplicativo no repositório.

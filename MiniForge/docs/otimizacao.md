# Otimização do TAC vigente

Cada passe devolve (novo_codigo, mudou), sem modificar as instruções recebidas.
otimizar aplica os cinco passes até ponto fixo. O TAC continua tipado e com
posição de origem. A otimização pode anteceder tanto impressão quanto execução.

| Passe | Antes | Depois |
|---|---|---|
| Propagação | x = 5; t1 = x + 1 | x = 5; t1 = 5 + 1 |
| Dobramento | t1 = 2 * 3 | t1 = 6 |
| Salto constante | ifFalse num_eh goto L | goto L |
| Código morto | goto L; print 1; L: | goto L; L: |
| Limpeza | goto L; L: | Sem salto redundante |

## Segurança

A propagação invalida cada destino escrito e esquece constantes em rótulos e
saltos. Não propaga valores anteriores a um laço como se fossem invariantes.
read e random escrevem no destino e são efeitos observáveis, preservados quando
alcançáveis mesmo se seu resultado não for lido. random nunca é dobrado.
Saídas alcançáveis permanecem. Divisão potencialmente falha não é removida por
falta de uso. Divisão por zero não é dobrada. Código comprovadamente inalcançável
pode ser removido. Não existe a regra insegura 0 / x = 0.

constantes.py avalia operações literais com int/bool estritos e as regras da
semântica. Divisão usa módulos e sinais, sem float, inclusive para inteiros grandes.
Não há dependência do executor nesse avaliador ou nos passes. Linhas de origem
acompanham instruções substituídas e a entrada não sofre mutação inesperada.

## Resultados estáticos conferidos em 13/11/2026

Contagem única: instruções TAC **exceto label**. Rótulos são marcadores, não
operações. Redução = 100 * (antes - depois) / antes. Não é medição de tempo,
aceleração ou instruções executadas.

| Fonte em exemplos/ | Antes | Depois | Redução % |
|---|---:|---:|---:|
| adivinha/adivinha.mini | 62 | 48 | 22,58 |
| calculadora/interativa.mini | 68 | 67 | 1,47 |
| calculadora/calculadora.mini | 34 | 8 | 76,47 |
| calculadora/constantes.mini | 19 | 9 | 52,63 |
| constantes.mini | 10 | 3 | 70,00 |
| escopos.mini | 6 | 6 | 0,00 |
| expressao.mini | 5 | 2 | 60,00 |
| fatorial.mini | 10 | 10 | 0,00 |
| if_constante.mini | 7 | 2 | 71,43 |
| if_else.mini | 9 | 4 | 55,56 |
| pao_de_queijo.mini | 18 | 18 | 0,00 |

Todos recebem os cinco passes, mas nem todos os passes mudam cada programa.
Contas fixas oferecem propagação, dobramento e remoção de temporários. Condições
constantes permitem simplificar saltos e caminhos. No jogo, os limites constantes
simplificam validações, mas a única instrução random permanece. Na calculadora
interativa, valores de teclado limitam a redução. Fatorial e laços sem oportunidade
local podem corretamente apresentar redução zero.

## Reproduzir a contagem

Na pasta MiniForge/:

```bash
python - <<'PY'
from pathlib import Path
from miniforge.lexer import Lexer
from miniforge.parser import Parser
from miniforge.ir import gerar_tac
from miniforge.otimizador import otimizar
for caminho in ('adivinha/adivinha.mini', 'calculadora/interativa.mini', 'constantes.mini'):
    lexer = Lexer(Path('exemplos', caminho).read_text(encoding='utf-8'))
    tokens = lexer.tokens()
    assert not lexer.erros
    original = gerar_tac(Parser(tokens).programa())
    novo = otimizar(original)
    a = sum(i.op != 'label' for i in original)
    b = sum(i.op != 'label' for i in novo)
    print(caminho, a, b, round(100 * (a - b) / a, 2))
PY
```

## Validação e limites

Há expectativas de TAC, parametrização de operadores, verificação de rótulos,
origem, não mutação, indicador mudou, ponto fixo e idempotência. As aplicações
também são executadas com/sem otimização em casos controlados. Testes de sorteio
controlam o gerador só quando precisam de respostas exatas; o uso normal sorteia
com SystemRandom. Evidências não são prova geral de equivalência.

O roteiro menciona comparação por execução e métricas dinâmicas. A revisão atual
tem execução, mas não instrumenta número de instruções executadas nem desempenho.
Não se afirma atendimento desses itens de medição. A antiga exclusão de toda
execução descreve só o marco sem-vm, não a main atual. Registros anteriores em
[histórico](historico/README.md); validação vigente em [testes.md](testes.md).

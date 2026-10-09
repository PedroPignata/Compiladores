# Arquitetura e plano do projeto

## Visão completa

O projeto MiniForge implementará a MiniLang em Python 3.10+, por fases. O
produto final compilará fontes `.mini` para código de três endereços (TAC),
que será executado por uma máquina virtual. Não há geração de assembly.

```text
Fonte .mini
    -> lexer.py + tokens.py          -> tokens com linha/coluna
    -> parser.py + ast.py            -> AST
    -> semantica.py + simbolos.py    -> AST validada e tipada
    -> ir.py                        -> TAC
    -> otimizador.py (opcional)      -> TAC otimizado
    -> vm.py                        -> saída do programa
```

Lexer, parser e semântica formam o frontend; geração de TAC e otimizações,
o middle-end; a VM cumpre o papel de backend. A CLI em `__main__.py` coordena
as fases. Hoje ela apenas lê o arquivo UTF-8 e reproduz o texto.

## Responsabilidades e contratos planejados

Os nomes abaixo seguem os slides e orientam a implementação futura; não são
APIs já disponíveis.

| Módulo | Responsabilidade | Contrato planejado |
| --- | --- | --- |
| `tokens.py` | Categorias e reservadas | `TipoToken`, `Token(tipo, lexema, linha, coluna)`, `RESERVADAS` |
| `lexer.py` | Converter texto em tokens | `Lexer(fonte).tokens()`, lista de erros léxicos e EOF |
| `ast.py` | Modelar a árvore | `Programa`, `Decl`, `Atrib`, `Print`, `Bloco`, `If`, `While`, `Binario`, `Unario`, `Num`, `Bool`, `Var` |
| `parser.py` | Reconhecer a gramática | `Parser(tokens).programa()` retorna `Programa`; `ErroSintatico` com posição |
| `simbolos.py` | Resolver nomes em escopos | `Simbolo`, `TabelaSimbolos`: entrar/sair, declarar, buscar |
| `semantica.py` | Validar nomes e tipos | `AnalisadorSemantico` usa Visitor, acumula erros e anota tipos na AST |
| `ir.py` | Linearizar a AST validada | `Instr(op, dest, a1, a2, linha)` e `GeradorTAC` |
| `otimizador.py` | Melhorar TAC | Passes retornam `(novo_codigo, mudou)`; repetição até ponto fixo |
| `vm.py` | Executar instruções | `VM(codigo, saida=print).executar()`, memória, rótulos e contador |

Nós da AST preservarão a linha do fonte para diagnósticos posteriores. O
Visitor poderá começar em `semantica.py` e ser compartilhado com a geração
de TAC quando essa etapa existir. Não precisamos criar uma hierarquia de
classes ou interfaces vazias antes de implementar as fases.

A CLI interromperá o pipeline se houver erros: uma fase só entrega dados
válidos à seguinte. Erros irão para stderr e resultarão em código de saída 1;
sucesso, 0. Erros de argumentos da CLI usam código 2, como padrão do argparse.

## Plano das 11 etapas

Datas abaixo são as do material da disciplina, não novos prazos definidos
para este trabalho. Apesar de hoje ser 09/10/2026, o pedido atual corresponde
à aula 06 fotografada, e não à implementação de símbolos da aula 20.

| Aula / data nos slides | Entrega principal | Marco |
| --- | --- | --- |
| 06 · 21/08 | Especificação, gramática inicial, módulos, 5 exemplos, CLI de eco | `v0.0-spec` |
| 08 · 28/08 | Lexer manual, tokens, pelo menos 8 testes e `--tokens` | Commit do lexer inicial |
| 10 · 04/09 | Análise de lexer didático, recuperação e pelo menos 3 testes de erro | `v0.1-lexer` |
| 12 · 11/09 | Gramática refinada, FIRST, derivação, pelo menos 8 casos válidos e 8 inválidos | Commit da gramática |
| 14 · 18/09 | Parser, AST, testes de precedência e associatividade, `--ast` | Commit do parser |
| 16 · 25/09 | Integração lexer/parser/AST, autoavaliação e demonstração de 3 minutos | `v0.2-checkpoint` |
| 20 · 09/10 | Tabela de símbolos e resolução de nomes | Commit dos símbolos |
| 22 · 16/10 | Tipos, AST tipada e mensagens sem erros em cascata | `v0.3-semantica` |
| 26 · 30/10 | TAC com temporários, rótulos e saltos, `--tac` | Commit do TAC |
| 28 · 06/11 | VM, erros de execução, testes ponta a ponta, `--stats` | `v0.4-vm` |
| 30 · 13/11 | Cinco passes, `-O`, equivalência e tabela comparativa | `v0.5-otimizacao` |

O material vincula a comparação de otimizações ao artigo e à apresentação
da A2 de 27/11. Resultados deverão ser medidos na nossa implementação; os
números dos slides são exemplos, não resultados do MiniForge.

## Cuidados que orientam as próximas fases

1. Ler o identificador inteiro antes de consultar reservadas; reconhecer
   operadores de dois caracteres antes dos de um caractere.
2. Comparações não associativas e chaves obrigatórias devem continuar iguais
   na especificação, na gramática e nos testes.
3. Analisar o inicializador antes de declarar o nome; permitir sombreamento e
   impedir redeclaração no mesmo escopo.
4. Ao gerar TAC, dar identidade própria a cada variável declarada. A memória
   plana mostrada nos slides não distingue dois `x` de escopos diferentes.
   Usar nomes internos únicos também evitará colisões com temporários `t1`.
5. Fazer divisão truncada para zero sem converter inteiros grandes para float.
   O exemplo `int(a / b)` dos slides pode perder precisão em inteiros grandes.
6. Ao otimizar, esquecer constantes nos limites de fluxo, preservar a saída
   e os erros de execução e nunca eliminar uma divisão por zero observável.

## Checklist da primeira entrega

- [x] Pastas e um módulo reservado por fase.
- [x] Especificação com tipos, comandos, operadores, precedência e escopos.
- [x] Gramática com uma regra para cada construção e expressões.
- [x] Três exemplos válidos e dois inválidos com erro comentado.
- [x] CLI que lê e imprime o arquivo.
- [x] README com objetivo e instruções.

A publicação exige commit, tag `v0.0-spec` e push. A presença desses marcos
no GitHub deve ser verificada no remoto; os arquivos locais não comprovam
que a publicação ocorreu.

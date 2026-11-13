# Checkpoint atual do MiniForge

Revisão documental de 13/11/2026. A main contém o frontend, geração e otimização
de TAC e execução explícita de programas mineirês.

## Recursos implementados

- Tokens com posições, recuperação léxica, parser, AST e verificação de tipos.
- Escopos, sombreamento e diagnósticos sem cascata.
- TAC com temporários, nomes internos, rótulos, origem e cinco passes até ponto fixo.
- Entrada inteira por le_so, mensagens literais e saída de valores.
- Sorteio inclusivo por sorteia_so, realizado somente em execução.
- Executor de TAC em execucao.py, chamado apenas com --executar.
- Calculadora interativa e jogo com segredo aleatório, ambos escritos em .mini.

## Verificação e organização

Resultado vigente: [testes.md](testes.md). Correspondência com o roteiro:
[matriz-requisitos.md](matriz-requisitos.md). Pastas e interfaces:
[arquitetura.md](arquitetura.md). Comandos de demonstração:
[demonstracao.md](demonstracao.md). Manual de edição dos programas:
[exemplos/README.md](../exemplos/README.md).

Não há bytecode de pilha, funções definidas pelo usuário, números decimais,
vetores, variáveis string ou operadores lógicos. Não há prova geral de
equivalência nem medição de aceleração. Apresentações ficam locais, fora do Git.

A tag v0.5-otimizacao-sem-vm registra o marco anterior. A execução e o sorteio
foram incorporados depois e já fazem parte da main; não são entregas futuras.
Não há afirmação de apresentação presencial realizada.

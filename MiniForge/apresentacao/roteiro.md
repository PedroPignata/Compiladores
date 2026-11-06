# Roteiro da apresentação até a semântica

Tempo sugerido: 10 minutos de fala e 3 de demonstração. Divisão sugerida, a combinar pelo grupo: Pedro Dutra (1–3), Pedro Pignata (4–6), Lucas Rocha Dantas (7–9), Renato Portilho (10–12 e demonstração).

## 1. MiniForge

Apresentar o grupo e o corte da entrega. O trabalho continua a versão do colega. Esta publicação integra o frontend até 16/10, mantendo o mineirês. Não demonstrar resultados executados.

## 2. A linguagem própria do grupo

Explicar as nove reservadas, escritas sem acento. Os nomes ingleses dos slides são equivalências conceituais. Não são palavras reservadas do mineirês. O compilador usa int/bool internamente.

## 3. O corte desta entrega

Diferenciar data real da integração, 06/11, do corte acadêmico em 16/10. Não alegar entregas ou datas de commits que não ocorreram. Representar print e while na árvore é tarefa do frontend.

## 4. Arquitetura do frontend

Percorrer os contratos na ordem. Texto vira tokens com posição, tokens viram AST e a semântica anota tipos. Uma falha impede as fases seguintes. A CLI entregue não importa IR, VM ou otimizador.

## 5. Texto e tokens

Usar trem n como exemplo. Mostrar lexema e tipo distintos. O lexer lê a palavra inteira antes de consultar RESERVADAS. enquanto_tiver2 é ID. <= vem antes de <. Erros são acumulados e a CLI bloqueia o parser.

## 6. Gramática, parser e AST

Explicar uma função por regra e FIRST distintos. O parser usa laços em soma e termo para associar à esquerda. Multiplicação liga mais forte. Chaves obrigatórias evitam else pendente. a < b < c é rejeitado.

## 7. Nomes e escopos

Explicar a pilha global e interna. A busca vai do topo para a base. Ao sair do bloco o x externo volta. Redeclaração no mesmo nível falha. Visitar o inicializador antes de inserir o símbolo evita autorreferência sem nome externo.

## 8. Regras semânticas e tipos

Enumerar as cinco regras: declarar antes de usar, não redeclarar, inicialização e atribuição compatíveis, condições booleanas e operadores válidos. Nenhuma coerção bool/int do Python passa pela tabela REGRAS.

## 9. A AST anotada

Mostrar a árvore antes e depois. O parser cria as expressões com tipo None. Cada visitante retorna o tipo e anota no.tipo. A apresentação usa inteirim/booleanim, mas os valores internos são int/bool. Verificar tipo não calcula o valor da expressão.

## 10. Diagnósticos sem cascata

Uma expressão inválida retorna None e os operadores externos não repetem o erro. Ambos os filhos ainda são visitados para detectar falhas independentes. Mostrar os três erros do exemplo solicitado. Avisos e contexto são adicionais.

## 11. Testes e demonstração

Resultado real da segunda execução: 377 passed em 9,87 segundos, Python 3.12.3 e pytest 8.4.2 no Linux. O tempo varia. 42 casos divididos em 11 válidos, 13 sintáticos inválidos e 18 semânticos. Rodar os comandos e explicar que tudo certim não imprime 120.

## 12. Continuidade do mesmo projeto

O ZIP permanece como referência completa. A próxima integração será a de TAC, depois VM e otimizações, com testes próprios. Não reimplementar o trabalho por preferência. Não há resultados finais nem artigo nesta entrega. Encerrar e abrir perguntas.

Demonstração reproduzível: ../docs/demonstracao.md.

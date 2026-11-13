# Matriz vigente de requisitos e evidências

Referência acadêmica: Compiladores_2026-2_Aulas_Praticas_Projeto.pdf.
A aula inicial usa o nome genérico MiniLang; o grupo usa MiniForge para o
compilador e mineirês para a linguagem. A main atual inclui execução e sorteio,
autorizados depois do marco v0.5-otimizacao-sem-vm.

| Requisito / referência | Implementação vigente | Situação e evidência |
|---|---|---|
| Organização, aula 06, p.5 física (4/5) | miniforge/, tests/, exemplos/, docs/, README | Atendido com o nome do grupo; árvore em arquitetura.md |
| Especificação e EBNF | especificacao.md e gramatica.md | Atualizadas com le_so, mensagens e sorteia_so |
| Frontend, aulas 08–22, pp.7–41 | tokens, lexer, AST, parser, símbolos e semântica | Implementado; regressões e diagnósticos testados |
| Escopos e tipos | simbolos.py e semantica.py | Redeclaração, sombreamento, inicializador, condições e operadores testados |
| TAC, aula 26, pp.42–46 | ir.py | Identidades, temporários, rótulos e origem; testes estruturais |
| Execução, aula 28, pp.47–51 | execucao.py | Executor/backend simples de TAC; papel da VM, sem copiar vm.py |
| Cinco passes, aula 30, pp.52–56 | otimizador.py e constantes.py | Contrato (novo_codigo, mudou), efeitos, divisões, ponto fixo e idempotência |
| Comparação antes/depois, p.56 | otimizacao.md e testes de execução | Medidas estáticas; sessões originais/otimizadas nos casos cobertos |
| Instruções executadas e desempenho, p.56 | Não instrumentados | Sem alegação de aceleração ou conformidade com métricas dinâmicas |
| Bytecode/VM de pilha, desafio p.46 | Não implementado | Recurso adicional excluído; não é necessário para os programas atuais |
| Extensões lógicas opcionais | Não implementadas | Não constam da gramática efetiva; sem promessa de entrega futura |
| Aplicações solicitadas posteriormente | Calculadora e jogo em exemplos/ | Programas em mineirês, READMEs próprios e guia conjunto |
| Aleatoriedade solicitada posteriormente | sorteia_so e random | Integrados em todas as fases, preservados com -O; test_sorteio.py |
| CLI e instruções | __main__.py e READMEs | Default TAC; execução explícita; combinações e códigos conferidos |

## Adaptações e alcance

O corte antigo sem backend foi substituído pelo pedido de programas interativos.
A execução atual é real e genérica, não um aplicativo Python específico de cada
programa. O nome execucao.py tem correspondência de responsabilidade com a VM
dos slides. A árvore mantém as pastas solicitadas; não se afirma equivalência
literal de nomes de módulos auxiliares adicionais.

Os testes de execução com/sem otimização reforçam os casos cobertos, mas não
provam equivalência geral de qualquer TAC. Não há contagem dinâmica, benchmark,
bytecode de pilha ou artigo final da A2. Essas limitações permanecem explícitas.

A calculadora rejeita numerador não nulo dividido para quociente inteiro zero
como regra da aplicação. O jogo sorteia uma vez por partida. Nenhuma dessas
regras deve ser confundida com alteração do operador / ou sorteio em compilação.

Registros dos cortes anteriores: [integração histórica](historico/integracao-v0.5.md).
Evidência vigente: [testes.md](testes.md). Resultados estáticos:
[otimizacao.md](otimizacao.md).

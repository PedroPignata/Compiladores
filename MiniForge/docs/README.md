# Documentação do MiniForge

Documentação da main com compilação, otimização, execução de TAC, entrada,
mensagens literais e sorteio inteiro. Aplicações: Calculadora Mineira e
Adivinha o trem, sô!, com segredo aleatório por partida.

PDF para entrega: [Projeto Final](../projeto-final/README.md), com documentação,
arquitetura e capturas da versão indicada na pasta.

## Estado vigente

| Documento | O que consultar |
|---|---|
| [README principal](../README.md) | Instalação, comandos e visão geral |
| [Guia dos programas](../exemplos/README.md) | Rodar, editar e construir programas mineirês |
| [Especificação](especificacao.md) | Vocabulário, tipos, operadores, escopos e limites |
| [Gramática](gramatica.md) | EBNF e decisões do parser |
| [Arquitetura](arquitetura.md) | Pastas, fases e interfaces |
| [Lexer](analise-lexer.md) | Reconhecimento, posições e recuperação |
| [Execução](execucao.md) | Entrada, saída, TAC e códigos de término |
| [Sorteio](sorteio.md) | Contrato e preservação de aleatoriedade com -O |
| [Otimização](otimizacao.md) | Passes e medições estáticas atuais |
| [Testes](testes.md) | Última validação e alcance das evidências |
| [Demonstração](demonstracao.md) | Comandos e cenários para apresentação |
| [Matriz de requisitos](matriz-requisitos.md) | Correspondência com os slides e adaptações |
| [Revisão documental](revisao-documental.md) | Escopo, correções e verificações desta revisão |
| [Checkpoint](checkpoint.md) | Estado consolidado da entrega |
| [Integração](integracao.md) | Evolução, reaproveitamento e publicação |
| [Relatório final](relatorio-final.md) | Relatório acadêmico da implementação atual |

## Registros históricos

Os documentos abaixo preservam comandos, métricas e decisões das revisões
em que foram produzidos. Opções removidas ou escopos anteriores não são
instruções para rodar a main atual.

- [Integração até otimização](relatorio-entrega.md): marco sem execução.
- [Revisões da calculadora](testes-calculadora.md): evolução dos primeiros testes.
- [Primeiro jogo](testes-programas.md): versão com segredo fixo.
- [Integração do sorteio](testes-sorteio.md): evidências da revisão aleatória.
- [Histórico detalhado](historico/README.md): relatório evolutivo e registros originais.

A tag `v0.5-otimizacao-sem-vm` é histórica e não inclui os recursos interativos
da main. Não se deve fazer checkout dessa tag esperando executar os dois programas.
Os resultados de 696, 715, 740, 754, 766 e 792 testes pertencem a revisões antigas.
O registro vigente está em testes.md; números históricos não foram reapresentados
como execuções novas.

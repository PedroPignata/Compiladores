# Integração e continuidade do MiniForge

## Base do grupo

O MiniForge é um único projeto do grupo: Pedro Dutra, Pedro Pignata, Lucas
Rocha Dantas e Renato Portilho. A versão completa do colega, preservada no ZIP
MiniForge-v0.6-mineires.zip, forneceu a identidade mineirês e implementações
reaproveitadas na continuidade. A base antiga não foi imposta à versão do grupo.
O ZIP original não foi alterado nem duplicado dentro da entrega.

## Evolução publicada

| Marco | Conteúdo e referência |
|---|---|
| Estrutura e especificação | Histórico inicial preservado em v0.0-spec |
| Frontend mineirês | v0.3-semantica, PR #1 |
| TAC e otimização | v0.5-otimizacao-sem-vm; PR #2 integrado na main, 749a919 |
| Calculadora e relatórios | 6622ed8 |
| Primeiro aplicativo interativo em Python | 197abf4, posteriormente substituído |
| Aplicação mineirês com entrada e executor | ef5e047, removeu interativa.py |
| Comentários e visual do terminal | 81d07a7; despedida ajustada depois em 5661019 |
| Jogo e guias dos programas | 0141d49 |
| Sorteio integrado à linguagem e ao jogo | 7e1408a |

A tabela registra fatos do histórico; não representa datas de entregas
retroativas nem autoria individual de trechos. A main atual inclui execução
e aleatoriedade. A tag cujo nome termina em sem-vm continua apontando ao marco
antigo e não foi sobrescrita.

## Reaproveitamento e adaptações

Foram preservados vocabulário, tipos internos, Visitor, organização por fase,
créditos e implementações válidas do grupo. O gerador TAC e os cinco passes
vieram da referência completa. A dependência do otimizador de vm.OPS foi
substituída por constantes.py; isso permite compilar/otimizar sem importar o
executor. A API pública de TAC valida semântica; os cálculos literais distinguem
bool de int e a divisão usa inteiros sem conversão intermediária para float.

Na revisão interativa, leitura, mensagens e execução passaram a ser requisitos.
Leitura e Mensagem foram integradas ao frontend, read/texto ao TAC e execucao.py
passou a executar instruções. O jogo aleatório acrescentou Sorteio e random nas
mesmas fases. Os passes preservam entrada, sorteio e falhas alcançáveis.
Não foi copiado vm.py nem bytecode de pilha do ZIP.

## Organização e publicação

A estrutura continua pacote em miniforge/, testes em tests/, programas e seus
manuais em exemplos/, documentos técnicos em docs/ e README na raiz MiniForge/.
O README da raiz Compiladores apresenta os projetos separados. Cada projeto
mantém linguagem e instruções próprias.

A documentação atual foi consolidada para não descrever a main como sem execução
nem o jogo como fixo em 65. Registros anteriores estão identificados no
[índice](README.md) e no [histórico](historico/README.md).
Os commits são publicados sem force push. O trabalho não inclui apresentações
versionadas, credenciais, ambientes ou caches.

## Referências locais

- ZIP: SHA-256 b00b4d7085e3faf74efbb63c33ec6739f827194210204b0e9ef139de84f3a6f8.
- PDFs da professora Projeto.pdf e Projeto-1.pdf: cópias idênticas na análise
  inicial, SHA-256 d8acb1bb5d3ecd479f344be3a7148f4c274f0ea728ec018956b15f10be19485c.
- Documentos com sufixo (1) não estavam disponíveis na integração inicial;
  foram usados os anexos efetivamente existentes, conforme registro histórico.

Guia de uso: [README principal](../README.md). Estado validado:
[testes.md](testes.md). O restante do ZIP não é incorporado automaticamente:
um novo recurso precisa de contrato, implementação e testes próprios.

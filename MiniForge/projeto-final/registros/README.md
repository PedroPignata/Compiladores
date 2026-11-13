# Registros das evidências do Projeto Final

Capturas de 13/11/2026, código de referência 71c0eae. O arquivo
[manifesto.json](manifesto.json) guarda os comandos, entradas e códigos de retorno.

| Registro | Método e resultado |
|---|---|
| [01-calculadora.txt](01-calculadora.txt) | Pseudoterminal real; operação 1, valores 18 e 6, saída 0; código 0 |
| [02-calculadora-fracao.txt](02-calculadora-fracao.txt) | Pseudoterminal com -O; operação 4, valores 2 e 5, saída 0; código 0 |
| [03-jogo.txt](03-jogo.txt) | Pseudoterminal com -O, SystemRandom normal; palpites 1 a 15 e acerto; código 0 |
| [04-tac.txt](04-tac.txt) | stdout do TAC original; código 0 |
| [04-tac-otimizado.txt](04-tac-otimizado.txt) | stdout do TAC otimizado; código 0 |
| [05-diagnosticos.txt](05-diagnosticos.txt) | stderr semântico com contexto; código 1 intencional |
| [06-testes.txt](06-testes.txt) | pytest real; 817 passed in 12.42s, código 0 |

Nos pseudoterminais, os números ecoados são entradas fornecidas ao processo.
Nenhuma semente ou resposta fixa foi injetada no jogo desta captura. Como os
palpites foram crescentes, o número de tentativas confirma o segredo 15 daquela
partida. Os testes unitários podem controlar o gerador, mas essa sessão não o fez.

Os PNGs são capturas de um visualizador HTML local contendo esses registros.
O print do jogo inclui o início e o fim com uma indicação explícita de omissão;
este TXT preserva a sessão inteira. Os outros prints mostram o registro completo.
O print de TAC combina os dois arquivos correspondentes, sem mudar suas linhas.

O PDF final foi renderizado em PNG e todas as suas 18 páginas foram inspecionadas.
A conferência estrutural encontrou seis imagens e nenhum texto fora das margens.
Não houve inspeção em PowerPoint, que não participa deste documento.

O ambiente do compilador é Python 3.12.3. A suíte usou pytest 8.4.2 no ambiente
isolado indicado no manifesto. Durações são as observadas nesta execução, não
promessas de tempo de teste ou benchmarks do compilador. Os documentos canônicos
registram outras rodadas do mesmo código com durações diferentes.

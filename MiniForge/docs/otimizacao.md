# Otimização do TAC - entrega 13/11/2026

Versão v0.5-otimizacao-sem-vm. Cada passe recebe uma lista e devolve
(novo_codigo, mudou), sem modificar as instruções da entrada. A aplicação
repetida termina em ponto fixo: operações viram cópias, operandos viram
constantes, saltos se simplificam e instruções redundantes desaparecem.

| Passe | Exemplo antes | Depois |
|---|---|---|
| Propagação | x = 5; t1 = x + 1 | x = 5; t1 = 5 + 1 |
| Dobramento | t1 = 2 * 3 | t1 = 6 |
| Salto constante | ifFalse num_eh goto L | goto L |
| Código morto | goto L; print 1; L: | goto L; L: |
| Limpeza | goto L; L: | sem salto redundante |

## Segurança

A propagação invalida cada destino escrito e esquece constantes em rótulos
e saltos. Não atravessa junções ou laços presumindo valores de entrada.
A remoção de temporários não lidos mantém divisões cujo divisor pode ser zero.
Uma divisão alcançável por zero não é dobrada nem removida; uma operação
comprovadamente inalcançável após salto incondicional pode desaparecer.
Saídas alcançáveis permanecem. Não há regra 0/x = 0 nem outras identidades
algébricas arriscadas. Linhas de origem acompanham instruções substituídas.

constantes.py avalia somente operações literais, sem memória, contador de
programa, saltos ou execução de TAC. Usa int/bool estritos e as regras
semânticas do frontend. Divisão usa módulos e sinais, sem float, inclusive
para inteiros grandes. Bytecode e backend não fazem parte deste módulo.

## Resultados estáticos medidos nesta versão

Convenção única: número de instruções TAC **sem rótulos**. Rótulos são
marcadores, não operações. Não se medem instruções executadas nem aceleração.
Redução = 100 * (antes - depois) / antes.

| Programa | Antes | Depois | Redução % |
|---|---:|---:|---:|
| constantes.mini | 10 | 3 | 70.0 |
| escopos.mini | 6 | 6 | 0.0 |
| expressao.mini | 5 | 2 | 60.0 |
| fatorial.mini | 10 | 10 | 0.0 |
| if_constante.mini | 7 | 2 | 71.43 |
| if_else.mini | 9 | 4 | 55.56 |
| pao_de_queijo.mini | 18 | 18 | 0.0 |

Os cinco passes são aplicados em todos os programas; nem todos produzem
mudanças em cada caso. Constantes/expressões envolvem propagação, dobramento
e remoção de temporários; condicionais constantes permitem ainda simplificar
saltos, eliminar caminhos mortos e limpar rótulos. Fatorial e laços variáveis
podem não oferecer ganho seguro com passes locais.

Validação: TAC esperado em casos pequenos, testes parametrizados de operações,
limites de fluxo, origem, não mutação, alvos válidos, idempotência e regressões.
Essas evidências estruturais não constituem prova geral de equivalência
semântica. A comparação de saída por execução usada no slide p.56 foi excluída
pelo pedido; não há VM nem executor substituto. A tabela não contém resultados
copiados da apresentação completa do colega.

# Entrada e execução de programas mineirês

## Mudança de escopo em 13/11/2026

O marco `v0.5-otimizacao-sem-vm` terminava na otimização. A solicitação posterior
foi uma calculadora verdadeiramente escrita em mineirês, com teclado e resultado.
Para atender a isso, a revisão atual adiciona entrada, mensagens e um executor de
TAC em `miniforge/execucao.py`. Trata-se de uma extensão real de execução/backend,
não apenas de uma interface Python. O código da calculadora é
`exemplos/calculadora/interativa.mini`. O aplicativo Python específico foi removido.

## Contrato da linguagem

- `le_so(nome);` exige um nome já declarado com tipo `inteirim`. Lê uma linha
  decimal, com sinal opcional, e atribui o inteiro à variável. Espaços externos
  são ignorados. Entrada inválida gera diagnóstico em stderr e repete a leitura.
  EOF durante leitura é erro de execução. Ler não conta como uso do valor antigo.
- `mostra_so("mensagem");` aceita texto entre aspas duplas, em uma única linha.
  O texto é literal: não possui escapes, interpolação ou concatenação. Acentos
  e `//` dentro das aspas são conteúdo. Aspa sem fechamento é erro léxico.
  A mensagem é comando, não expressão de um novo tipo. Variáveis continuam
  limitadas a inteiro e booleano.
- `mostra_so(expr);` preserva seu comportamento para valores inteiros/booleanos.

Novos nós AST: `Leitura(nome)` e `Mensagem(texto)`. A semântica verifica nome
e tipo na leitura e aceita a mensagem literal. O TAC usa `read destino` e
`texto 'mensagem'`, preservando a linha de origem. O texto fica no campo dest
para não ser confundido com operando variável pelos passes existentes.

## Execução explícita

```bash
python -m miniforge exemplos/calculadora/interativa.mini --executar
python -m miniforge exemplos/calculadora/interativa.mini --executar -O
```

Sem `--executar`, o padrão continua imprimir TAC. Inspeções como `--tokens`,
`--ast`, `--tipos`, `--verificar` e `--tac` não podem acompanhar `--executar`
(código 2). `-O` otimiza antes de executar e é permitido nesse modo.
As análises sempre ocorrem antes de qualquer leitura ou saída do programa.

O executor recebe TAC válido, mantém memória de nomes internos, indexa rótulos
e avança um contador de instruções. Executa cópias, operações, leitura, saída,
saltos, rótulos e sorteio random. Os tipos e os escopos já foram verificados; identidades internas
preservam o sombreamento. A aritmética compartilha as regras de `constantes.py`,
inclusive divisão truncada para zero, sem float. Divisão por zero gera diagnóstico
com linha do fonte. EOF gera código 1; Ctrl+C é tratado pela CLI, com código 130.
A saída usa flush para os prompts aparecerem antes de esperar pelo teclado.
Laços infinitos do fonte continuam sendo laços infinitos; não há limite artificial.

## Segurança das otimizações com entrada

`read` escreve no destino, portanto invalida a constante previamente conhecida.
Também é um efeito observável e pode falhar por EOF: não pode ser eliminado
porque o valor lido não foi usado. Código inalcançável pode ser removido.
Mensagens alcançáveis permanecem. Os limites de bloco continuam impedindo
propagação incorreta em laços e junções.

## Testes e limites

A suíte contém sessões de execução com e sem otimização, múltiplas contas,
leitura inválida, EOF, divisão por zero e testes estruturais das novas fases.
Os testes anteriores do frontend e do otimizador permanecem. As expectativas
de vocabulário e quantidade de nós AST foram atualizadas para os recursos novos.
Não há bytecode de pilha, JIT, tempo de execução medido ou prova geral de
equivalência. O executor novo não é uma cópia do `vm.py` do ZIP e esse arquivo
continua ausente. Documentos de integração anteriores registram o escopo histórico.


## Sorteio na versão vigente

O executor também interpreta random para sorteia_so. Essa operação usa os
limites avaliados em execução e não é dobrada pelo otimizador. Contrato em
[sorteio.md](sorteio.md). Validação atual em [testes.md](testes.md); a tag
sem-vm citada no histórico não contém este executor.

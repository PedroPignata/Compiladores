# Validação da revisão aleatória

> **Registro histórico.** Registro executado na integração do sorteio em 7e1408a. A validação documental mais recente está em testes.md.
> Documentação vigente: [índice](README.md), [relatório final](relatorio-final.md) e [testes](testes.md).


Data: 13/11/2026. Linux, Python 3.12.3, pytest 8.4.2.
Ambiente: `/tmp/miniforge-relatorio-venv`.

## Suíte completa

Comando na raiz MiniForge/:

```bash
python -m pytest -q
```

Resultado executado: **817 passed in 15.31s**, sem skips ou xfails.
Os 792 casos da revisão anterior foram adaptados quando dependiam do segredo
fixo e continuam cobrindo o jogo e a calculadora. A nova reservada acrescentou
um caso no teste parametrizado de vocabulário e test_sorteio.py tem 24 casos.
O teste de correspondência entre nós AST e visitante foi ampliado para Sorteio.
Não foram retiradas asserções de tipos, erros, dicas ou contagem.

## Cobertura do sorteio

- Token, vírgula, posição e identificador que começa com sorteia_so.
- Dois argumentos, precedência, árvore tipada e emissão/formatação do TAC.
- Rejeição de limites booleanos, aridade incorreta e erros independentes sem cascata.
- Limites inclusivos reais, negativos, unitários e inteiros grandes.
- Intervalo invertido em execução, com linha e falha preservada mesmo sem uso.
- Ordem de avaliação de chamadas aninhadas e múltiplas chamadas.
- Otimização não chama o gerador, não altera o original e atinge ponto fixo.
- Sorteio em cada iteração de um laço e em nova execução do mesmo código.
- Temporário não lido não elimina sorteio alcançável.

Os testes de lógica do jogo controlam o gerador para obter resultados
repetíveis e exigem uma única chamada por partida. Também há CLI real sem
controle do gerador com intervalo 42 a 42. Testes de SystemRandom real apenas
verificam inclusão nos limites; não exigem diversidade como condição de aprovação.

## Sessões reais com intervalo padrão

Foram executados os comandos abaixo, fornecendo os palpites 1 a 100 em ordem:

```bash
python3 -m miniforge exemplos/adivinha/adivinha.mini --executar
python3 -m miniforge exemplos/adivinha/adivinha.mini --executar -O
```

A primeira sessão acertou em 44 tentativas e a segunda em 65, ambas com código
0, sem stderr. Como os palpites foram crescentes a partir de 1, essas contagens
correspondem aos segredos sorteados nessas duas execuções. São observações,
não números esperados para futuras partidas nem prova estatística da distribuição.
O gerador normal não usa semente fixa e pode repetir um valor por acaso.

## Métrica estática atual

Contagem sem instruções label: **62 antes**, **48 depois**, **22,58% de redução**.
Há uma instrução random no TAC otimizado. A chamada não é dobrada mesmo com
limites constantes; só verificações e caminhos simplificáveis são reduzidos.
Não há comparação de velocidade ou contagem de instruções executadas.
O registro testes-programas.md descreve a versão histórica de segredo fixo;
seus números 66/46 não representam a versão aleatória.

`python3 -m compileall -q miniforge tests` e `git diff --check` terminaram com
código 0. Não houve validação da revisão em Windows. Evidências não são prova
geral de equivalência para todos os programas.

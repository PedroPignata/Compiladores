# Testes do MiniForge

Na raiz MiniForge/, com pytest instalado:

```bash
python -m pytest -q
python -m pytest -q tests/test_calculadora.py tests/test_calculadora_interativa.py tests/test_adivinha.py tests/test_sorteio.py
```

A primeira chamada verifica o projeto inteiro. A segunda verifica os exemplos
fixos da calculadora e sessões dos dois programas interativos.

- Lexer, parser, tipos e símbolos: tokens, posições, sintaxe, escopos e diagnósticos.
- IR e otimizador: instruções esperadas, rótulos, nomes, origem, efeitos, divisões,
  não mutação e ponto fixo. A importação desses módulos não depende do executor.
- Calculadora: contas, entrada, menu, erros, frações truncadas para zero e repetição.
- Jogo: dicas, contagem, limites, abandono, configurações e inspeção sem teclado.

As aplicações são testadas com o executor real do projeto, com e sem otimização.
Não há executor substituto implementado nos testes. O banco tests/casos/ mantém
fontes válidos e inválidos; comentários de expectativa dos casos são dados de teste.
Personalizações de programas podem exigir atualização deliberada dos cenários,
mas não remoção de asserções para esconder falhas.

Resultados históricos em [testes.md](../docs/testes.md), revisão da calculadora
em [testes-calculadora.md](../docs/testes-calculadora.md) e primeira validação conjunta
em [testes-programas.md](../docs/testes-programas.md). Validação vigente: [testes.md](../docs/testes.md). Os casos cobertos não
constituem prova geral de equivalência entre TAC original e otimizado.

Sorteio: test_sorteio.py verifica tipos, sintaxe, ordem, limites e preservação
de efeitos pelo otimizador. Resultados atuais em [testes.md](../docs/testes.md).

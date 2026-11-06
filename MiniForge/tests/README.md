# Testes do frontend

Preservamos os testes do ZIP para lexer, parser, casos, símbolos, semântica,
tipos e vocabulário. Em `test_mineires.py`, os exemplos antes executados agora
verificam a AST e os tipos. A formatação da saída da VM e divisão por zero
permanecem no ZIP, fora do escopo desta suíte.

`test_cli_frontend.py` acrescenta testes do padrão sem execução, das 32
combinações de opções, erros de argumentos e leitura, opções futuras recusadas,
independência de imports e dos 40 pares de operadores/tipos.

Banco original: 11 válidos, 13 inválidos sintáticos e 18 semânticos, estes com
um erro por arquivo. Os inválidos começam com `// ERRO:` e o teste compara a
mensagem. Novos casos podem ser incluídos sem alterar o parametrizador.

Executar `python -m pytest -q`. Ambiente e resultados reais em
[docs/testes.md](../docs/testes.md).

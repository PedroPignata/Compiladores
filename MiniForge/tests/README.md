# Testes

Esta primeira etapa entrega especificação, arquitetura e CLI de leitura.
A CLI pode ser verificada executando os cinco arquivos de `exemplos/` e
comparando sua saída com o conteúdo de cada arquivo.

A partir da próxima etapa, usar `python -m pytest -q` e criar progressivamente:
`test_lexer.py`, `test_parser.py`, `test_casos.py`, `test_simbolos.py`,
`test_semantica.py`, `test_ir.py`, `test_vm.py` e `test_otimizador.py`.
Ainda não há testes automatizados nem validação da linguagem nesta versão.

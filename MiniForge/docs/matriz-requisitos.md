# Matriz de atendimento e diagnóstico

Diagnóstico realizado em 06/11/2026 antes da integração. Corte acadêmico: 16/10/2026.
As páginas são físicas (1–56) do PDF da professora. Situação refere-se ao ZIP.

| Requisito | Aula / página | Implementação no ZIP | Situação | Adaptação para o corte | Evidência na entrega |
|---|---|---|---|---|---|
| Especificação e 5 exemplos | 06, pp. 4–6 | docs/especificacao.md, exemplos/ | Mineirês completo | Ajustar resultados futuros | test_mineires.py |
| Tokens, posições, reservadas e EOF | 08, pp. 8–11 | tokens.py, lexer.py | Implementado | Preservar | test_lexer.py |
| Recuperação e análise de lexer didático | 10, pp. 13–16 | lexer.py, docs/analise-lexer.md | Implementado | Preservar ficha | test_varios_erros_reportados_de_uma_vez |
| EBNF, FIRST, derivação, 8 válidos e 8 inválidos | 12, pp. 18–21 | docs/gramatica.md, tests/casos/ | 11 válidos e 13 inválidos | Preservar | test_casos.py |
| Parser, precedência, AST e diagnósticos | 14, pp. 23–26 | parser.py, ast.py | Implementado | Preservar | test_parser.py |
| Integração e checkpoint | 16, pp. 28–31 | __main__.py, docs/checkpoint.md | CLI completa e contagens históricas | Cortar execução e atualizar evidências | test_cli_frontend.py |
| Símbolos e quatro operações | 20, pp. 33–36 | simbolos.py | Cinco atributos mais usos | Preservar | test_simbolos.py |
| Escopos, sombreamento e inicializador | 20, pp. 34–36 | semantica.py | Visitor e pilha implementados | Preservar | test_semantica.py |
| Cinco regras e tabela de tipos | 22, pp. 38–41 | semantica.py | Implementado, tipos internos int/bool | Preservar | test_tipos.py e matriz de operadores |
| AST anotada e supressão de cascata | 22, pp. 39–41 | ast.py, semantica.py | Implementado | Preservar | test_ast_anotada_em_todos_os_nos_de_expressao |
| Contexto e avisos opcionais | 20/22, pp. 36 e 41 | semantica.py, __main__.py | Recursos adicionais implementados | Manter sem exigir para aprovação | test_cli_contexto_com_circunflexo |
| CLI independente e tag semântica | 22, pp. 40–41 | __main__.py | Importa IR/VM/otimizador | Remover imports, opções e execução posteriores | test_cli_frontend.py |
| Testes da linguagem | 08–22 | tests/test_mineires.py | Mistura frontend e VM | Separar testes e converter evidência para AST/tipos | test_mineires.py |
| TAC, pilha, VM, otimização e artigo | 26–30, pp. 42–56 | ir.py, vm.py, otimizador.py e testes/docs | Concluídos no ZIP, futuros neste corte | Não integrar; original permanece intacto | Teste de ausência de módulos e imports |

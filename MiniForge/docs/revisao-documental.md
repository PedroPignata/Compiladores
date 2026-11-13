# Revisão documental do repositório

Data: 13/11/2026. Referência inicial da main: 7e1408a. Esta revisão modifica
somente Markdown; nenhum código, teste ou programa mineirês foi alterado.

## Objetivo e organização

Consolidar a descrição da implementação vigente: frontend, TAC, cinco passes,
execução explícita, leitura inteira, mensagens e sorteio. Corrigir divergências
entre documentos, indicar a pasta dos comandos e identificar registros antigos.
O README da raiz Compiladores passa a listar também o MiniForge e os manuais
dos dois programas. Cada projeto conserva sua linguagem e seu relatório.

## Alterações do MiniForge

- README principal com instalação, onze reservadas, comandos e combinações atuais.
- Novo docs/README.md para documentos vigentes e históricos.
- Relatório final consolidado, sem apresentar revisões antigas como estado atual.
- Checkpoint, integração e matriz atualizados com execução e aleatoriedade.
- Gramática com FIRST de leitura/sorteio e remoção de alternativa lógica não implementada.
- Descrição atual do lexer, incluindo mensagem literal, vírgula e erros de fechamento.
- Tabela de otimização recalculada para todos os exemplos válidos, incluindo calculadora interativa.
- Demonstração com oito comandos executados e saídas capturadas da implementação atual.
- Testes vigentes separados de resultados anteriores; código de referência e ambiente explícitos.
- Registros anteriores preservados com identificação histórica e índice próprio.
- Guias dos programas e testes apontando à documentação vigente.

## Outros projetos

MiniLexer: corrigida a instrução de entrar em minilexer/ antes de compilar e
explicado o contexto do relatório. O comando documentado foi conferido com GCC;
o exemplo integrado produziu 26 tokens e zero erros, código 0.

Mini C Compiler: corrigida a localização dos comandos e atualizados documentos
de estrutura e parser, que ainda falavam em placeholders e nós AST_LET ou
AST_IDENTIFIER inexistentes no enum. Os nomes reais são AST_ASSIGN e AST_VAR.
A descrição do interpretador foi alinhada com esses nomes. A compilação foi
conferida e T01 terminou com resultado 10, código 0. Não foi reexecutada toda
a bateria histórica deste projeto nem alterado seu código.

Transformer por Dentro: esclarecido de onde executar cd e que seus resultados
e dependências são próprios. Mantidos os dados do relatório e as evidências de
31 testes registrados naquela aplicação. Essa suíte e a interface Streamlit
não foram reexecutadas nesta revisão; a contagem não foi apresentada como nova.
Os demais documentos sem divergência confirmada foram preservados.

## Verificações

- MiniForge: `python -m pytest -q` -> **817 passed in 15.48s**, sem skips/xfails.
- Contagens estáticas recalculadas por gerar_tac e otimizar, sem rótulos.
- Oito comandos da demonstração executados com códigos esperados.
- Comandos distintos do MiniForge nos manuais vigentes conferidos por subprocesso;
  execução interativa usa entrada 0 para encerrar e não ficar aguardando teclado.
- Redirecionamentos de TAC são verificados sem sobrescrever referências.
- O caminho meu_programa.mini do tutorial é explicitamente um arquivo a criar,
  não um exemplo entregue; não é tratado como link quebrado.
- Varredura final de 46 documentos Markdown, com 193 links locais válidos e
  32 comandos distintos do MiniForge conferidos.
- Links Markdown locais verificados na árvore versionada e nos novos documentos,
  excluindo links externos e conteúdo de blocos de código.
- `python3 -m compileall -q miniforge tests` e `git diff --check`: código 0.
- Binários de conferência dos projetos C gerados em /tmp, fora do Git.

## Alcance

A revisão não comprova que todo link externo está disponível nem revalida
apresentações locais. Não altera métricas históricas, tags ou autoria. Não
reivindica prova geral de equivalência, benchmark ou execução de todas as suítes
dos demais projetos. O estado atual do MiniForge está em [testes.md](testes.md)
e os contratos em [especificacao.md](especificacao.md).

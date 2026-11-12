# Matriz da entrega de 13/11/2026

Diagnóstico antes da integração em 12/11: main 2bb5b03, sem alterações locais.
Os PDFs Projeto.pdf e Projeto-1.pdf são idênticos (SHA-256 d8acb1bb5d3ecd479f344be3a7148f4c274f0ea728ec018956b15f10be19485c).
As apresentações anteriores têm conteúdo e hashes diferentes: foram usadas como referências de continuidade, não de escopo.
Os nomes com (1) citados no pedido não estão disponíveis; os arquivos anexados sem esse sufixo são a referência efetiva.

| Requisito / página física | Implementação | Diagnóstico / adaptação | Situação / evidência |
|---|---|---|---|
| Organização, aula 06 p.5 (4/5) | miniforge/, tests/, exemplos/, docs/ | minilang é o nome genérico do exemplo; preservado MiniForge | Atendido, árvore no README |
| Frontend, aulas 08–22 pp.7–41 | tokens, lexer, parser, AST, símbolos e semântica | Preservar código e regressões | Atendido, testes anteriores |
| TAC, aula 26 pp.42–46 | ir.py do ZIP | Remover bytecode e executor dos testes | Atendido, test_ir.py |
| Temporários, escopos, saltos, origem | GeradorTAC do ZIP | Preservar nomes únicos; validar AST na API pública | Atendido, testes estruturais |
| Cinco passes, aula 30 pp.52–56 | otimizador.py do ZIP | Extrair avaliação constante de vm.OPS | Atendido, testes isolados e ponto fixo |
| Comparação antes/depois p.56 | docs/otimizacao.md | Contagem estática sem rótulos | Adaptado, medições desta versão |
| Equivalência por execução p.56 | testes de execução no ZIP | Não integrar executor de TAC nem VM de teste | Excluído por pedido, sem prova geral de equivalência |
| VM e estatísticas aulas 28 pp.47–51 | vm.py do ZIP | Não integrar | Excluído por pedido |
| Desafio pilha p.46 | GeradorPilha | Não integrar | Excluído por pedido |
| Extensões lógicas opcionais | proposta na gramática | Priorizar núcleo e segurança | Futuro, não implementado |

Definições: dependência de vm.OPS é incompatibilidade de escopo, não defeito do projeto completo.
Melhorias propostas: avaliação constante com tipos estritos; guarda semântica na API de geração.
Riscos a testar: constantes em laços/junções, divisão por zero alcançável, mutação, idempotência e colisões.
Nenhum bloqueio técnico identificado no diagnóstico.

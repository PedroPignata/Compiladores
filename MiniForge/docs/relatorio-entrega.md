# Registro da integração até otimização - 13/11/2026

Relatório acadêmico completo e aplicação demonstrativa: [relatorio-final.md](relatorio-final.md).
Este documento preserva o diagnóstico e as medições da integração inicial.

## Estado inicial

main 2bb5b03, frontend v0.3-semantica e nenhuma alteração local. Revisão real
em 12/11/2026. Requisitos novos substituem o corte anterior. PDFs da professora
idênticos; ZIP original intacto. Sem AGENTS.md aplicável.

## Conteúdo e alterações

Reaproveitados gerador TAC e cinco passes do ZIP, mantendo nomes, vocabulário,
Visitor, escopos e créditos. Adicionados ir.py, otimizador.py e constantes.py.
Evoluída CLI; atualizados README, documentação, exemplos, testes frontend;
novos test_ir.py, test_otimizador.py e test_middleend.py. A lista exata de
arquivos pode ser conferida no diff do PR, todo dentro de MiniForge/.

Correções/adaptações: vm.OPS substituído por avaliação constante independente;
API pública verifica semântica; bool não é aceito como int no dobramento;
-O com inspeção sem --tac é rejeitado com código 2. Não foi reproduzido defeito
do algoritmo dos passes sobre TAC válido; não se atribui ao colega defeito
inexistente. Bytecode e executores dos testes mistos não foram integrados.
Não houve extensão da linguagem; propostas lógicas permanecem futuras.

## Evidências e critérios de aceite

Matriz por aula/página em matriz-requisitos.md. Frontend e organização
preservados; TAC completo com nomes internos únicos, rótulos válidos e origem;
cinco passes conservadores sem backend; CLI original/otimizada; testes pertinentes
aprovados; medições estáticas em otimizacao.md. Segunda revisão confirmou esses
itens e ausência de imports de VM. Documentação consistente com o novo padrão.

696 testes, duas execuções completas aprovadas (10,97 e 10,64 s), sem skips ou
xfails. Ambiente e comandos em testes.md. Testes estruturais não comprovam
equivalência semântica geral. Resultados estáticos sem rótulos: constantes
10/3, expressão 5/2, if constante 7/2, if/else 9/4; fatorial 10/10,
escopos 6/6 e pão de queijo 18/18. Nenhuma alegação de aceleração ou saída executada.

## Exclusões e pendências

VM, backend, pilha, métricas de execução e artigo final excluídos por pedido,
não por bloqueio técnico. Não há VM de testes. Sem teste em Windows ou
PowerPoint e sem prova formal geral de equivalência. Entradas patológicas
continuam limitações documentadas. Nenhum bloqueio de implementação restante.
A demonstração presencial em 13/11 ainda deve ser realizada pelo grupo.

Apresentação local em apresentacao/13-11/: PPTX editável, PDF e roteiro,
sem versionar mídia conforme preferência do usuário. Os comandos com saídas
conferidas estão em demonstracao.md. A publicação usa branch
entrega/otimizador-13-11 e tag v0.5-otimizacao-sem-vm; PR #2 integrado à main em 12/11/2026, commit 749a919c7468a9bc3ffd1502d617b614a02a7054.

## Passo a passo para correção

1. Fazer checkout da branch/tag e entrar em MiniForge/.
2. python3 -m venv .venv e ativar o ambiente.
3. python -m pip install -r requirements-dev.txt.
4. python -m pytest -q.
5. python -m miniforge exemplos/constantes.mini --tac.
6. Repetir com -O e comparar o TAC, sem contar rótulos.
7. Conferir fatorial com/sem -O: conservadorismo sem ganho.
8. Mostrar erros léxicos, sintáticos e semânticos conforme demonstracao.md.
9. Examinar ir.py, otimizador.py e os testes dos riscos conhecidos.

Para continuar: recuperar somente a próxima fase autorizada do ZIP, nunca
restaurar a CLI completa sem preservar as regras de combinações e a exclusão
vigente do backend. Não há autorização implícita para integrar VM futuramente.

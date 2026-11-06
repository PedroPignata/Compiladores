# Integração seletiva do trabalho do grupo

Data real: 06/11/2026. Corte acadêmico: 16/10/2026, aulas 06 a 22.
Base anterior: commit `569a146` em `main`, apenas estrutura e CLI de eco.
Remoto: `https://github.com/PedroPignata/Compiladores.git`.
Não havia alterações locais. Não foram encontrados AGENTS.md aplicáveis.

## Referência preservada

`/home/pedro/Downloads/MiniForge-v0.6-mineires.zip`, intacto, SHA-256:
`b00b4d7085e3faf74efbb63c33ec6739f827194210204b0e9ef139de84f3a6f8`.
Não publicar uma segunda cópia do compilador completo nesta entrega.

Créditos do grupo: Pedro Dutra, Pedro Pignata, Lucas Rocha Dantas e Renato
Portilho. Professora Lorena Bezerra. O código continua o trabalho iniciado
no repositório e desenvolvido pelo colega, sem atribuir autoria individual
que os materiais não identificam nem inventar commits de etapas passadas.

## Reaproveitado

`tokens.py`, `lexer.py`, `parser.py`, `ast.py`, `simbolos.py` e `semantica.py`
vieram do ZIP, mantendo as implementações, interfaces e convenções. O Visitor,
a tabela REGRAS, a pilha de dicionários, os tipos internos e o pretty-printer
foram preservados. O vocabulário é o das nove reservadas do grupo.

Mantidos os quatro exemplos válidos pertinentes ao frontend e os quatro
exemplos de erro léxico/sintático/semântico. Mantidos 42 casos e seis arquivos
de testes do frontend. `test_mineires.py` preserva vocabulário e diagnósticos,
substituindo expectativas de execução por evidências de AST e tipos.
Especificação, gramática, ficha de análise de lexer, checkpoint, arquitetura
e README foram adaptados da documentação do ZIP.

## Adaptações necessárias

- CLI: removidos imports e caminhos de TAC, pilha, VM, estatísticas e `-O`.
  O padrão agora valida e informa sucesso. `--verificar` continua disponível.
- Combinações: `--ast --tipos` e `--ast --verificar` continuam até a semântica,
  corrigindo o retorno antecipado que ignorava a outra opção no ZIP.
- `--contexto` e avisos de não uso permanecem como recursos adicionais.
- Removidos os três stubs antigos de fases futuras, sem substituí-los por
  implementações do ZIP. Nenhum teste desta entrega importa essas fases.
- `test_mineires.py`: testes de saída da VM e divisão por zero continuam
  exclusivamente no ZIP. Nenhuma verificação relevante de frontend foi pulada.
- README, checkpoint e apresentação usam contagens medidas nesta entrega,
  sem repetir 707 testes ou resultados finais. Menções ao fatorial calculado
  nos comentários do exemplo descrevem seu objetivo futuro, não saída da CLI.

## Classificação da revisão

**Defeito confirmado da interface:** retorno antecipado de `--ast` ignorava
pedidos simultâneos de semântica. Corrigido e coberto por testes.
**Incompatibilidade de escopo:** execução padrão e imports do backend, não
um defeito do compilador completo. Separados para cumprir o corte acadêmico.
**Documentação desatualizada para o corte:** resultados de VM/A2 e contagens
históricas não descreviam o frontend publicado. Adaptados.
**Riscos/limitações:** o atalho `parse` não valida erros léxicos (contrato já
documentado no ZIP); usar a CLI para validação completa. Profundidade extrema
e literais decimais acima do limite do Python não têm diagnóstico dedicado.
**Melhorias opcionais:** recuperação sintática múltipla e robustez para entradas
patológicas. Não são pré-requisitos da entrega.
**Futuro:** TAC, pilha, VM, otimização e artigo não estão ativos neste corte.

## Incorporação posterior

Recuperar do ZIP somente os módulos/testes da próxima aula. Na aula 26,
reintegrar `ir.py` e testes de TAC/pilha; na 28, `vm.py` e testes de execução;
na 30, `otimizador.py`, testes comparativos e documentação de resultados.
Os arquivos `test_ir.py`, `test_vm.py` e `test_otimizador.py`, exemplos de
execução/otimização e docs finais permanecem na referência original.

Preservar o padrão sem execução enquanto o corte o exigir. Quando a etapa
permitir execução, revisar explicitamente a CLI e os testes desse contrato.
Não restaurar o arquivo completo da CLI sobre as correções de precedência.

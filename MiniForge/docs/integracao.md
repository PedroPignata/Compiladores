# Integração de 12/11 para entrega de 13/11/2026

Base: main 2bb5b03, sem alterações locais. Branch entrega/otimizador-13-11.
Nenhum AGENTS.md aplicável encontrado. Nenhum outro projeto foi alterado.
O pedido atual substitui o limite anterior e exclui explicitamente o backend.

Referência: MiniForge-v0.6-mineires.zip, SHA-256
b00b4d7085e3faf74efbb63c33ec6739f827194210204b0e9ef139de84f3a6f8.
Original intacto em Downloads. Arquivos com sufixo (1) citados no texto não
estão disponíveis; foram usados os anexos efetivamente existentes.
Os PDFs da professora Projeto.pdf e Projeto-1.pdf são idênticos.
As três apresentações/guia da entrega anterior diferem entre si e da
apresentação completa; suas métricas e limites não foram usados como atuais.

## Trabalho preservado e alterações

Frontend preservado. ir.py veio do ZIP, removendo somente GeradorPilha e
estruturas associadas. Otimizador mantém os cinco passes do colega. A CLI
preserva correções de combinações anteriores e acrescenta geração explícita
ou padrão, otimização e rejeição de -O sem geração.
Testes TAC do ZIP foram separados: nenhum executor_tac ou bytecode foi integrado.
Testes isolados dos passes foram reaproveitados; casos com VM, medição dinâmica
e equivalência executada permanecem exclusivamente na referência original.

## Defeitos, riscos e melhorias

Dependência de vm.OPS era incompatibilidade com este corte, não defeito do
projeto completo. Foi removida por constantes.py, sem copiar uma máquina.
A API gerar_tac antes confiava apenas em pré-condição documentada. Agora
rejeita semanticamente AST inválida antes de gerar: melhoria de contrato.
Dobramento antes aceitava bool como int pelo Python em TAC malformado. Agora
valida a combinação de tipos por REGRAS: robustez adicional, sem afirmar que
o frontend correto gerava esse TAC inválido.
Riscos de laços, junções, origem, efeitos e divisão por zero foram testados
estruturalmente. Não foi identificado defeito reproduzido no algoritmo dos
cinco passes sobre TAC válido. Não foram introduzidas extensões sintáticas.
A prioridade foi preservar compatibilidade e validar o núcleo solicitado.

## Continuidade e exclusões

Créditos: Pedro Dutra, Pedro Pignata, Lucas Rocha Dantas e Renato Portilho.
Sem datas ou autoria individual inventadas. Implementação da linguagem e do
middle-end reaproveita o trabalho do mesmo grupo.
VM, Stack VM, execução de TAC, métricas dinâmicas e artigo final foram excluídos.
A apresentação fica local conforme preferência do usuário. A branch, o PR e
a tag v0.5-otimizacao-sem-vm identificam que a versão não inclui VM.

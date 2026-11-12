# Testes até otimização

Executar python -m pytest -q. Frontend original preservado. test_ir.py contém
expectativas textuais e estruturais do ZIP, sem seu executor TAC e desafio de
pilha. test_otimizador.py reaproveita os testes isolados dos cinco passes e
ponto fixo, removendo dependências de VM. test_middleend.py acrescenta riscos,
API semântica, divisão exata, tipos estritos e 128 combinações de CLI.
Não há VM de testes ou executor de TAC. Evidência não é prova geral de
equivalência. Relatório completo em ../docs/testes.md.

# Arquitetura até otimização, sem backend

A estrutura da página física 5 (slide 4/5) é mantida com o nome do pacote
miniforge. Léxico e parser usam tokens e dataclasses da AST. A semântica usa
Visitor e TabelaSimbolos, verificando nomes, escopos e tipos. Todos os seis
módulos centrais do frontend continuam iguais à entrega anterior.

ir.py preserva Instr, GeradorTAC e a base de escopos do ZIP. Cada expressão
emite instruções em pós-ordem. O inicializador é gerado antes da nova declaração.
Sombreamento usa x.2; t1 do usuário vira t1.1 para não colidir com temporários.
Rótulos têm espaço separado dos nomes de variáveis. Cada salto mira um rótulo
existente, e a condição de while fica depois do rótulo inicial, sendo reavaliável.
A API gerar_tac valida semanticamente sua AST e rejeita erros com ValueError.
GeradorTAC é a interface de baixo nível, cuja pré-condição é AST validada.
Instâncias de gerador são de uso único; a API cria instância nova a cada chamada.

otimizador.py aplica cinco passes com contrato (novo_codigo, mudou), até ponto
fixo. constantes.py contém avaliação estrita de uma operação literal, usando
REGRAS da semântica. Não contém execução de instruções ou fluxo de controle.
O otimizador recebe TAC válido e tipado da geração. A CLI é o ponto de entrada
que verifica também erros léxicos e sintáticos.

Não existem vm.py, bytecode, pilha, contador de programa ou executor de testes.
A saída print no TAC é uma instrução representada, não uma chamada executada.
Os contratos da CLI estão no README, e os limites da validação em testes.md.

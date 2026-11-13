# Arquitetura do MiniForge

## Organização conforme o roteiro

O slide “Estrutura do repositório” (página física 5, 4/5 da aula inicial)
separa pacote Python, testes, exemplos e documentação. O nome genérico
`minilang` corresponde a `MiniForge/miniforge` no projeto do grupo.

```text
MiniForge/
  miniforge/
    __init__.py
    __main__.py
    tokens.py
    lexer.py
    ast.py
    parser.py
    simbolos.py
    semantica.py
    ir.py
    otimizador.py
    constantes.py
    execucao.py
  tests/
    test_lexer.py, test_parser.py, test_simbolos.py, test_semantica.py, ...
    test_ir.py, test_otimizador.py, test_middleend.py
    test_calculadora.py, test_calculadora_interativa.py, test_adivinha.py, test_sorteio.py
    casos/
  exemplos/
    README.md
    calculadora/
      interativa.mini, calculadora.mini, constantes.mini, README.md
      arquivos TAC de referência dos exemplos fixos
    adivinha/
      adivinha.mini, README.md
    demais exemplos .mini
  docs/
    especificacao.md, gramatica.md, arquitetura.md, otimizacao.md, ...
  README.md
  pytest.ini
  requirements-dev.txt
```

Os programas ficam em subpastas de exemplos/, sem módulos específicos dentro
do compilador. Seus testes ficam em tests/, e seus guias de uso acompanham os
fontes. A configuração pytest mantém a descoberta em tests/ e o pacote na raiz.
As apresentações continuam locais e ignoradas pelo Git. Outros projetos do
repositório Compiladores não são modificados por esta organização.

## Responsabilidade de cada módulo

| Módulo | Entrada e saída / responsabilidade |
|---|---|
| tokens.py | Categorias, reservadas, nomes de tipos e literais |
| lexer.py | Texto UTF-8 para tokens com posição e erros recuperáveis |
| ast.py | Nós de comandos/expressões e formatação da árvore |
| parser.py | Tokens terminados em EOF para AST, respeitando precedência |
| simbolos.py | Declarações e usos numa pilha de escopos |
| semantica.py | AST para diagnósticos e expressões anotadas com tipos |
| ir.py | AST validada para lista de Instr com origem e nomes únicos |
| constantes.py | Avaliação tipada de uma operação literal, sem executar fluxo |
| otimizador.py | TAC para novo TAC, cinco passes até ponto fixo |
| execucao.py | TAC válido para entrada, saída e estado de execução |
| __main__.py | CLI, leitura de arquivo, escolha das fases e códigos de retorno |

## Fluxo e contratos

A CLI verifica erros léxicos antes de chamar o parser e só gera TAC depois da
semântica aprovada. `--tokens`, `--ast`, `--tipos` e `--verificar` permitem parar
na fase correspondente. Sem opções, imprime TAC; `-O` seleciona TAC otimizado.
`--executar` executa, podendo acompanhar `-O`, mas não opções de inspeção.

`gerar_tac` valida a semântica da AST na API pública. O visitante de geração
percorre expressões em pós-ordem. O inicializador vem antes de inserir o novo
nome. Sombreamento usa identidades internas, como x.2; nomes do usuário como t1
não colidem com temporários. O laço reavalia a condição após seu rótulo inicial.
Cada geração usa uma instância nova e tem resultado determinístico.

Os passes devolvem `(novo_codigo, mudou)` e preservam a entrada. Propagação
respeita limites de fluxo e invalida destinos escritos, inclusive read. Leituras,
saídas e divisões potencialmente falhas não desaparecem por falta de uso.
A aplicação dos passes termina num ponto fixo.

## Execução e correspondência com os slides

O arquivo execucao.py exerce o papel de executor/backend simples de TAC,
correspondente à responsabilidade da VM no roteiro. A CLI controla o caminho:
sem --executar, apresenta código intermediário; com essa opção, executa as
instruções após a validação e a otimização opcional. Não há bytecode de pilha.
Os contratos de entrada, saída e erros estão em [execucao.md](execucao.md).

A calculadora e o jogo só usam instruções já suportadas: cópias, operações,
read, texto, print, saltos, rótulos e random. A expressão sorteia_so foi
integrada nos módulos existentes, sem novo pacote ou aplicativo auxiliar.
Seu contrato e as adaptações dos passes estão em sorteio.md. Contratos da linguagem em [especificacao.md](especificacao.md),
EBNF em [gramatica.md](gramatica.md) e conformidade histórica em
[matriz-requisitos.md](matriz-requisitos.md).

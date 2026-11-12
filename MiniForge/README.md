# MiniForge - compilador de mineirês, sô

Entrega para **13/11/2026**, versão **v0.5-otimizacao-sem-vm**.
Pedro Dutra, Pedro Pignata, Lucas Rocha Dantas e Renato Portilho.
Professora Lorena Bezerra, Compiladores 2026.2.

Continuação do frontend v0.3-semantica: agora o projeto valida o fonte,
gera código de três endereços (TAC) e pode otimizá-lo. **Não executa programas**.
A máquina virtual e o backend foram explicitamente excluídos desta entrega.

## Instalar e conferir

Requer Python 3.10+. Dentro de MiniForge/:

```bash
python3 -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scripts\activate
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m miniforge exemplos/fatorial.mini
python -m miniforge exemplos/constantes.mini --tac -O
```

O compilador usa a biblioteca padrão; pytest é dependência de desenvolvimento.
A suíte desta entrega tem 696 testes. Resultados reais em docs/testes.md.

## Linguagem

| Palavra | Papel | Exemplo |
|---|---|---|
| trem | declaração inicializada | trem x: inteirim = 1; |
| inteirim | inteiro | trem n: inteirim = 5; |
| booleanim | booleano | trem ok: booleanim = eh_memo; |
| eh_memo / num_eh | verdadeiro / falso | ok = num_eh; |
| uai / sinao | condicional | uai (ok) { mostra_so(1); } sinao { mostra_so(0); } |
| enquanto_tiver | repetição | enquanto_tiver (n > 0) { n = n - 1; } |
| mostra_so | comando de saída no TAC | mostra_so(n); |

Sem coerção int/bool. Chaves obrigatórias, comentários //, comparações não
encadeadas. Tipos internos continuam int e bool. Nenhuma extensão de linguagem
foi adicionada: operadores lógicos permanecem proposta futura na gramática.

## Organização e pipeline

```text
MiniForge/
  miniforge/ __init__.py, __main__.py, tokens.py, lexer.py,
             ast.py, parser.py, simbolos.py, semantica.py,
             ir.py, otimizador.py, constantes.py
  tests/     casos e testes por fase
  exemplos/  programas .mini
  docs/      especificacao.md, gramatica.md, arquitetura.md,
             otimizacao.md, matriz-requisitos.md e relatórios
  README.md, pytest.ini, requirements-dev.txt

fonte -> tokens -> AST -> AST tipada -> TAC -> [otimização]
```

A estrutura corresponde ao slide inicial 4/5 (página física 5). O pacote
genérico minilang do exemplo corresponde a MiniForge/miniforge. Não há
exigência de renomear nossa linguagem. vm.py é a exceção deliberada, excluída.
Não foram alterados os demais projetos de Compiladores.

## CLI e combinações

Sem opções, gera e imprime TAC original. -O sozinho imprime TAC otimizado.
Essa é a evolução do padrão anterior, que apenas informava sucesso semântico.

| Opção | Comportamento |
|---|---|
| --tokens | Léxico e tokens |
| --ast | Parser e AST sintática |
| --tipos | Semântica e AST anotada |
| --verificar | Só frontend, mensagem de sucesso |
| --contexto | Acrescenta contexto aos diagnósticos semânticos |
| --tac | Frontend e impressão do TAC |
| --tac -O | Frontend e impressão do TAC otimizado |

Inspeções combinadas são cumulativas, na ordem tokens, AST sintática, tipos,
mensagem de verificação e TAC. O pipeline avança até a fase mais profunda
pedida. Saídas de fases anteriores podem aparecer antes de erro posterior.
Com uma inspeção explícita, TAC só aparece se --tac também for pedido.
-O junto de inspeção exige --tac: combinações sem geração são erro de uso 2,
para não ignorar silenciosamente a otimização. --contexto sozinho mantém o
padrão de geração. Há testes das 128 combinações de sete sinalizadores.

0: sucesso; 1: erro de leitura/compilação; 2: argumentos inválidos.
Diagnósticos e avisos vão para stderr; uma fase com erro bloqueia as seguintes.
--pilha, --vm-pilha e --stats são rejeitados. Não há estatísticas de execução.

## Documentação e limites

- [Especificação](docs/especificacao.md), [gramática](docs/gramatica.md).
- [Arquitetura](docs/arquitetura.md), [matriz](docs/matriz-requisitos.md).
- [Otimizações e resultados estáticos](docs/otimizacao.md).
- [Integração e revisão](docs/integracao.md), [testes](docs/testes.md).
- [Demonstração conferida](docs/demonstracao.md).

Sem VM, pilha, backend ou artigo final da A2. Não há prova geral de equivalência
por execução. O atalho interno parse() pressupõe fonte lexicamente válido;
para compilar arquivos use a CLI. Entradas patológicas, profundidade extrema
e limite decimal do Python continuam limitações. Funções, strings, vetores e
novos tipos não foram acrescentados. Apresentações ficam locais, fora do Git.

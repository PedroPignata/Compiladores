# MiniForge — compilador MiniLang

Projeto didático de Compiladores 2026.2: construir um compilador da MiniLang,
com análise léxica, parser e AST, análise semântica, código de três endereços
(TAC), máquina virtual e otimizações.

**Versão inicial: `v0.0-spec`.** Esta entrega contém a arquitetura, a
especificação, a gramática inicial, cinco programas de exemplo e a CLI de
leitura. Os demais módulos estão reservados para as próximas etapas.

## Executar

Requer Python 3.10 ou superior. Execute a partir desta pasta `MiniForge/`:

```bash
python3 -m minilang exemplos/fatorial.mini
python3 -m minilang --help
```

Se `python` no seu ambiente aponta para Python 3.10+, pode usar o comando dos
slides: `python -m minilang exemplos/fatorial.mini`.

**Nesta versão, a saída é o próprio código-fonte.** Ainda não há tokenização,
validação ou execução: o fatorial não calcula `120`, e os exemplos inválidos
também são impressos normalmente. Arquivos inexistentes ou sem UTF-8 válido
geram mensagem em stderr e saída 1; argumentos incorretos geram saída 2.

## Estrutura

```text
MiniForge/
├── minilang/
│   ├── __init__.py
│   ├── __main__.py     # CLI implementada nesta entrega
│   ├── tokens.py       # módulos abaixo reservados para as próximas etapas
│   ├── lexer.py
│   ├── ast.py
│   ├── parser.py
│   ├── simbolos.py
│   ├── semantica.py
│   ├── ir.py
│   ├── vm.py
│   └── otimizador.py
├── docs/
│   ├── especificacao.md
│   ├── gramatica.md
│   └── arquitetura.md
├── exemplos/           # 3 válidos e 2 inválidos comentados
├── tests/              # reservado para testes das próximas etapas
├── requirements-dev.txt
└── README.md
```

A pasta faz parte do repositório `PedroPignata/Compiladores`. MiniForge é o
nome do projeto e `minilang` é o pacote Python, conforme a proposta da aula.

## Documentação

- [Especificação da linguagem](docs/especificacao.md): sintaxe, tipos,
  operadores, precedência, escopos e resultados esperados dos exemplos.
- [Gramática inicial em EBNF](docs/gramatica.md): comandos e expressões.
- [Arquitetura e plano](docs/arquitetura.md): contratos planejados,
  as 11 etapas dos slides e decisões para a evolução do compilador.

## Verificação desta entrega

Compare o texto impresso com o arquivo original:

```bash
python3 -m minilang exemplos/fatorial.mini > /tmp/miniforge-fatorial.txt
diff exemplos/fatorial.mini /tmp/miniforge-fatorial.txt
```

O `diff` deve terminar sem diferenças. Repita para os demais exemplos.
Ainda não há suíte automatizada. Nas etapas seguintes, criar o ambiente e
instalar o pytest:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
# Depois de implementar os testes:
python -m pytest -q
```

A execução atual não depende de pacotes externos. As opções `--tokens`,
`--ast`, `--tac`, `--stats` e `-O` serão acrescentadas nas respectivas etapas.

## Publicar o marco inicial

A partir de `MiniForge/`, com autenticação Git configurada:

```bash
git add README.md .gitignore requirements-dev.txt docs exemplos minilang tests
git commit -m "Cria arquitetura e especificação inicial da MiniLang"
git tag v0.0-spec
git push origin main
git push origin v0.0-spec
```

Referência: material de aulas práticas do projeto MiniLang, Compiladores
2026.2, Lorena Bezerra. A entrega segue a aula 06; funcionalidades das aulas
seguintes permanecem planejadas.

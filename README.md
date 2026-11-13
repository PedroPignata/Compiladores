# Compiladores

Atividades e projetos da disciplina de Compiladores. Cada pasta é uma aplicação
independente, com linguagem, dependências, testes e relatório próprios.
Documentação do índice revisada em 13/11/2026.

## Projetos e instruções

| Projeto | Implementação e objetivo | Como começar |
|---|---|---|
| [MiniForge](MiniForge/README.md) | Compilador Python da linguagem mineirês: frontend, TAC, otimização e execução | [Instalação e comandos](MiniForge/README.md), [relatório final](MiniForge/docs/relatorio-final.md) |
| [Transformer por Dentro](transformer-simulator/README.md) | Simulação didática de Transformer em Python/Streamlit | [Manual](transformer-simulator/README.md), [relatório](transformer-simulator/RELATORIO.md) |
| [Mini C Compiler](mini-c-compiler/README.md) | Interpretador em C baseado em AST, com análise e melhoria do parser | [Manual](mini-c-compiler/README.md), [relatório](mini-c-compiler/RELATORIO.md) |
| [MiniLexer](minilexer/README.md) | Analisador léxico em C para a linguagem fictícia MiniC | [Compilar e usar](minilexer/README.md), [relatório](minilexer/RELATORIO.md) |

## Programas em mineirês

Os dois programas estão em MiniForge/exemplos/, não nas linguagens dos outros
projetos. Na raiz deste repositório:

```bash
cd MiniForge
python3 -m miniforge exemplos/calculadora/interativa.mini --executar
python3 -m miniforge exemplos/adivinha/adivinha.mini --executar
```

Execute cada programa separadamente. A calculadora recebe inteiros e oferece
quatro operações. O jogo sorteia um segredo entre 1 e 100 em cada partida.
A opção -O pode acompanhar --executar. Sem --executar, o MiniForge gera TAC.
No Windows ou com ambiente Python ativo, use python em vez de python3.

- [Guia para usar e modificar os dois programas](MiniForge/exemplos/README.md).
- [Documentação vigente do MiniForge](MiniForge/docs/README.md).
- [Validação atual do MiniForge](MiniForge/docs/testes.md).

## Organização dos comandos

Os comandos de cada README devem ser executados na pasta daquela aplicação,
conforme suas instruções. Dependências e métricas não são compartilhadas:
os testes do MiniForge não certificam o simulador Transformer ou os projetos C.
Relatórios históricos e notas do projeto original permanecem identificados;
eles não descrevem automaticamente a main de outro projeto.

Apresentações do MiniForge são mantidas localmente, fora do Git. Não há
instalação única de todos os projetos nem exigência de API externa para usar
os programas mineirês.

"""CLI do frontend mineirês: validação até a semântica, sem execução."""

import argparse
from pathlib import Path
import sys

from .ast import formatar_ast
from .lexer import Lexer, formatar_token
from .parser import ErroSintatico, Parser
from .semantica import analisar


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m miniforge",
        description="MiniForge: compilador didático da linguagem mineirês, "
                    "sô. Sem opções, valida léxico, sintaxe e semântica "
                    "sem executar o programa.",
    )
    parser.add_argument("arquivo", type=Path, help="caminho do programa .mini")
    parser.add_argument(
        "--tokens", action="store_true",
        help="imprime a lista de tokens (linha:coluna, tipo e lexema)",
    )
    parser.add_argument(
        "--ast", action="store_true",
        help="imprime a árvore sintática abstrata indentada (sem semântica)",
    )
    parser.add_argument(
        "--tipos", action="store_true",
        help="roda a semântica e imprime a AST anotada com o tipo de cada "
             "expressão",
    )
    parser.add_argument(
        "--contexto", action="store_true",
        help="mostra, sob cada erro semântico, a linha do fonte com um ^ "
             "no ponto do erro",
    )
    parser.add_argument(
        "--verificar", action="store_true",
        help="verifica léxico, sintaxe e semântica (também é o padrão)",
    )
    args = parser.parse_args(argv)
    # --ast é uma visão sintática. Com --tipos/--verificar, a análise
    # continua até a semântica. --tokens pode acompanhar qualquer visão.

    # A árvore usa caracteres como "├──"; num terminal sem UTF-8 (ex.: saída
    # redirecionada no Windows) eles viram "?" em vez de derrubar o programa.
    for fluxo in (sys.stdout, sys.stderr):
        if hasattr(fluxo, "reconfigure"):
            fluxo.reconfigure(errors="replace")

    try:
        fonte = args.arquivo.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as erro:
        print(f"erro ao ler '{args.arquivo}': {erro}", file=sys.stderr)
        return 1

    # 1 · lexer: texto -> list[Token]
    lexer = Lexer(fonte)
    toks = lexer.tokens()
    if lexer.erros:                      # erros léxicos -> stderr, sai 1
        for msg in lexer.erros:
            print(msg, file=sys.stderr)
        return 1

    if args.tokens:
        for tok in toks:
            print(formatar_token(tok))
        if not (args.ast or args.tipos or args.verificar):
            # só --tokens: dispensa o parser
            return 0

    # 2 · parser: list[Token] -> Programa
    try:
        programa = Parser(toks).programa()
    except ErroSintatico as erro:        # erro sintático -> stderr, sai 1
        print(erro, file=sys.stderr)
        return 1

    if args.ast:
        print(formatar_ast(programa))
        if not (args.tipos or args.verificar):
            return 0

    # 3 · semântica: Programa -> AST validada e tipada (aulas 20 e 22)
    analisador = analisar(programa)
    if analisador.erros:                 # erros semânticos -> stderr, sai 1
        linhas_fonte = fonte.splitlines()
        for msg, (lin, col) in zip(analisador.erros, analisador.posicoes):
            print(msg, file=sys.stderr)
            if args.contexto:
                for extra in contexto(linhas_fonte, lin, col):
                    print(extra, file=sys.stderr)
        # Com erro, só os erros aparecem (avisos ficariam no meio deles) e
        # nenhum código é gerado: as próximas fases só recebem AST válida.
        return 1
    for msg in analisador.avisos:        # avisos -> stderr, não impedem
        print(msg, file=sys.stderr)

    if args.tipos:
        print(formatar_ast(programa))
    if args.verificar or not args.tipos:
        print(f"{args.arquivo}: tudo certim, sem erros léxicos, sintáticos "
              "ou semânticos")
    return 0


def contexto(linhas_fonte, linha, coluna):
    """Desafio da aula 22: linha do fonte e um ^ sob a coluna, como no Clang.

        3 | uai (x) { y = 2; }
          |      ^
    """
    if not (1 <= linha <= len(linhas_fonte)) or coluna < 1:
        return []                        # AST montada à mão, sem posição
    texto = linhas_fonte[linha - 1]
    # Copia tabulações do próprio fonte para o ^ alinhar em qualquer terminal.
    recuo = "".join(c if c == "\t" else " " for c in texto[:coluna - 1])
    margem = " " * len(str(linha))
    return [f" {linha} | {texto}", f" {margem} | {recuo}^"]


if __name__ == "__main__":
    raise SystemExit(main())

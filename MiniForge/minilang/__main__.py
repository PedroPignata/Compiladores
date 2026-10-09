"""Ponto de entrada da etapa de especificação: leitura e eco do fonte."""

import argparse
from pathlib import Path
import sys


def main() -> int:
    parser = argparse.ArgumentParser(
        description="MiniForge / MiniLang: nesta etapa, apenas lê e imprime o fonte."
    )
    parser.add_argument("arquivo", type=Path, help="caminho do programa .mini")
    args = parser.parse_args()
    try:
        fonte = args.arquivo.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as erro:
        print(f"erro ao ler '{args.arquivo}': {erro}", file=sys.stderr)
        return 1
    print(fonte, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

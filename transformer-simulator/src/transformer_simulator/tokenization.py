"""Tokenizador didático baseado em expressões regulares Unicode."""

from __future__ import annotations

import re


TOKEN_PATTERN = re.compile(r"\w+(?:[-’']\w+)*|[^\w\s]", re.UNICODE)
PUNCTUATION = frozenset(".,!?;:%)]}»")
OPENING = frozenset("([{«")


def tokenize(text: str) -> list[str]:
    """Separa palavras, números e sinais de pontuação em tokens."""

    return TOKEN_PATTERN.findall(text)


def token_category(token: str) -> str:
    if token.isalpha():
        return "palavra"
    if token.isdigit():
        return "número"
    if len(token) == 1 and not token.isalnum():
        return "pontuação/especial"
    return "token misto"


def detokenize(tokens: list[str] | tuple[str, ...]) -> str:
    """Reconstrói texto sem inserir espaços antes de pontuação de fechamento."""

    result = ""
    previous = ""
    for token in tokens:
        if not result:
            result = token
        elif token in PUNCTUATION:
            result += token
        elif previous in OPENING:
            result += token
        else:
            result += f" {token}"
        previous = token
    return result

"""Vocabulário pequeno e auditável usado pela simulação."""

from __future__ import annotations

from .models import TokenInfo
from .tokenization import token_category


# cada palavra conhecida tem um numero fixo usado pelo simulador
VOCABULARY: dict[str, int] = {
    "<pad>": 0,
    "<unk>": 1,
    "<bos>": 2,
    "<eos>": 3,
    ".": 8,
    "?": 9,
    "!": 10,
    ",": 11,
    "a": 12,
    ":": 13,
    ";": 14,
    "+": 15,
    "=": 16,
    "qual": 101,
    "é": 87,
    "o": 28,
    "um": 29,
    "uma": 30,
    "capital": 345,
    "do": 64,
    "brasil": 728,
    "brasília": 729,
    "2": 202,
    "4": 204,
    "igual": 310,
    "que": 311,
    "compilador": 430,
    "traduz": 431,
    "código": 432,
    "fonte": 433,
    "para": 434,
    "outra": 435,
    "representação": 436,
    "não": 500,
    "tenho": 501,
    "resposta": 502,
    "cadastrada": 503,
    "essa": 504,
    "pergunta": 505,
    "entendi": 510,
    "você": 511,
    "apresentou": 512,
    "frase": 513,
    "afirmativa": 514,
    "são": 601,
    "rio": 602,
    "salvador": 603,
    "recife": 604,
}


def assign_token_ids(tokens: list[str]) -> tuple[TokenInfo, ...]:
    """Associa IDs estáveis e usa UNK para palavras desconhecidas"""

    # percorre os tokens e procura cada um no vocabulario
    result: list[TokenInfo] = []
    for position, token in enumerate(tokens):
        key = token.casefold()
        known = key in VOCABULARY
        # se a palavra nao existir ela recebe o ID reservado para desconhecidos
        result.append(
            TokenInfo(
                text=token,
                position=position,
                token_id=VOCABULARY.get(key, VOCABULARY["<unk>"]),
                known=known,
                category=token_category(token),
            )
        )
    return tuple(result)

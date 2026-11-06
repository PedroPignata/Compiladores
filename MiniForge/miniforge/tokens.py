"""Tipos de token, Token e tabela de palavras reservadas (aula 08)."""

from dataclasses import dataclass
from enum import Enum, auto


class TipoToken(Enum):
    # literais e nomes
    NUM = auto(); ID = auto()
    # palavras reservadas
    VAR = auto(); INT = auto(); BOOL = auto()
    TRUE = auto(); FALSE = auto(); IF = auto()
    ELSE = auto(); WHILE = auto(); PRINT = auto()
    # operadores
    MAIS = auto(); MENOS = auto(); VEZES = auto()
    DIV = auto(); ATRIB = auto(); IGUAL = auto()
    DIFERENTE = auto(); MENOR = auto(); MAIOR = auto()
    MENOR_IGUAL = auto(); MAIOR_IGUAL = auto()
    # delimitadores
    ABRE_PAR = auto(); FECHA_PAR = auto()
    ABRE_CHAVE = auto(); FECHA_CHAVE = auto()
    DOIS_PONTOS = auto(); PONTO_VIRG = auto()
    # fim de arquivo
    EOF = auto()


@dataclass
class Token:
    tipo: TipoToken
    lexema: str
    linha: int
    coluna: int


# Mineirês (v0.6): as palavras reservadas da linguagem. O compilador inteiro
# trabalha com os tipos de token (T.VAR, T.IF, ...) e com os nomes internos
# dos tipos ("int", "bool"); só esta tabela e as mensagens sabem que o
# programa foi escrito em mineirês. Trocar a linguagem de superfície é trocar
# esta tabela.
RESERVADAS = {
    "trem": TipoToken.VAR,              # var   — "trem x: inteirim = 1;"
    "inteirim": TipoToken.INT,          # int
    "booleanim": TipoToken.BOOL,        # bool
    "eh_memo": TipoToken.TRUE,          # true  — "é mêmo"
    "num_eh": TipoToken.FALSE,          # false — "num é"
    "uai": TipoToken.IF,                # if
    "sinao": TipoToken.ELSE,            # else  — "sinão"
    "enquanto_tiver": TipoToken.WHILE,  # while
    "mostra_so": TipoToken.PRINT,       # print — "mostra, sô"
}

# Nome de cada tipo interno como o programador mineiro escreve (mensagens).
NOME_TIPO = {"int": "inteirim", "bool": "booleanim"}

# Tipo interno de cada token de tipo (o parser guarda "int"/"bool" na AST).
TIPO_INTERNO = {TipoToken.INT: "int", TipoToken.BOOL: "bool"}

# Como cada valor booleano aparece no fonte e na saída do programa.
LITERAL_BOOL = {True: "eh_memo", False: "num_eh"}


def nome_tipo(tipo):
    """Nome mineiro de um tipo interno ("int" -> "inteirim")."""
    return NOME_TIPO.get(tipo, tipo)


# Operadores e delimitadores. Os de 2 caracteres são testados antes dos de 1
# (maior casamento): "<=" é um token só, não "<" seguido de "=".
OPERADORES_2 = {
    "==": TipoToken.IGUAL,
    "!=": TipoToken.DIFERENTE,
    "<=": TipoToken.MENOR_IGUAL,
    ">=": TipoToken.MAIOR_IGUAL,
}

OPERADORES_1 = {
    "+": TipoToken.MAIS,
    "-": TipoToken.MENOS,
    "*": TipoToken.VEZES,
    "/": TipoToken.DIV,
    "=": TipoToken.ATRIB,
    "<": TipoToken.MENOR,
    ">": TipoToken.MAIOR,
    "(": TipoToken.ABRE_PAR,
    ")": TipoToken.FECHA_PAR,
    "{": TipoToken.ABRE_CHAVE,
    "}": TipoToken.FECHA_CHAVE,
    ":": TipoToken.DOIS_PONTOS,
    ";": TipoToken.PONTO_VIRG,
}

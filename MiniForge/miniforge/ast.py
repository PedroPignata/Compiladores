"""Nós da árvore sintática abstrata com posição no fonte (aulas 14 e 22).

Uma dataclass por construção da linguagem, todas herdando de No. Os campos
linha e coluna são keyword-only: não entram na ordem dos campos posicionais
e todo nó pode recebê-los como linha=..., coluna=... . A análise semântica
(aula 22) e a VM (aula 28) usam essa posição para apontar onde o erro
aconteceu, quando os tokens já não existem mais. A coluna é o desafio da
aula 22 (mostrar a linha do fonte com um ^ sob o erro) e fica fora da
comparação entre nós, para os testes que só informam a linha continuarem
valendo.

As expressões herdam de Expr, que acrescenta o campo tipo: None depois do
parser e "int" ou "bool" depois da análise semântica (aula 22), que anota a
AST com no.tipo = ... . A geração de código lê esse campo em vez de
recalcular os tipos.

A AST guarda só o que importa para as fases seguintes: não há ';', parênteses
nem níveis intermediários (expr, soma, termo, fator). A precedência já está
codificada na forma da árvore.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from .tokens import LITERAL_BOOL, nome_tipo


@dataclass
class No:
    linha: int = field(default=0, kw_only=True)
    coluna: int = field(default=0, kw_only=True, compare=False)


@dataclass
class Expr(No):
    """Base das expressões: guarda o tipo anotado pela semântica (aula 22)."""
    tipo: Optional[str] = field(default=None, kw_only=True, compare=False,
                                repr=False)


# ----------------------------------------------------------------------
# programa e comandos
# ----------------------------------------------------------------------
@dataclass
class Programa(No):
    comandos: List[No]


@dataclass
class Decl(No):          # trem nome: tipo = expr;
    nome: str
    tipo: str            # "int" ou "bool"
    expr: No


@dataclass
class Atrib(No):         # nome = expr;
    nome: str
    expr: No


@dataclass
class Print(No):         # mostra_so(expr);
    expr: No


@dataclass
class Leitura(No):
    nome: str


@dataclass
class Mensagem(No):
    texto: str


@dataclass
class Bloco(No):         # { comandos }
    comandos: List[No]


@dataclass
class If(No):            # uai (cond) entao [sinao senao]
    cond: No
    entao: Bloco
    senao: Optional[Bloco] = None


@dataclass
class While(No):         # enquanto_tiver (cond) corpo
    cond: No
    corpo: Bloco


# ----------------------------------------------------------------------
# expressões
# ----------------------------------------------------------------------
@dataclass
class Binario(Expr):     # esq op dir
    op: str
    esq: No
    dir: No


@dataclass
class Unario(Expr):      # op expr  (só "-" nesta versão)
    op: str
    expr: No


@dataclass
class Num(Expr):
    valor: int


@dataclass
class Bool(Expr):
    valor: bool


@dataclass
class Var(Expr):
    nome: str


# ----------------------------------------------------------------------
# pretty-printer (desafio da aula 14; formato do slide da aula 16)
# ----------------------------------------------------------------------
def rotulo(no):
    """Texto de um nó na árvore indentada, sem os filhos.

    Depois da análise semântica, as expressões mostram o tipo anotado:
    "Binario + : int".
    """
    texto = _rotulo_sem_tipo(no)
    if isinstance(no, Expr) and no.tipo is not None:
        texto += f" : {nome_tipo(no.tipo)}"
    return texto


def _rotulo_sem_tipo(no):
    if isinstance(no, Leitura):
        return f"Leitura {no.nome}"
    if isinstance(no, Mensagem):
        return f"Mensagem {no.texto!r}"
    if isinstance(no, Decl):
        return f"Decl {no.nome}: {nome_tipo(no.tipo)}"
    if isinstance(no, Atrib):
        return f"Atrib {no.nome}"
    if isinstance(no, (Binario, Unario)):
        return f"{type(no).__name__} {no.op}"
    if isinstance(no, Num):
        return f"Num {no.valor}"
    if isinstance(no, Bool):
        return f"Bool {LITERAL_BOOL[no.valor]}"
    if isinstance(no, Var):
        return f"Var {no.nome}"
    return type(no).__name__          # Programa, Print, Bloco, If, While


def filhos(no):
    """Subárvores de um nó, na ordem em que aparecem no fonte."""
    if isinstance(no, (Programa, Bloco)):
        return list(no.comandos)
    if isinstance(no, (Decl, Atrib, Print, Unario)):
        return [no.expr]
    if isinstance(no, If):
        return [no.cond, no.entao] + ([no.senao] if no.senao is not None else [])
    if isinstance(no, While):
        return [no.cond, no.corpo]
    if isinstance(no, Binario):
        return [no.esq, no.dir]
    return []                          # Num, Bool, Var são folhas


def formatar_ast(raiz):
    """AST indentada, um nó por linha (formato do slide da aula 16):

        Programa
        ├── Decl x: int
        │   └── Num 1
        └── Atrib x
            └── Binario +
                ├── Var x
                └── Num 2
    """
    linhas = [rotulo(raiz)]

    def visitar(no, prefixo):
        lista = filhos(no)
        for i, filho in enumerate(lista):
            ultimo = i == len(lista) - 1
            linhas.append(prefixo + ("└── " if ultimo else "├── ") + rotulo(filho))
            visitar(filho, prefixo + ("    " if ultimo else "│   "))

    visitar(raiz, "")
    return "\n".join(linhas)

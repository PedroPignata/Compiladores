"""Representação intermediária: código de três endereços, TAC (aula 26).

O GeradorTAC percorre a AST já validada e tipada pela semântica (aula 22) e
produz uma lista linear de Instr. Cada instrução tem no máximo um operador e
três endereços (destino + 2 fontes), nas formas do slide 2 da aula 26:

    FORMA                 Instr(op, dest, a1, a2)
    x = y                 ("=",       "x",  y)            cópia
    t = a op b            ("+",       "t1", a, b)         + - * / < > <= >= == !=
    t = -a                ("neg",     "t1", a)            unário
    goto L                ("goto",    "L1")
    ifFalse t goto L      ("iffalse", "L2", t)            salta se t for falso
    L:                    ("label",   "L1")
    print a               ("print",   None, a)

Um operando ("endereço") é um int (constante inteira), um bool (constante
booleana, impressa como eh_memo/num_eh) ou uma str (nome de variável ou de
temporário). Os rótulos só aparecem no campo dest de label, goto e iffalse,
nunca como operando. O campo linha guarda a linha do fonte que originou a
instrução, para a VM (aula 28) apontar erros de execução (divisão por zero).

Expressões devolvem o próprio endereço: Num, Bool e Var devolvem o valor ou
o nome; Binario e Unario emitem uma instrução e devolvem um temporário novo.
Os temporários (t1, t2, ...) e os rótulos (L1, L2, ...) vêm de contadores que
só crescem, então nunca se repetem no programa.

A geração não verifica mais nada: a AST que chega aqui é válida ("frontend
completo", aula 22).

Nomes internos (docs/arquitetura.md, cuidado 4): a memória da VM é plana, mas
a MiniForge permite sombreamento. Por isso cada variável declarada recebe um
nome interno próprio:

    * a 1ª declaração de um nome mantém o nome do fonte (x);
    * a k-ésima declaração do mesmo nome, k >= 2, vira x.k (x.2, x.3, ...);
    * um nome com a forma de temporário (t1, t27, ...) vira t1.1 já na 1ª
      declaração, para não colidir com os temporários do gerador.

O ponto não pode aparecer num identificador da MiniForge ([a-zA-Z_][a-zA-Z0-9_]*),
então um nome interno nunca coincide com outra variável nem com um temporário.
Programas sem sombreamento (como todos os do slide) ficam com os nomes do
fonte: "x = t2", "n = 5".

"""

from dataclasses import dataclass
import re
from typing import Optional

from .semantica import Visitor, analisar
from .tokens import LITERAL_BOOL

# Operadores binários do TAC (os mesmos da tabela REGRAS da semântica).
OPERADORES = ("+", "-", "*", "/", "<", ">", "<=", ">=", "==", "!=")

_FORMA_DE_TEMP = re.compile(r"t[0-9]+")


def formatar(endereco):
    """Texto de um operando: eh_memo/num_eh para bool, o valor/nome no resto."""
    if isinstance(endereco, bool):        # antes de int: bool é subclasse de int
        return LITERAL_BOOL[endereco]
    return str(endereco)


@dataclass
class Instr:
    op: str                     # '=', '+', ..., 'neg', 'goto', 'iffalse', 'label', 'print'
    dest: Optional[str] = None  # variável/temporário destino, ou rótulo
    a1: object = None
    a2: object = None
    linha: int = 0

    def __str__(self):
        """Formato do slide 2: rótulo na margem, demais com 4 espaços."""
        a1, a2 = formatar(self.a1), formatar(self.a2)
        if self.op == "label":
            return f"{self.dest}:"
        if self.op == "=":
            texto = f"{self.dest} = {a1}"
        elif self.op == "neg":
            texto = f"{self.dest} = -{a1}"
        elif self.op == "goto":
            texto = f"goto {self.dest}"
        elif self.op == "iffalse":
            texto = f"ifFalse {a1} goto {self.dest}"
        elif self.op == "print":
            texto = f"print {a1}"
        elif self.op in OPERADORES:
            texto = f"{self.dest} = {a1} {self.op} {a2}"
        else:
            raise ValueError(f"instrução TAC desconhecida: {self.op!r}")
        return "    " + texto


class _GeradorBase(Visitor):
    """Contadores de rótulos e nomes internos únicos por declaração.

    Base do GeradorTAC.
    """

    def __init__(self):
        self.codigo, self.nt, self.nl = [], 0, 0
        self.escopos = [{}]               # nome do fonte -> nome interno
        self._declaracoes = {}            # nome do fonte -> quantas vezes

    def novo_rotulo(self):
        self.nl += 1
        return f"L{self.nl}"

    def declarar(self, nome):
        """Cria o nome interno da variável declarada agora no escopo atual."""
        k = self._declaracoes.get(nome, 0) + 1
        self._declaracoes[nome] = k
        if k == 1 and not _FORMA_DE_TEMP.fullmatch(nome):
            interno = nome
        else:
            interno = f"{nome}.{k}"
        self.escopos[-1][nome] = interno
        return interno

    def nome_interno(self, nome):
        """Resolve como a tabela de símbolos: do escopo mais interno para fora."""
        for escopo in reversed(self.escopos):
            if nome in escopo:
                return escopo[nome]
        # A semântica garante que não acontece; um KeyError aqui é um bug.
        raise KeyError(f"'{nome}' sem declaração: a AST não foi validada?")

    def visitar_Programa(self, no):
        for c in no.comandos:
            self.visitar(c)
        return self.codigo

    def visitar_Bloco(self, no):
        self.escopos.append({})
        for c in no.comandos:
            self.visitar(c)
        self.escopos.pop()


class GeradorTAC(_GeradorBase):
    """AST validada -> lista de Instr. visitar(programa) devolve o código."""

    def novo_temp(self):
        self.nt += 1
        return f"t{self.nt}"

    def emitir(self, op, dest=None, a1=None, a2=None, linha=0):
        self.codigo.append(Instr(op, dest, a1, a2, linha))

    # ------------------------------------------------------------------
    # comandos
    # ------------------------------------------------------------------
    def visitar_Decl(self, no):
        # O inicializador é gerado antes de declarar o nome, como na
        # semântica: em trem x: inteirim = x + 1; o x da direita é o externo.
        a = self.visitar(no.expr)
        self.emitir("=", self.declarar(no.nome), a, linha=no.linha)

    def visitar_Atrib(self, no):
        a = self.visitar(no.expr)
        self.emitir("=", self.nome_interno(no.nome), a, linha=no.linha)

    def visitar_Print(self, no):
        a = self.visitar(no.expr)
        self.emitir("print", None, a, linha=no.linha)

    def visitar_If(self, no):
        # t = <código de c>; ifFalse t goto L_senao; <S1>; goto L_fim;
        # L_senao: <S2>; L_fim:   (sem else, <S2> fica vazio)
        senao, fim = self.novo_rotulo(), self.novo_rotulo()
        c = self.visitar(no.cond)
        self.emitir("iffalse", senao, c, linha=no.linha)
        self.visitar(no.entao)
        self.emitir("goto", fim, linha=no.linha)
        self.emitir("label", senao, linha=no.linha)
        if no.senao is not None:
            self.visitar(no.senao)
        self.emitir("label", fim, linha=no.linha)

    def visitar_While(self, no):
        # L_ini: t = <código de c>; ifFalse t goto L_fim; <S>; goto L_ini; L_fim:
        ini, fim = self.novo_rotulo(), self.novo_rotulo()
        self.emitir("label", ini, linha=no.linha)
        c = self.visitar(no.cond)
        self.emitir("iffalse", fim, c, linha=no.linha)
        self.visitar(no.corpo)
        self.emitir("goto", ini, linha=no.linha)
        self.emitir("label", fim, linha=no.linha)

    # ------------------------------------------------------------------
    # expressões: devolvem o endereço do valor
    # ------------------------------------------------------------------
    def visitar_Binario(self, no):
        a = self.visitar(no.esq)
        b = self.visitar(no.dir)
        t = self.novo_temp()
        self.emitir(no.op, t, a, b, linha=no.linha)
        return t                          # endereço do resultado

    def visitar_Unario(self, no):
        a = self.visitar(no.expr)
        t = self.novo_temp()
        self.emitir("neg", t, a, linha=no.linha)
        return t

    def visitar_Num(self, no):
        return no.valor                   # constante int

    def visitar_Bool(self, no):
        return no.valor                   # constante bool (True/False)

    def visitar_Var(self, no):
        return self.nome_interno(no.nome)


def gerar_tac(programa):
    """Atalho: TAC de uma AST já validada por analisar()."""
    erros = analisar(programa).erros
    if erros:
        raise ValueError("AST semanticamente inválida: " + "; ".join(erros))
    return GeradorTAC().visitar(programa)


def formatar_tac(codigo):
    """Texto do TAC, uma instrução por linha (o que --tac imprime)."""
    return "\n".join(str(i) for i in codigo)

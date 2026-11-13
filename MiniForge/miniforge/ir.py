"""Geração de TAC com nomes internos únicos e posição de origem."""

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
        """Mantém rótulos na margem e recua as instruções."""
        a1, a2 = formatar(self.a1), formatar(self.a2)
        if self.op == "random":
            return f"    {self.dest} = sorteia {a1}, {a2}"
        if self.op == "read":
            return f"    read {self.dest}"
        if self.op == "texto":
            return f"    texto {self.dest!r}"
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

    # comandos

    def visitar_Decl(self, no):
        # O inicializador é gerado antes de declarar o nome, como na
        # semântica: em trem x: inteirim = x + 1; o x da direita é o externo.
        a = self.visitar(no.expr)
        self.emitir("=", self.declarar(no.nome), a, linha=no.linha)

    def visitar_Atrib(self, no):
        a = self.visitar(no.expr)
        self.emitir("=", self.nome_interno(no.nome), a, linha=no.linha)

    def visitar_Leitura(self, no):
        self.emitir('read', self.nome_interno(no.nome), linha=no.linha)

    def visitar_Mensagem(self, no):
        self.emitir('texto', no.texto, linha=no.linha)

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

    # expressões: devolvem o endereço do valor

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

    def visitar_Sorteio(self, no):
        minimo = self.visitar(no.minimo)
        maximo = self.visitar(no.maximo)
        destino = self.novo_temp()
        self.emitir('random', destino, minimo, maximo, linha=no.linha)
        return destino

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

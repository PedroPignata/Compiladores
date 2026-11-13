"""Construção da AST por análise descendente com precedência explícita."""

from . import ast as A
from .lexer import Lexer
from .tokens import TIPO_INTERNO
from .tokens import TipoToken as T

COMPARADORES = (T.IGUAL, T.DIFERENTE, T.MENOR, T.MAIOR,
                T.MENOR_IGUAL, T.MAIOR_IGUAL)


class ErroSintatico(Exception):
    """Erro sintático com posição: 'L:C: erro sintático: msg, sô: achei ...'."""

    def __init__(self, mensagem, linha=0, coluna=0):
        super().__init__(mensagem)
        self.linha = linha
        self.coluna = coluna


class Parser:
    def __init__(self, tokens):
        tokens = list(tokens)
        if not tokens or tokens[-1].tipo != T.EOF:
            raise ValueError("a lista de tokens deve terminar em EOF")
        self.tokens = tokens
        self.pos = 0

    # utilitários

    def atual(self):
        """Devolve o token corrente, sem consumir."""
        return self.tokens[self.pos]

    def verificar(self, *tipos):
        """O token atual é de um desses tipos?"""
        return self.atual().tipo in tipos

    def consumir(self):
        """Devolve o token atual e avança (nunca passa do EOF)."""
        tok = self.atual()
        if tok.tipo != T.EOF:
            self.pos += 1
        return tok

    def esperar(self, tipo, msg):
        """Consome se casar; senão, lança ErroSintatico."""
        if self.verificar(tipo):
            return self.consumir()
        raise self.erro(msg)

    def erro(self, msg):
        """ErroSintatico apontando para o token atual."""
        t = self.atual()
        return ErroSintatico(
            f"{t.linha}:{t.coluna}: erro sintático: {msg}, sô: "
            f"achei '{t.lexema or 'EOF'}'",
            t.linha, t.coluna)

    # programa e comandos

    def programa(self):            # programa → { comando } EOF
        comandos = []
        while not self.verificar(T.EOF):      # vai até o EOF: um '}' sobrando
            comandos.append(self.comando())   # cai em comando() e é acusado
        return A.Programa(comandos, linha=1, coluna=1)

    def comando(self):             # escolhe pela FIRST
        if self.verificar(T.VAR):         return self.decl()
        if self.verificar(T.ID):          return self.atrib()
        if self.verificar(T.READ):        return self.leitura()
        if self.verificar(T.PRINT):       return self.print_()
        if self.verificar(T.IF):          return self.if_()
        if self.verificar(T.WHILE):       return self.while_()
        if self.verificar(T.ABRE_CHAVE):  return self.bloco()
        raise self.erro("comando fora do lugar")

    def decl(self):                # decl → "trem" ID ":" tipo "=" expr ";"
        ini = self.esperar(T.VAR, "faltou 'trem'")
        nome = self.esperar(T.ID, "faltou um nome")
        self.esperar(T.DOIS_PONTOS, "faltou ':'")
        tipo = self.tipo()
        self.esperar(T.ATRIB, "faltou '='")
        expr = self.expr()
        self.esperar(T.PONTO_VIRG, "faltou ';'")
        return A.Decl(nome.lexema, tipo, expr, linha=ini.linha,
                      coluna=ini.coluna)

    def tipo(self):                # tipo → "inteirim" | "booleanim"
        if self.verificar(T.INT, T.BOOL):       # "inteirim" -> "int" na AST
            return TIPO_INTERNO[self.consumir().tipo]
        raise self.erro("faltou o tipo ('inteirim' ou 'booleanim')")

    def atrib(self):               # atrib → ID "=" expr ";"
        nome = self.esperar(T.ID, "faltou um nome")
        self.esperar(T.ATRIB, "faltou '='")
        expr = self.expr()
        self.esperar(T.PONTO_VIRG, "faltou ';'")
        return A.Atrib(nome.lexema, expr, linha=nome.linha,
                       coluna=nome.coluna)

    def leitura(self):
        ini = self.esperar(T.READ, "faltou 'le_so'")
        self.esperar(T.ABRE_PAR, "faltou '('")
        nome = self.esperar(T.ID, "faltou um nome")
        self.esperar(T.FECHA_PAR, "faltou ')'")
        self.esperar(T.PONTO_VIRG, "faltou ';'")
        return A.Leitura(nome.lexema, linha=ini.linha, coluna=ini.coluna)

    def print_(self):              # print → "mostra_so" "(" expr ")" ";"
        ini = self.esperar(T.PRINT, "faltou 'mostra_so'")
        self.esperar(T.ABRE_PAR, "faltou '('")
        if self.verificar(T.TEXTO):
            texto = self.consumir().lexema[1:-1]
            self.esperar(T.FECHA_PAR, "faltou ')'")
            self.esperar(T.PONTO_VIRG, "faltou ';'")
            return A.Mensagem(texto, linha=ini.linha, coluna=ini.coluna)
        expr = self.expr()
        self.esperar(T.FECHA_PAR, "faltou ')'")
        self.esperar(T.PONTO_VIRG, "faltou ';'")
        return A.Print(expr, linha=ini.linha, coluna=ini.coluna)

    def if_(self):                 # if → "uai" "(" expr ")" bloco [ "sinao" bloco ]
        ini = self.esperar(T.IF, "faltou 'uai'")
        self.esperar(T.ABRE_PAR, "faltou '('")
        cond = self.expr()
        self.esperar(T.FECHA_PAR, "faltou ')'")
        entao = self.bloco()
        senao = None
        if self.verificar(T.ELSE):
            self.consumir()
            senao = self.bloco()
        return A.If(cond, entao, senao, linha=ini.linha, coluna=ini.coluna)

    def while_(self):              # while → "enquanto_tiver" "(" expr ")" bloco
        ini = self.esperar(T.WHILE, "faltou 'enquanto_tiver'")
        self.esperar(T.ABRE_PAR, "faltou '('")
        cond = self.expr()
        self.esperar(T.FECHA_PAR, "faltou ')'")
        corpo = self.bloco()
        return A.While(cond, corpo, linha=ini.linha, coluna=ini.coluna)

    def bloco(self):               # bloco → "{" { comando } "}"
        ini = self.esperar(T.ABRE_CHAVE, "faltou '{'")
        comandos = []
        while not self.verificar(T.FECHA_CHAVE, T.EOF):
            comandos.append(self.comando())
        self.esperar(T.FECHA_CHAVE, "faltou '}'")
        return A.Bloco(comandos, linha=ini.linha, coluna=ini.coluna)

    # expressões: um método por nível de precedência

    def expr(self):                # expr → soma [ comparador soma ]
        esq = self.soma()
        if self.verificar(*COMPARADORES):     # [ ] e não { }: não associativa
            op = self.consumir()
            esq = A.Binario(op.lexema, esq, self.soma(),
                            linha=op.linha, coluna=op.coluna)
        return esq

    def soma(self):                # soma → termo { ("+"|"-") termo }
        esq = self.termo()
        while self.verificar(T.MAIS, T.MENOS):
            op = self.consumir()
            esq = A.Binario(op.lexema, esq, self.termo(),
                            linha=op.linha, coluna=op.coluna)
        return esq                 # o laço gera associatividade à esquerda

    def termo(self):               # termo → fator { ("*"|"/") fator }
        esq = self.fator()
        while self.verificar(T.VEZES, T.DIV):
            op = self.consumir()
            esq = A.Binario(op.lexema, esq, self.fator(),
                            linha=op.linha, coluna=op.coluna)
        return esq

    def fator(self):               # fator → NUM | "eh_memo" | "num_eh" | ID
        t = self.atual()           #       | "(" expr ")" | "-" fator
        if self.verificar(T.NUM):
            self.consumir()
            return A.Num(int(t.lexema), linha=t.linha, coluna=t.coluna)
        if self.verificar(T.TRUE, T.FALSE):
            self.consumir()
            return A.Bool(t.tipo == T.TRUE, linha=t.linha, coluna=t.coluna)
        if self.verificar(T.ID):
            self.consumir()
            return A.Var(t.lexema, linha=t.linha, coluna=t.coluna)
        if self.verificar(T.ABRE_PAR):
            self.consumir()
            e = self.expr()
            self.esperar(T.FECHA_PAR, "faltou ')'")
            return e               # parênteses não viram nó: a forma da árvore basta
        if self.verificar(T.MENOS):
            self.consumir()
            return A.Unario("-", self.fator(), linha=t.linha,
                            coluna=t.coluna)
        raise self.erro("faltou uma expressão")


def parse(fonte):
    """Atalho: texto -> Programa. Não verifica erros léxicos (a CLI verifica)."""
    return Parser(Lexer(fonte).tokens()).programa()

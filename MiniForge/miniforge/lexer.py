"""Análise léxica manual e recuperação de erros (aulas 08 e 10).

O lexer percorre o fonte caractere a caractere. Cada ramo de
proximo_token() corresponde a um caminho do autômato finito:

    q0 --letra ou _--> q1 (laço em letra, dígito, _)  -> aceita ID/reservada
    q0 --dígito------> q2 (laço em dígito)            -> aceita NUM

Regras de prioridade: maior casamento (whilex é ID; <= é um token só) e
reservadas consultadas na tabela RESERVADAS depois de ler a palavra inteira.

Erros léxicos usam recuperação em modo pânico: a mensagem vai para
self.erros, o caractere inválido é descartado e a análise continua.
"""

from .tokens import OPERADORES_1, OPERADORES_2, RESERVADAS, Token
from .tokens import TipoToken as T

FIM = ""  # valor de atual()/proximo() quando o fonte acabou


def eh_letra(c):
    """Letra ASCII ou _ — início de identificador: [a-zA-Z_]."""
    return ("a" <= c <= "z") or ("A" <= c <= "Z") or c == "_"


def eh_digito(c):
    """Dígito decimal ASCII: [0-9]."""
    return "0" <= c <= "9"


class Lexer:
    def __init__(self, fonte):
        self.fonte = fonte
        self.pos = 0          # índice do caractere atual em fonte
        self.linha = 1        # linha e coluna do caractere atual, a partir de 1
        self.coluna = 1
        self.erros = []       # mensagens "linha:coluna: erro léxico: ..."

    # ------------------------------------------------------------------
    # utilitários de leitura
    # ------------------------------------------------------------------
    def atual(self):
        """Caractere na posição atual, sem consumir ("" no fim)."""
        if self.pos < len(self.fonte):
            return self.fonte[self.pos]
        return FIM

    def proximo(self):
        """Caractere seguinte ao atual, sem consumir ("" no fim)."""
        if self.pos + 1 < len(self.fonte):
            return self.fonte[self.pos + 1]
        return FIM

    def avancar(self):
        """Consome o caractere atual e atualiza linha e coluna."""
        c = self.atual()
        self.pos += 1
        if c == "\n":
            self.linha += 1
            self.coluna = 1
        else:
            self.coluna += 1
        return c

    # ------------------------------------------------------------------
    # espaços e comentários
    # ------------------------------------------------------------------
    def pular_espacos_e_comentarios(self):
        while True:
            c = self.atual()
            if c in (" ", "\t", "\r", "\n"):
                self.avancar()
            elif c == "/" and self.proximo() == "/":
                while self.atual() not in ("\n", FIM):   # // até o fim da linha
                    self.avancar()
            else:
                return

    # ------------------------------------------------------------------
    # reconhecimento de um token
    # ------------------------------------------------------------------
    def proximo_token(self):
        """Devolve o próximo Token, ou None quando houve erro léxico."""
        self.pular_espacos_e_comentarios()
        lin, col = self.linha, self.coluna
        c = self.atual()

        if c == FIM:
            return Token(T.EOF, "", lin, col)

        if eh_letra(c):                                  # q0 --letra--> q1
            ini = self.pos
            while eh_letra(self.atual()) or eh_digito(self.atual()):
                self.avancar()                           # laço em q1
            lex = self.fonte[ini:self.pos]
            tipo = RESERVADAS.get(lex, T.ID)             # reservada ou ID?
            return Token(tipo, lex, lin, col)

        if eh_digito(c):                                 # q0 --dígito--> q2
            ini = self.pos
            while eh_digito(self.atual()):
                self.avancar()                           # laço em q2
            return Token(T.NUM, self.fonte[ini:self.pos], lin, col)

        dois = c + self.proximo()                        # 2 caracteres primeiro
        if dois in OPERADORES_2:
            self.avancar()
            self.avancar()
            return Token(OPERADORES_2[dois], dois, lin, col)

        if c in OPERADORES_1:
            self.avancar()
            return Token(OPERADORES_1[c], c, lin, col)

        # nenhum padrão casou: modo pânico
        self.avancar()                                   # descarta o caractere
        self.erros.append(f"{lin}:{col}: erro léxico: caractere inválido '{c}', "
                         "que trem é esse?")
        return None                                      # tokens() ignora e segue

    def tokens(self):
        """Lista completa de tokens, terminando sempre em EOF."""
        lista = []
        while True:
            tok = self.proximo_token()
            if tok is None:
                continue
            lista.append(tok)
            if tok.tipo == T.EOF:
                return lista


def formatar_token(tok):
    """Uma linha da saída de --tokens: posição, tipo e lexema."""
    pos = f"{tok.linha}:{tok.coluna}"
    return f"{pos:<6}{tok.tipo.name:<13}'{tok.lexema}'"

"""Análise semântica por Visitor: nomes, escopos e tipos (aulas 20 e 22).

O AnalisadorSemantico percorre a AST uma vez, sem executar o programa, e
verifica as 5 regras semânticas da MiniForge (slide da aula 22):

    1. Toda variável é declarada antes do uso.
    2. Não há redeclaração no mesmo escopo.
    3. Em trem x: T = e; e x = e; , o tipo de e é igual ao de x.
    4. A condição de if e while é bool.
    5. Cada operador recebe os tipos da tabela REGRAS.

Todos os erros são acumulados (a análise não para no primeiro), no formato
único "linha L: erro semântico: <mensagem>":

    'x' num foi declarado, sô                            regra 1
    'x' já foi declarado neste escopo, uai               regra 2
    'b' é booleanim, mas tá recebendo inteirim           regra 3
    condição tem que ser booleanim, mas veio inteirim    regra 4
    operador '+' num serve pra booleanim e inteirim      regra 5
    operador '-' num serve pra booleanim                 regra 5 (unário)

Os tipos são "int" e "bool" por dentro; nome_tipo() os traduz para o
mineirês (inteirim, booleanim) só na hora de montar a mensagem.

Cada visitar_* de expressão devolve "int", "bool" ou None, e anota o nó com
no.tipo. None quer dizer "um erro já foi reportado aqui dentro": quem recebe
None não reporta de novo, e assim um único engano gera uma única mensagem
(sem erros em cascata). Em mostra_so(z + 1 + 2); com z não declarada sai só
"'z' num foi declarado, sô", e não mais duas queixas sobre as somas.

Desafio da aula 20: variáveis declaradas e nunca lidas geram um aviso (não
erro), como o -Wunused-variable do GCC: "linha L: aviso: 'x' declarado e
nunca usado, sô".

Desafio da aula 22: cada erro guarda também a coluna do nó (em .posicoes,
paralela a .erros), para a CLI mostrar a linha do fonte com um ^ sob o
ponto do erro, no estilo GCC/Clang (opção --contexto).

Frontend completo: uma AST sem erros aqui está toda tipada, e as fases
seguintes (TAC, VM) não precisam checar mais nada.
"""

from .simbolos import TabelaSimbolos
from .tokens import nome_tipo

INT, BOOL = "int", "bool"

# Tabela de tipos dos operadores binários: (op, esq, dir) -> resultado.
REGRAS = {}
for op in "+-*/":
    REGRAS[(op, INT, INT)] = INT
for op in ("<", ">", "<=", ">="):
    REGRAS[(op, INT, INT)] = BOOL
for op in ("==", "!="):
    REGRAS[(op, INT, INT)] = BOOL
    REGRAS[(op, BOOL, BOOL)] = BOOL
del op

# Operador unário: (op, operando) -> resultado.
REGRAS_UNARIO = {("-", INT): INT}


class Visitor:
    """Despacho pelo nome da classe: Bloco -> visitar_Bloco(no)."""

    def visitar(self, no):
        nome = "visitar_" + type(no).__name__
        return getattr(self, nome)(no)


class AnalisadorSemantico(Visitor):
    def __init__(self):
        self.tabela = TabelaSimbolos()
        self.erros = []                # "linha L: erro semântico: ..."
        self.posicoes = []             # (linha, coluna) de cada erro, mesma ordem
        self.avisos = []
        self._nao_usados = []          # símbolos com usos == 0 ao sair do escopo

    def erro(self, no, mensagem):
        self.erros.append(f"linha {no.linha}: erro semântico: {mensagem}")
        self.posicoes.append((no.linha, no.coluna))

    def _fechar_escopo(self, simbolos):
        self._nao_usados.extend(s for s in simbolos.values() if s.usos == 0)

    def checar_condicao(self, cond):
        """Regra 4: a condição de if/while precisa ser bool."""
        t = self.visitar(cond)
        if t and t != BOOL:
            self.erro(cond, f"condição tem que ser {nome_tipo('bool')}, mas veio {nome_tipo(t)}")

    # ------------------------------------------------------------------
    # programa e comandos
    # ------------------------------------------------------------------
    def visitar_Programa(self, no):
        # O escopo global (nível 0) já existe na tabela: não empilha outro.
        for c in no.comandos:
            self.visitar(c)
        self._fechar_escopo(self.tabela.escopos[0])
        self.avisos = [
            f"linha {s.linha}: aviso: '{s.nome}' declarado e nunca usado, sô"
            for s in sorted(self._nao_usados, key=lambda s: s.linha)
        ]
        # Devolve a lista de erros: o teste do slide da aula 26 faz
        # assert AnalisadorSemantico().visitar(arv) == [] antes de gerar TAC.
        return self.erros

    def visitar_Bloco(self, no):
        self.tabela.entrar_escopo()
        for c in no.comandos:
            self.visitar(c)
        self._fechar_escopo(self.tabela.sair_escopo())

    def visitar_Decl(self, no):
        # Regra 3. O inicializador é visitado antes de declarar o nome
        # (trem x: inteirim = x + 1; não enxerga o próprio x).
        t = self.visitar(no.expr)
        if t and t != no.tipo:
            self.erro(no, f"'{no.nome}' é {nome_tipo(no.tipo)}, mas tá "
                          f"recebendo {nome_tipo(t)}")
        # Regra 2. Mesmo com inicializador errado, o nome é declarado com o
        # tipo escrito pelo programador: os usos seguintes não viram uma
        # cascata de "'x' num foi declarado, sô".
        if self.tabela.declarar(no.nome, no.tipo, no.linha) is None:
            self.erro(no, f"'{no.nome}' já foi declarado neste escopo, uai")

    def visitar_Atrib(self, no):
        # Regras 1 e 3. Atribuir não é ler: não conta como uso para o aviso.
        s = self.tabela.buscar(no.nome)
        if s is None:
            self.erro(no, f"'{no.nome}' num foi declarado, sô")
        t = self.visitar(no.expr)
        if s is not None and t and t != s.tipo:
            self.erro(no, f"'{no.nome}' é {nome_tipo(s.tipo)}, mas tá "
                          f"recebendo {nome_tipo(t)}")

    def visitar_Print(self, no):
        self.visitar(no.expr)          # print aceita int e bool

    def visitar_If(self, no):
        self.checar_condicao(no.cond)
        self.visitar(no.entao)         # Bloco: cria o próprio escopo
        if no.senao is not None:
            self.visitar(no.senao)

    def visitar_While(self, no):
        self.checar_condicao(no.cond)
        self.visitar(no.corpo)

    # ------------------------------------------------------------------
    # expressões: devolvem o tipo (ou None) e anotam a AST
    # ------------------------------------------------------------------
    def visitar_Binario(self, no):
        te, td = self.visitar(no.esq), self.visitar(no.dir)
        if te is None or td is None:
            return None                # evita erro em cascata
        res = REGRAS.get((no.op, te, td))
        if res is None:
            self.erro(no, f"operador '{no.op}' num serve pra {nome_tipo(te)} e "
                          f"{nome_tipo(td)}")
        no.tipo = res                  # anota a AST
        return res

    def visitar_Unario(self, no):
        t = self.visitar(no.expr)
        if t is None:
            return None                # evita erro em cascata
        res = REGRAS_UNARIO.get((no.op, t))
        if res is None:
            self.erro(no, f"operador '{no.op}' num serve pra {nome_tipo(t)}")
        no.tipo = res
        return res

    def visitar_Num(self, no):
        no.tipo = INT
        return INT

    def visitar_Bool(self, no):
        no.tipo = BOOL
        return BOOL

    def visitar_Var(self, no):
        s = self.tabela.buscar(no.nome)
        if s is None:
            self.erro(no, f"'{no.nome}' num foi declarado, sô")
            return None
        s.usos += 1
        no.tipo = s.tipo               # o tipo vem da tabela de símbolos
        return s.tipo


def analisar(programa):
    """Atalho: roda o analisador sobre a AST e o devolve (com .erros e .avisos).

    Se analisar(p).erros estiver vazio, toda expressão de p tem no.tipo.
    """
    analisador = AnalisadorSemantico()
    analisador.visitar(programa)
    return analisador

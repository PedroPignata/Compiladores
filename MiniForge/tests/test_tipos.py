"""Testes da verificação de tipos e da AST anotada (aula 22).

Cobrem as 5 regras semânticas, a tabela REGRAS de operadores, a anotação
no.tipo em cada expressão, a ausência de erros em cascata, o exemplo
exemplos/semantico.mini do slide de entrega, a CLI (todos os erros de uma
vez, código 1, sem gerar código) e o desafio do ^ sob a coluna do erro.
"""

import pathlib
import subprocess
import sys

import pytest

from miniforge import ast as A
from miniforge.parser import parse
from miniforge.semantica import REGRAS, AnalisadorSemantico, analisar

RAIZ = pathlib.Path(__file__).parent.parent
VALIDOS = sorted((RAIZ / "tests" / "casos" / "validos").glob("*.mini"))


def sem(fonte):
    return analisar(parse(fonte)).erros


def tipo_de(expr_fonte, decl=""):
    """Tipo anotado na expressão de print(<expr>);."""
    prog = parse(f"{decl}mostra_so({expr_fonte});")
    a = analisar(prog)
    assert a.erros == []
    return prog.comandos[-1].expr.tipo


def expressoes(no):
    """Todos os nós de expressão da árvore."""
    if isinstance(no, A.Expr):
        yield no
    for filho in A.filhos(no):
        yield from expressoes(filho)


# ----------------------------------------------------------------------
# tabela de tipos dos operadores
# ----------------------------------------------------------------------
def test_tabela_regras_igual_ao_slide():
    esperado = {}
    for op in "+-*/":
        esperado[(op, "int", "int")] = "int"
    for op in ("<", ">", "<=", ">="):
        esperado[(op, "int", "int")] = "bool"
    for op in ("==", "!="):
        esperado[(op, "int", "int")] = "bool"
        esperado[(op, "bool", "bool")] = "bool"
    assert REGRAS == esperado


@pytest.mark.parametrize("expr, tipo", [
    ("1 + 2", "int"),                 # exemplos do slide
    ("1 < 2", "bool"),
    ("eh_memo == num_eh", "bool"),
    ("7 / 2", "int"),
    ("2 * 3 - 1", "int"),
    ("1 != 2", "bool"),
    ("3 >= 3", "bool"),
    ("-5", "int"),
    ("-(1 + 2)", "int"),
    ("(1 < 2) == (3 > 4)", "bool"),
    ("(1 == 1) != num_eh", "bool"),
    ("eh_memo", "bool"),
    ("42", "int"),
])
def test_tipo_das_expressoes(expr, tipo):
    assert tipo_de(expr) == tipo


@pytest.mark.parametrize("expr, msg", [
    ("eh_memo + 1", "operador '+' num serve pra booleanim e inteirim"),     # do slide
    ("1 == eh_memo", "operador '==' num serve pra inteirim e booleanim"),   # do slide
    ("num_eh - eh_memo", "operador '-' num serve pra booleanim e booleanim"),
    ("2 / num_eh", "operador '/' num serve pra inteirim e booleanim"),
    ("eh_memo > num_eh", "operador '>' num serve pra booleanim e booleanim"),
    ("1 <= eh_memo", "operador '<=' num serve pra inteirim e booleanim"),
    ("eh_memo != 0", "operador '!=' num serve pra booleanim e inteirim"),
    ("-eh_memo", "operador '-' num serve pra booleanim"),
    ("-(1 < 2)", "operador '-' num serve pra booleanim"),
])
def test_operadores_com_tipos_invalidos(expr, msg):
    assert sem(f"mostra_so({expr});") == [f"linha 1: erro semântico: {msg}"]


# ----------------------------------------------------------------------
# regras 3 e 4: declarações, atribuições e condições
# ----------------------------------------------------------------------
def test_decl_com_tipo_errado():                 # caso do slide
    assert sem("trem b: booleanim = 1 + 2;\nmostra_so(b);") == [
        "linha 1: erro semântico: 'b' é booleanim, mas tá recebendo inteirim"]


def test_decl_int_recebe_bool():
    assert sem("trem n: inteirim = eh_memo;\nmostra_so(n);") == [
        "linha 1: erro semântico: 'n' é inteirim, mas tá recebendo booleanim"]


def test_decl_com_tipo_certo():
    assert sem("trem n: inteirim = 2 * 3;\ntrem b: booleanim = n > 1;\nmostra_so(b);") == []


def test_atribuicao_com_tipo_errado():
    fonte = "trem x: inteirim = 1;\nx = x < 2;\nmostra_so(x);"
    assert sem(fonte) == ["linha 2: erro semântico: 'x' é inteirim, mas tá recebendo booleanim"]


def test_atribuicao_usa_o_tipo_da_variavel_visivel():
    fonte = "trem x: booleanim = eh_memo;\n{\n  trem x: inteirim = 0;\n  x = 1;\n  mostra_so(x);\n}\nx = num_eh;\nmostra_so(x);"
    assert sem(fonte) == []


@pytest.mark.parametrize("cmd", ["uai", "enquanto_tiver"])
def test_condicao_int(cmd):
    assert sem(f"{cmd} (1) {{ }}") == [
        "linha 1: erro semântico: condição tem que ser booleanim, mas veio inteirim"]


def test_condicao_bool_variavel_e_comparacao():
    assert sem("trem c: booleanim = eh_memo;\nuai (c) { }\nenquanto_tiver (1 > 2) { }\nuai (c == num_eh) { }") == []


def test_condicao_de_variavel_int():
    assert sem("trem n: inteirim = 1;\nenquanto_tiver (n) { n = n - 1; }") == [
        "linha 2: erro semântico: condição tem que ser booleanim, mas veio inteirim"]


def test_print_aceita_int_e_bool():
    assert sem("mostra_so(1);\nmostra_so(eh_memo);\nmostra_so(1 < 2);") == []


# ----------------------------------------------------------------------
# anotação da AST
# ----------------------------------------------------------------------
def test_ast_anotada_em_todos_os_nos_de_expressao():
    fonte = ("trem n: inteirim = 5;\n"
             "trem ok: booleanim = (-n < 0) == eh_memo;\n"
             "enquanto_tiver (n > 0) { n = n - 1; }\n"
             "mostra_so(ok);")
    prog = parse(fonte)
    assert analisar(prog).erros == []
    exprs = list(expressoes(prog))
    assert len(exprs) == 14
    assert all(e.tipo in ("int", "bool") for e in exprs)


def test_tipos_anotados_no_lugar_certo():
    prog = parse("trem x: inteirim = 1;\ntrem b: booleanim = x + 1 < 3;\nmostra_so(b);")
    analisar(prog)
    cmp_ = prog.comandos[1].expr                       # x + 1 < 3
    assert (cmp_.op, cmp_.tipo) == ("<", "bool")
    assert (cmp_.esq.op, cmp_.esq.tipo) == ("+", "int")
    assert (cmp_.esq.esq.nome, cmp_.esq.esq.tipo) == ("x", "int")
    assert cmp_.dir.tipo == "int"
    assert prog.comandos[2].expr.tipo == "bool"        # Var b


def test_var_recebe_o_tipo_da_declaracao_visivel():
    prog = parse("trem x: inteirim = 1;\n{ trem x: booleanim = eh_memo; mostra_so(x); }\nmostra_so(x);")
    analisar(prog)
    interno = prog.comandos[1].comandos[1].expr
    externo = prog.comandos[2].expr
    assert (interno.tipo, externo.tipo) == ("bool", "int")


def test_parser_deixa_tipo_vazio():
    prog = parse("mostra_so(1 + 2);")
    assert all(e.tipo is None for e in expressoes(prog))


def test_tipo_nao_entra_na_comparacao_de_nos():
    prog = parse("mostra_so(1);")
    analisar(prog)
    assert prog.comandos[0].expr == A.Num(1, linha=1)


@pytest.mark.parametrize("arq", VALIDOS, ids=lambda p: p.name)
def test_casos_validos_ficam_totalmente_tipados(arq):
    prog = parse(arq.read_text(encoding="utf-8"))
    assert analisar(prog).erros == []
    assert all(e.tipo in ("int", "bool") for e in expressoes(prog))


def test_formatar_ast_mostra_tipos_depois_da_semantica():
    prog = parse("trem x: inteirim = 1 + 2;\nmostra_so(x < 4);")
    analisar(prog)
    assert A.formatar_ast(prog) == (
        "Programa\n"
        "├── Decl x: inteirim\n"
        "│   └── Binario + : inteirim\n"
        "│       ├── Num 1 : inteirim\n"
        "│       └── Num 2 : inteirim\n"
        "└── Print\n"
        "    └── Binario < : booleanim\n"
        "        ├── Var x : inteirim\n"
        "        └── Num 4 : inteirim"
    )


# ----------------------------------------------------------------------
# sem erros em cascata
# ----------------------------------------------------------------------
def test_sem_cascata_em_somas():                 # exemplo do slide
    assert sem("mostra_so(z + 1 + 2);") == [
        "linha 1: erro semântico: 'z' num foi declarado, sô"]


def test_sem_cascata_operador_invalido_dentro_de_outro():
    # true + 1 já é erro; o "* 2" e o "< 3" de fora não reclamam de novo.
    assert sem("mostra_so((eh_memo + 1) * 2 < 3);") == [
        "linha 1: erro semântico: operador '+' num serve pra booleanim e inteirim"]


def test_sem_cascata_unario():
    assert sem("mostra_so(-(-ausente));") == [
        "linha 1: erro semântico: 'ausente' num foi declarado, sô"]


def test_sem_cascata_condicao_e_declaracao():
    fonte = ("uai (a < 1) { }\n"
             "trem b: booleanim = c + 1;\n"
             "d = 1 + eh_memo;")
    assert sem(fonte) == [
        "linha 1: erro semântico: 'a' num foi declarado, sô",
        "linha 2: erro semântico: 'c' num foi declarado, sô",
        "linha 3: erro semântico: 'd' num foi declarado, sô",
        "linha 3: erro semântico: operador '+' num serve pra inteirim e booleanim",
    ]


def test_decl_errada_ainda_declara_o_nome():
    fonte = "trem q: inteirim = eh_memo;\nq = q + 1;\nmostra_so(q);"
    assert sem(fonte) == ["linha 1: erro semântico: 'q' é inteirim, mas tá recebendo booleanim"]


def test_erros_independentes_no_mesmo_operador_sao_todos_reportados():
    assert sem("mostra_so(a + b);") == [
        "linha 1: erro semântico: 'a' num foi declarado, sô",
        "linha 1: erro semântico: 'b' num foi declarado, sô",
    ]


def test_todos_os_erros_de_uma_vez_na_ordem():
    fonte = ("trem x: inteirim = 1;\n"
             "trem x: inteirim = 2;\n"
             "trem b: booleanim = x;\n"
             "enquanto_tiver (x) { b = 3; }\n"
             "mostra_so(eh_memo + x);\n"
             "mostra_so(-b);\n"
             "{ trem y: inteirim = 1; mostra_so(y); } y = 2;")
    assert sem(fonte) == [
        "linha 2: erro semântico: 'x' já foi declarado neste escopo, uai",
        "linha 3: erro semântico: 'b' é booleanim, mas tá recebendo inteirim",
        "linha 4: erro semântico: condição tem que ser booleanim, mas veio inteirim",
        "linha 4: erro semântico: 'b' é booleanim, mas tá recebendo inteirim",
        "linha 5: erro semântico: operador '+' num serve pra booleanim e inteirim",
        "linha 6: erro semântico: operador '-' num serve pra booleanim",
        "linha 7: erro semântico: 'y' num foi declarado, sô",
    ]


# ----------------------------------------------------------------------
# exemplo do slide de entrega e posições (desafio)
# ----------------------------------------------------------------------
SAIDA_SLIDE = [
    "linha 2: erro semântico: 'b' é booleanim, mas tá recebendo inteirim",
    "linha 3: erro semântico: condição tem que ser booleanim, mas veio inteirim",
    "linha 3: erro semântico: 'y' num foi declarado, sô",
]


def test_exemplo_semantico_do_slide():
    fonte = (RAIZ / "exemplos" / "semantico.mini").read_text(encoding="utf-8")
    assert sem(fonte) == SAIDA_SLIDE


def test_posicoes_paralelas_aos_erros():
    fonte = (RAIZ / "exemplos" / "semantico.mini").read_text(encoding="utf-8")
    a = analisar(parse(fonte))
    assert a.posicoes == [(2, 1), (3, 6), (3, 11)]


def test_coluna_dos_nos_vem_do_token():
    prog = parse("trem a: inteirim = 1;\n  mostra_so(a + 20);")
    p = prog.comandos[1]
    assert (p.linha, p.coluna) == (2, 3)
    soma = p.expr
    assert (soma.coluna, soma.esq.coluna, soma.dir.coluna) == (15, 13, 17)


def test_ast_montada_a_mao_sem_coluna():
    a = AnalisadorSemantico()
    a.visitar(A.Programa([A.Print(A.Var("q", linha=7), linha=7)]))
    assert a.posicoes == [(7, 0)]


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------
def cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "miniforge", *args],
        cwd=RAIZ, capture_output=True, text=True, encoding="utf-8")


def test_cli_saida_do_slide():
    r = cli("exemplos/semantico.mini")
    assert r.returncode == 1
    assert r.stdout == ""                        # nada de código gerado
    assert r.stderr.splitlines() == SAIDA_SLIDE  # avisos não se misturam


def test_cli_programa_valido():
    r = cli("exemplos/fatorial.mini", "--verificar")
    assert r.returncode == 0
    assert r.stdout == "exemplos/fatorial.mini: tudo certim, sem erros léxicos, sintáticos ou semânticos\n"
    assert r.stderr == ""


def test_cli_tipos_imprime_ast_anotada():
    r = cli("exemplos/if_else.mini", "--tipos")
    assert r.returncode == 0
    linhas = r.stdout.splitlines()
    assert linhas[0] == "Programa"
    assert "│   └── Num 3 : inteirim" in linhas
    assert "│   └── Binario < : booleanim" in linhas


def test_cli_tipos_com_erro_nao_imprime_ast():
    r = cli("exemplos/semantico.mini", "--tipos")
    assert r.returncode == 1
    assert r.stdout == ""


def test_cli_ast_continua_sem_semantica():
    r = cli("exemplos/semantico.mini", "--ast")
    assert r.returncode == 0
    assert "Binario + : inteirim" not in r.stdout     # AST sem tipos anotados
    assert "Binario +" in r.stdout


def test_cli_contexto_com_circunflexo():
    r = cli("exemplos/semantico.mini", "--contexto")
    assert r.returncode == 1
    assert r.stderr.splitlines() == [
        "linha 2: erro semântico: 'b' é booleanim, mas tá recebendo inteirim",
        " 2 | trem b: booleanim = x + 1;",
        "   | ^",
        "linha 3: erro semântico: condição tem que ser booleanim, mas veio inteirim",
        " 3 | uai (x) { y = 2; }",
        "   |      ^",
        "linha 3: erro semântico: 'y' num foi declarado, sô",
        " 3 | uai (x) { y = 2; }",
        "   |           ^",
    ]


def test_cli_contexto_alinha_com_tabulacao(tmp_path):
    arq = tmp_path / "tab.mini"
    arq.write_text("{\n\tmostra_so(1 + eh_memo);\n}\n", encoding="utf-8")
    r = cli(str(arq), "--contexto")
    assert r.returncode == 1
    assert r.stderr.splitlines() == [
        "linha 2: erro semântico: operador '+' num serve pra inteirim e booleanim",
        " 2 | \tmostra_so(1 + eh_memo);",
        "   | \t            ^",
    ]

"""Testes do parser recursivo descendente e da AST."""

import pathlib
import subprocess
import sys

import pytest

from miniforge import ast as A
from miniforge.lexer import Lexer
from miniforge.parser import ErroSintatico, Parser

RAIZ = pathlib.Path(__file__).resolve().parent.parent


def parse(fonte):
    return Parser(Lexer(fonte).tokens()).programa()


def erro_de(fonte):
    with pytest.raises(ErroSintatico) as info:
        parse(fonte)
    return str(info.value)


def test_precedencia():
    e = parse("x = 1 + 2 * 3;").comandos[0].expr
    assert e.op == "+" and e.dir.op == "*"


def test_associatividade_esquerda():
    e = parse("x = 10 - 3 - 2;").comandos[0].expr
    assert e.op == "-" and e.esq.op == "-"


def test_falta_ponto_virgula():
    with pytest.raises(ErroSintatico, match="faltou ';'"):
        parse("trem x: inteirim = 1")

# forma da AST


def test_ast_completa_do_slide():
    p = parse("trem x: inteirim = 1;\nx = x + 2 * 3;")
    assert p == A.Programa([
        A.Decl("x", "int", A.Num(1, linha=1), linha=1),
        A.Atrib("x", A.Binario(
            "+", A.Var("x", linha=2),
            A.Binario("*", A.Num(2, linha=2), A.Num(3, linha=2), linha=2),
            linha=2), linha=2),
    ], linha=1)


def test_todo_no_herda_de_no_e_tem_linha():
    for cls in (A.Programa, A.Decl, A.Atrib, A.Print, A.Bloco, A.If, A.While,
                A.Binario, A.Unario, A.Num, A.Bool, A.Var):
        assert issubclass(cls, A.No)
    assert A.Num(7).linha == 0                      # padrão
    assert A.Num(7, linha=3).linha == 3             # keyword-only
    with pytest.raises(TypeError):
        A.Num(7, 3)                                 # linha não é posicional


def test_linhas_dos_nos():
    p = parse("trem a: inteirim = 1;\n\nenquanto_tiver (a < 3) {\n  a = a + 1;\n}")
    w = p.comandos[1]
    assert isinstance(w, A.While) and w.linha == 3
    assert w.cond.linha == 3 and w.corpo.linha == 3
    assert w.corpo.comandos[0].linha == 4
    assert w.corpo.comandos[0].expr.linha == 4


def test_parenteses_mudam_agrupamento_e_nao_viram_no():
    e = parse("x = (1 + 2) * 3;").comandos[0].expr
    assert e.op == "*" and isinstance(e.esq, A.Binario) and e.esq.op == "+"


def test_termo_associa_a_esquerda():
    e = parse("x = 8 / 4 / 2;").comandos[0].expr
    assert e.op == "/" and e.esq.op == "/" and e.dir == A.Num(2, linha=1)


def test_multiplicacao_antes_de_soma_a_esquerda():
    e = parse("x = 2 * 3 + 4;").comandos[0].expr
    assert e.op == "+" and e.esq.op == "*"


def test_comparacao_tem_menor_precedencia():
    e = parse("x = 1 + 2 < 3 * 4;").comandos[0].expr
    assert e.op == "<" and e.esq.op == "+" and e.dir.op == "*"

@pytest.mark.parametrize("op", ["==", "!=", "<", ">", "<=", ">="])
def test_todos_os_comparadores(op):
    e = parse(f"x = a {op} b;").comandos[0].expr
    assert e == A.Binario(op, A.Var("a", linha=1), A.Var("b", linha=1), linha=1)


def test_comparacao_nao_associativa():
    assert erro_de("x = a < b < c;") == \
        "1:11: erro sintático: faltou ';', sô: achei '<'"


def test_comparacao_agrupada_com_parenteses_e_aceita():
    e = parse("x = (a < b) == eh_memo;").comandos[0].expr
    assert e.op == "==" and e.esq.op == "<" and e.dir == A.Bool(True, linha=1)


def test_unario():
    e = parse("x = - -4 * 2;").comandos[0].expr
    assert e.op == "*"
    assert e.esq == A.Unario("-", A.Unario("-", A.Num(4, linha=1), linha=1), linha=1)


def test_literais_e_variaveis():
    cmds = parse("mostra_so(eh_memo); mostra_so(num_eh); mostra_so(42); mostra_so(y);").comandos
    assert [c.expr for c in cmds] == [
        A.Bool(True, linha=1), A.Bool(False, linha=1),
        A.Num(42, linha=1), A.Var("y", linha=1)]


def test_decl_bool():
    d = parse("trem ok: booleanim = eh_memo;").comandos[0]
    assert (d.nome, d.tipo, d.expr) == ("ok", "bool", A.Bool(True, linha=1))


def test_if_com_e_sem_else():
    p = parse("uai (a) { mostra_so(1); } sinao { mostra_so(2); }\nuai (b) { }")
    com_else, sem_else = p.comandos
    assert isinstance(com_else.senao, A.Bloco)
    assert com_else.entao.comandos == [A.Print(A.Num(1, linha=1), linha=1)]
    assert sem_else.senao is None and sem_else.entao.comandos == []


def test_blocos_aninhados():
    p = parse("{ { } trem x: inteirim = 1; }")
    externo = p.comandos[0]
    assert isinstance(externo, A.Bloco)
    assert isinstance(externo.comandos[0], A.Bloco)
    assert isinstance(externo.comandos[1], A.Decl)


def test_programa_vazio():
    assert parse("") == A.Programa([], linha=1)
    assert parse("// só comentário\n") == A.Programa([], linha=1)

# erros sintáticos: posição e mensagem


def test_erro_aponta_o_proximo_token():

    assert erro_de("trem x: inteirim = 1\nmostra_so(x);") == \
        "2:1: erro sintático: faltou ';', sô: achei 'mostra_so'"


def test_erro_no_eof():
    assert erro_de("mostra_so(x)") == \
        "1:13: erro sintático: faltou ';', sô: achei 'EOF'"


def test_erro_guarda_linha_e_coluna():
    with pytest.raises(ErroSintatico) as info:
        parse("x = 1;\n  y = ;")
    assert (info.value.linha, info.value.coluna) == (2, 7)

@pytest.mark.parametrize("fonte, esperado", [
    ("trem x inteirim = 1;", "1:8: erro sintático: faltou ':', sô: achei 'inteirim'"),
    ("x = 1 + ;", "1:9: erro sintático: faltou uma expressão, sô: achei ';'"),
    ("uai x > 1 { }", "1:5: erro sintático: faltou '(', sô: achei 'x'"),
    ("1 = x;", "1:1: erro sintático: comando fora do lugar, sô: achei '1'"),
    ("trem b: booleanim = (1 + 2;",
     "1:27: erro sintático: faltou ')', sô: achei ';'"),
    ("trem 1x: inteirim = 0;",
     "1:6: erro sintático: faltou um nome, sô: achei '1'"),
    ("enquanto_tiver (x) { x = x - 1;",
     "1:32: erro sintático: faltou '}', sô: achei 'EOF'"),
    ("x = 1; }", "1:8: erro sintático: comando fora do lugar, sô: achei '}'"),
    ("sinao { }", "1:1: erro sintático: comando fora do lugar, sô: achei 'sinao'"),
    ("trem x: float = 1;",
     "1:9: erro sintático: faltou o tipo ('inteirim' ou 'booleanim'), sô: achei 'float'"),
    ("trem x: inteirim;", "1:17: erro sintático: faltou '=', sô: achei ';'"),
    ("x == 1;", "1:3: erro sintático: faltou '=', sô: achei '=='"),
    ("enquanto_tiver (a) mostra_so(a);",
     "1:20: erro sintático: faltou '{', sô: achei 'mostra_so'"),
    ("uai (a) { } sinao mostra_so(a);",
     "1:19: erro sintático: faltou '{', sô: achei 'mostra_so'"),
    ("mostra_so 1;", "1:11: erro sintático: faltou '(', sô: achei '1'"),
    ("x = ();", "1:6: erro sintático: faltou uma expressão, sô: achei ')'"),
])
def test_mensagens_de_erro(fonte, esperado):
    assert erro_de(fonte) == esperado


def test_parser_exige_eof_no_fim():
    from miniforge.tokens import Token, TipoToken as T
    with pytest.raises(ValueError):
        Parser([Token(T.ID, "x", 1, 1)])

# pretty-printer


def test_ast_indentada_do_slide():
    assert A.formatar_ast(parse("trem x: inteirim = 1;\nx = x + 2 * 3;")) == "\n".join([
        "Programa",
        "├── Decl x: inteirim",
        "│   └── Num 1",
        "└── Atrib x",
        "    └── Binario +",
        "        ├── Var x",
        "        └── Binario *",
        "            ├── Num 2",
        "            └── Num 3",
    ])


def test_ast_indentada_if_while():
    fonte = "enquanto_tiver (a) { uai (-b) { mostra_so(eh_memo); } sinao { } }"
    assert A.formatar_ast(parse(fonte)) == "\n".join([
        "Programa",
        "└── While",
        "    ├── Var a",
        "    └── Bloco",
        "        └── If",
        "            ├── Unario -",
        "            │   └── Var b",
        "            ├── Bloco",
        "            │   └── Print",
        "            │       └── Bool eh_memo",
        "            └── Bloco",
    ])


def cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "miniforge", *args],
        cwd=RAIZ, capture_output=True, text=True, encoding="utf-8")


def test_cli_ast_fatorial():
    r = cli("exemplos/fatorial.mini", "--ast")
    assert r.returncode == 0, r.stderr
    linhas = r.stdout.splitlines()
    assert linhas[:3] == ["Programa", "├── Decl n: inteirim", "│   └── Num 5"]
    assert "├── While" in linhas
    assert linhas[-2:] == ["└── Print", "    └── Var f"]

@pytest.mark.parametrize("arq", ["fatorial.mini", "if_else.mini",
                                 "escopos.mini"])
def test_cli_exemplos_validos(arq):
    r = cli(f"exemplos/{arq}", "--verificar")
    assert r.returncode == 0, r.stderr
    assert r.stdout == f"exemplos/{arq}: tudo certim, sem erros léxicos, sintáticos ou semânticos\n"


def test_cli_ast_nao_depende_da_semantica():
    # erro_semantico.mini é sintaticamente válido: --ast mostra a árvore.
    r = cli("exemplos/erro_semantico.mini", "--ast")
    assert r.returncode == 0, r.stderr
    assert r.stdout.splitlines() == ["Programa", "└── Print", "    └── Var ausente"]


def test_cli_erro_sintatico_sai_com_codigo_1():
    r = cli("exemplos/erro_sintatico.mini", "--ast")
    assert r.returncode == 1
    assert r.stdout == ""
    assert r.stderr == "3:8: erro sintático: faltou ':', sô: achei 'inteirim'\n"


def test_cli_erro_lexico_vem_antes_do_parser():
    r = cli("exemplos/erro_lexico.mini", "--ast")
    assert r.returncode == 1
    assert "erro léxico" in r.stderr and "erro sintático" not in r.stderr


def test_cli_tokens_e_ast_juntos():
    r = cli("exemplos/fatorial.mini", "--tokens", "--ast")
    assert r.returncode == 0
    linhas = r.stdout.splitlines()
    assert linhas[0].split() == ["1:1", "VAR", "'trem'"]
    assert "Programa" in linhas


def test_cli_tokens_nao_depende_do_parser():
    r = cli("exemplos/erro_sintatico.mini", "--tokens")
    assert r.returncode == 0
    assert r.stdout.splitlines()[-1].split()[1] == "EOF"


def test_cli_arquivo_inexistente():
    r = cli("exemplos/nao_existe.mini", "--ast")
    assert r.returncode == 1 and "erro ao ler" in r.stderr

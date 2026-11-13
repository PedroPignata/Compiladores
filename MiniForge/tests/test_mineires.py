"""Verifica vocabulário e integração dos programas mineirês."""

import pathlib
import subprocess
import sys

import pytest

from miniforge.lexer import Lexer
from miniforge.parser import ErroSintatico, parse
from miniforge.semantica import analisar
from miniforge.tokens import LITERAL_BOOL, NOME_TIPO, RESERVADAS, nome_tipo
from miniforge.tokens import TipoToken as T

RAIZ = pathlib.Path(__file__).resolve().parent.parent

VOCABULARIO = {
    "le_so": T.READ,
    "trem": T.VAR, "inteirim": T.INT, "booleanim": T.BOOL,
    "eh_memo": T.TRUE, "num_eh": T.FALSE, "uai": T.IF, "sinao": T.ELSE,
    "enquanto_tiver": T.WHILE, "mostra_so": T.PRINT,
}


def erros(fonte):
    return analisar(parse(fonte)).erros

# vocabulário


def test_vocabulario_completo():
    assert RESERVADAS == VOCABULARIO

@pytest.mark.parametrize("palavra, tipo", sorted(VOCABULARIO.items()))
def test_cada_palavra_vira_o_token_certo(palavra, tipo):
    assert [t.tipo for t in Lexer(palavra).tokens()] == [tipo, T.EOF]

@pytest.mark.parametrize("antiga", ["var", "int", "bool", "true", "false",
                                    "if", "else", "while", "print"])
def test_palavras_do_ingles_viraram_identificadores(antiga):
    toks = Lexer(antiga).tokens()
    assert (toks[0].tipo, toks[0].lexema) == (T.ID, antiga)


def test_da_pra_usar_while_como_nome_de_variavel():
    prog = parse("trem while: inteirim = 3; mostra_so(while * 2);")
    assert analisar(prog).erros == []
    assert prog.comandos[-1].expr.tipo == "int"


def test_maior_casamento_com_sublinhado():
    # "enquanto_tiver_mais" é um nome só; "eh_memo2" também
    assert [t.tipo for t in Lexer("enquanto_tiver_mais eh_memo2 uai_").tokens()] \
        == [T.ID, T.ID, T.ID, T.EOF]


def test_tipos_internos_continuam_int_e_bool():
    prog = parse("trem a: inteirim = 1; trem b: booleanim = num_eh;")
    assert [d.tipo for d in prog.comandos] == ["int", "bool"]
    assert NOME_TIPO == {"int": "inteirim", "bool": "booleanim"}
    assert nome_tipo("int") == "inteirim" and nome_tipo("xyz") == "xyz"

# saída e literais


def test_literais_booleanos():
    prog = parse("mostra_so(eh_memo); mostra_so(num_eh);")
    assert analisar(prog).erros == []
    assert [c.expr.valor for c in prog.comandos] == [True, False]
    assert [c.expr.tipo for c in prog.comandos] == ["bool", "bool"]
    assert LITERAL_BOOL == {True: "eh_memo", False: "num_eh"}


def test_programa_completo_em_mineires():
    fonte = """
        trem n: inteirim = 4;
        trem soma: inteirim = 0;
        enquanto_tiver (n > 0) {
            soma = soma + n;
            n = n - 1;
        }
        uai (soma == 10) { mostra_so(eh_memo); } sinao { mostra_so(num_eh); }
        mostra_so(soma);
    """
    prog = parse(fonte)
    assert analisar(prog).erros == []
    assert prog.comandos[-2].cond.tipo == "bool"
    assert prog.comandos[-2].entao.comandos[0].expr.tipo == "bool"
    assert prog.comandos[-1].expr.tipo == "int"

# mensagens com sotaque


def test_erro_lexico_pergunta_que_trem_e_esse():
    lx = Lexer("trem x: inteirim = 1 # 2;")
    lx.tokens()
    assert lx.erros == ["1:22: erro léxico: caractere inválido '#', que trem é esse?"]

@pytest.mark.parametrize("fonte, esperado", [
    ("trem x: inteirim = 1", "1:21: erro sintático: faltou ';', sô: achei 'EOF'"),
    ("var x: int = 1;", "1:5: erro sintático: faltou '=', sô: achei 'x'"),
    ("trem x: int = 1;",
     "1:9: erro sintático: faltou o tipo ('inteirim' ou 'booleanim'), sô: achei 'int'"),
    ("sinao { }", "1:1: erro sintático: comando fora do lugar, sô: achei 'sinao'"),
])
def test_erros_sintaticos(fonte, esperado):
    with pytest.raises(ErroSintatico) as info:
        parse(fonte)
    assert str(info.value) == esperado

@pytest.mark.parametrize("fonte, esperado", [
    ("mostra_so(x);", "'x' num foi declarado, sô"),
    ("trem a: inteirim = 1; trem a: inteirim = 2; mostra_so(a);",
     "'a' já foi declarado neste escopo, uai"),
    ("trem b: booleanim = 1;", "'b' é booleanim, mas tá recebendo inteirim"),
    ("uai (1) { }", "condição tem que ser booleanim, mas veio inteirim"),
    ("mostra_so(eh_memo + 1);", "operador '+' num serve pra booleanim e inteirim"),
    ("mostra_so(-num_eh);", "operador '-' num serve pra booleanim"),
])
def test_erros_semanticos(fonte, esperado):
    assert erros(fonte) == [f"linha 1: erro semântico: {esperado}"]


def test_aviso_de_trem_sem_uso():
    a = analisar(parse("trem esquecido: inteirim = 1;"))
    assert a.avisos == ["linha 1: aviso: 'esquecido' declarado e nunca usado, sô"]


def test_cli_verificar_diz_tudo_certim():
    r = subprocess.run(
        [sys.executable, "-m", "miniforge", "exemplos/pao_de_queijo.mini",
         "--verificar"],
        cwd=RAIZ, capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0
    assert r.stdout == ("exemplos/pao_de_queijo.mini: tudo certim, sem erros "
                        "léxicos, sintáticos ou semânticos\n")

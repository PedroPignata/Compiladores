"""Testes do analisador léxico (aulas 08 e 10)."""

import pathlib
import subprocess
import sys

import pytest

from miniforge.lexer import Lexer
from miniforge.tokens import RESERVADAS
from miniforge.tokens import TipoToken as T

RAIZ = pathlib.Path(__file__).resolve().parent.parent
EXEMPLOS = RAIZ / "exemplos"


def tipos(fonte):
    return [t.tipo for t in Lexer(fonte).tokens()]


# ----------------------------------------------------------------------
# Aula 08 — tokens
# ----------------------------------------------------------------------
def test_declaracao():
    assert tipos("trem x: inteirim = 10;") == [
        T.VAR, T.ID, T.DOIS_PONTOS, T.INT,
        T.ATRIB, T.NUM, T.PONTO_VIRG, T.EOF]


def test_reservada_vs_identificador():
    assert tipos("enquanto_tiver enquanto_tiverx")[:-1] == [T.WHILE, T.ID]


def test_operadores_de_dois_caracteres():
    assert tipos("<= ==")[:-1] == [T.MENOR_IGUAL, T.IGUAL]


def test_posicao():
    t = Lexer("trem\n  x").tokens()[1]
    assert (t.linha, t.coluna) == (2, 3)


def test_todas_as_reservadas():
    fonte = "trem inteirim booleanim eh_memo num_eh uai sinao enquanto_tiver mostra_so le_so"
    assert tipos(fonte)[:-1] == [
        T.VAR, T.INT, T.BOOL, T.TRUE, T.FALSE,
        T.IF, T.ELSE, T.WHILE, T.PRINT, T.READ]
    assert set(RESERVADAS) == set(fonte.split())


def test_todos_os_operadores_e_delimitadores():
    fonte = "+ - * / = == != < > <= >= ( ) { } : ;"
    assert tipos(fonte)[:-1] == [
        T.MAIS, T.MENOS, T.VEZES, T.DIV, T.ATRIB, T.IGUAL, T.DIFERENTE,
        T.MENOR, T.MAIOR, T.MENOR_IGUAL, T.MAIOR_IGUAL,
        T.ABRE_PAR, T.FECHA_PAR, T.ABRE_CHAVE, T.FECHA_CHAVE,
        T.DOIS_PONTOS, T.PONTO_VIRG]


def test_maior_casamento_sem_espacos():
    toks = Lexer("x<=10>=y==z!=1<2>3=4").tokens()
    assert [t.lexema for t in toks][:-1] == [
        "x", "<=", "10", ">=", "y", "==", "z", "!=", "1", "<", "2",
        ">", "3", "=", "4"]


def test_identificadores_e_numeros():
    toks = Lexer("_tmp contador2 x_1 007 42").tokens()
    assert [(t.tipo, t.lexema) for t in toks][:-1] == [
        (T.ID, "_tmp"), (T.ID, "contador2"), (T.ID, "x_1"),
        (T.NUM, "007"), (T.NUM, "42")]


def test_sinal_negativo_e_operador_separado():
    assert tipos("-4")[:-1] == [T.MENOS, T.NUM]


def test_reservadas_sao_sensiveis_a_maiusculas():
    assert tipos("Uai TREM Eh_memo")[:-1] == [T.ID, T.ID, T.ID]


def test_comentarios_e_espacos_sao_descartados():
    fonte = "// cabeçalho\ntrem\t x // resto da linha\n\r\n;// fim sem quebra"
    toks = Lexer(fonte).tokens()
    assert [t.tipo for t in toks] == [T.VAR, T.ID, T.PONTO_VIRG, T.EOF]
    assert [(t.linha, t.coluna) for t in toks] == [(2, 1), (2, 7), (4, 1), (4, 19)]


def test_divisao_nao_e_comentario():
    assert tipos("a / b")[:-1] == [T.ID, T.DIV, T.ID]


def test_entrada_vazia_gera_so_eof():
    toks = Lexer("").tokens()
    assert len(toks) == 1
    assert (toks[0].tipo, toks[0].lexema, toks[0].linha, toks[0].coluna) == (
        T.EOF, "", 1, 1)


def test_eof_na_linha_seguinte_a_ultima_quebra():
    toks = Lexer("trem x: inteirim = 1;\nx = x + 2 * 3;\n").tokens()
    eof = toks[-1]
    assert (eof.tipo, eof.linha, eof.coluna) == (T.EOF, 3, 1)


def test_posicoes_do_fatorial_como_no_slide():
    toks = Lexer((EXEMPLOS / "fatorial.mini").read_text(encoding="utf-8")).tokens()
    assert [(t.linha, t.coluna, t.tipo, t.lexema) for t in toks[:7]] == [
        (2, 1, T.VAR, "trem"), (2, 6, T.ID, "n"), (2, 7, T.DOIS_PONTOS, ":"),
        (2, 9, T.INT, "inteirim"), (2, 18, T.ATRIB, "="), (2, 20, T.NUM, "5"),
        (2, 21, T.PONTO_VIRG, ";")]


# ----------------------------------------------------------------------
# Aula 10 — erros léxicos com recuperação em modo pânico
# ----------------------------------------------------------------------
def test_erro_lexico_continua():
    lx = Lexer("x @ y")
    assert [t.tipo for t in lx.tokens()] == [T.ID, T.ID, T.EOF]
    assert lx.erros == [
        "1:3: erro léxico: caractere inválido '@', que trem é esse?"]


def test_varios_erros_reportados_de_uma_vez():
    lx = Lexer("trem a: inteirim = 1;\n$ a = a # 2;\n")
    tipos_ok = [t.tipo for t in lx.tokens()]
    assert lx.erros == [
        "2:1: erro léxico: caractere inválido '$', que trem é esse?",
        "2:9: erro léxico: caractere inválido '#', que trem é esse?"]
    assert tipos_ok[-6:] == [T.ID, T.ATRIB, T.ID, T.NUM, T.PONTO_VIRG, T.EOF]


def test_exclamacao_sozinha_e_invalida():
    lx = Lexer("x ! y != z")
    assert [t.tipo for t in lx.tokens()] == [T.ID, T.ID, T.DIFERENTE, T.ID, T.EOF]
    assert lx.erros == ["1:3: erro léxico: caractere inválido '!', que trem é esse?"]


def test_caractere_fora_do_alfabeto_ascii():
    lx = Lexer("trem ação: inteirim = 1;")
    lx.tokens()
    assert lx.erros == [
        "1:7: erro léxico: caractere inválido 'ç', que trem é esse?",
        "1:8: erro léxico: caractere inválido 'ã', que trem é esse?"]


def test_sem_erros_lista_vazia():
    lx = Lexer("mostra_so(1);")
    lx.tokens()
    assert lx.erros == []


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------
def cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "miniforge", *args],
        cwd=RAIZ, capture_output=True, text=True, encoding="utf-8")


def test_cli_tokens_fatorial():
    r = cli("exemplos/fatorial.mini", "--tokens")
    assert r.returncode == 0
    linhas = r.stdout.splitlines()
    assert linhas[0].split() == ["2:1", "VAR", "'trem'"]
    assert linhas[2].split() == ["2:7", "DOIS_PONTOS", "':'"]
    assert linhas[-1].split() == ["9:1", "EOF", "''"]


def test_cli_erro_lexico_sai_com_codigo_1():
    r = cli("exemplos/erro_lexico.mini")
    assert r.returncode == 1
    assert r.stdout == ""
    assert r.stderr.splitlines() == [
        "1:3: erro léxico: caractere inválido '@', que trem é esse?",
        "4:9: erro léxico: caractere inválido '$', que trem é esse?"]


@pytest.mark.parametrize("arq", sorted(
    p.name for p in EXEMPLOS.glob("*.mini") if p.name != "erro_lexico.mini"))
def test_cli_exemplos_lexicamente_validos(arq):
    r = cli(f"exemplos/{arq}", "--tokens")
    assert r.returncode == 0, r.stderr
    assert r.stdout.splitlines()[-1].split()[1] == "EOF"

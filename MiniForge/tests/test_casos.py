"""Valida arquivos de referência e suas mensagens esperadas."""

import pathlib
import re

import pytest

from miniforge.ast import Programa
from miniforge.lexer import Lexer
from miniforge.parser import ErroSintatico, Parser
from miniforge.semantica import analisar

CASOS = pathlib.Path(__file__).parent / "casos"
VALIDOS = sorted((CASOS / "validos").glob("*.mini"))
INVALIDOS = sorted((CASOS / "invalidos").glob("*.mini"))
SEMANTICOS = sorted((CASOS / "semanticos").glob("*.mini"))


def parse(fonte):
    return Parser(Lexer(fonte).tokens()).programa()


def test_banco_tem_pelo_menos_8_de_cada():
    assert len(VALIDOS) >= 8
    assert len(INVALIDOS) >= 8
    assert len(SEMANTICOS) >= 6

@pytest.mark.parametrize("arq", VALIDOS, ids=lambda p: p.name)
def test_validos(arq):
    fonte = arq.read_text(encoding="utf-8")
    lx = Lexer(fonte)
    toks = lx.tokens()
    assert lx.erros == []                    # casos do parser são lexicamente válidos
    assert isinstance(Parser(toks).programa(), Programa)  # não pode lançar exceção

@pytest.mark.parametrize("arq", INVALIDOS, ids=lambda p: p.name)
def test_invalidos(arq):
    fonte = arq.read_text(encoding="utf-8")
    linha1 = fonte.splitlines()[0]
    assert linha1.startswith("// ERRO: "), "1ª linha deve anotar o erro esperado"
    esperado = linha1.removeprefix("// ERRO: ")
    assert Lexer(fonte).tokens() and Lexer(fonte).erros == []  # erro é sintático, não léxico
    with pytest.raises(ErroSintatico, match=re.escape(esperado)) as info:
        parse(fonte)
    # formato completo: "L:C: erro sintático: <mensagem>, sô: achei '...'"
    assert re.fullmatch(
        rf"\d+:\d+: erro sintático: {re.escape(esperado)}, sô: achei '.*'",
        str(info.value))

@pytest.mark.parametrize("arq", SEMANTICOS, ids=lambda p: p.name)
def test_semanticos(arq):
    fonte = arq.read_text(encoding="utf-8")
    linha1 = fonte.splitlines()[0]
    assert linha1.startswith("// ERRO: "), "1ª linha deve anotar o erro esperado"
    esperado = linha1.removeprefix("// ERRO: ")
    lx = Lexer(fonte)
    programa = Parser(lx.tokens()).programa()  # sintaxe válida: não lança
    assert lx.erros == []
    erros = analisar(programa).erros
    assert len(erros) == 1, erros              # exatamente um erro, sem cascata
    assert re.fullmatch(rf"linha \d+: erro semântico: {re.escape(esperado)}",
                        erros[0])

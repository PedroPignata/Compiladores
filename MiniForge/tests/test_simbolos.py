"""Testes da tabela de símbolos isolada, sem AST (aula 20).

Cobrem as 4 operações (entrar_escopo, sair_escopo, declarar, buscar), os 5
atributos do Simbolo, sombreamento, saída de escopo e redeclaração.
"""

import pytest

from miniforge.simbolos import Simbolo, TabelaSimbolos


def test_escopos():                      # teste do slide da aula 20
    ts = TabelaSimbolos()
    ts.declarar("x", "int", 1)
    ts.entrar_escopo()
    ts.declarar("x", "bool", 2)          # sombreia
    assert ts.buscar("x").tipo == "bool"
    ts.sair_escopo()
    assert ts.buscar("x").tipo == "int"
    assert ts.declarar("x", "int", 3) is None


def test_simbolo_tem_os_5_atributos():
    ts = TabelaSimbolos()
    ts.entrar_escopo()
    s = ts.declarar("y", "int", 3)
    assert (s.nome, s.tipo, s.categoria, s.linha, s.nivel) == \
        ("y", "int", "variavel", 3, 1)
    assert s == Simbolo("y", "int", "variavel", 3, 1)


def test_tabela_comeca_so_com_o_global():
    ts = TabelaSimbolos()
    assert ts.escopos == [{}]
    assert ts.nivel == 0
    assert ts.buscar("x") is None


def test_declarar_devolve_o_simbolo_e_guarda_no_escopo_atual():
    ts = TabelaSimbolos()
    s = ts.declarar("x", "int", 1)
    assert s is ts.buscar("x")
    assert ts.escopos[0] == {"x": s}
    assert s.nivel == 0


def test_redeclaracao_no_mesmo_escopo_devolve_none_e_mantem_o_original():
    ts = TabelaSimbolos()
    original = ts.declarar("x", "int", 1)
    assert ts.declarar("x", "bool", 2) is None
    assert ts.buscar("x") is original
    assert ts.buscar("x").tipo == "int"


def test_redeclaracao_em_bloco_interno():
    ts = TabelaSimbolos()
    ts.entrar_escopo()
    assert ts.declarar("y", "int", 2) is not None
    assert ts.declarar("y", "int", 3) is None


def test_mesmo_nome_em_escopo_interno_e_permitido():
    ts = TabelaSimbolos()
    ts.declarar("x", "int", 1)
    ts.entrar_escopo()
    assert ts.declarar("x", "int", 2) is not None    # mesmo tipo também pode


def test_buscar_vai_do_topo_para_a_base():
    # Situação do slide de revisão: x (nível 0), y (nível 1), x (nível 2).
    ts = TabelaSimbolos()
    ts.declarar("x", "int", 1)
    ts.entrar_escopo()
    ts.declarar("y", "int", 3)
    ts.entrar_escopo()
    ts.declarar("x", "bool", 5)
    assert ts.nivel == 2
    assert (ts.buscar("y").nivel, ts.buscar("y").linha) == (1, 3)
    assert (ts.buscar("x").tipo, ts.buscar("x").nivel) == ("bool", 2)
    ts.sair_escopo()
    assert (ts.buscar("x").tipo, ts.buscar("x").linha) == ("int", 1)


def test_nome_de_bloco_interno_invisivel_fora_dele():
    ts = TabelaSimbolos()
    ts.entrar_escopo()
    ts.declarar("y", "int", 1)
    ts.sair_escopo()
    assert ts.buscar("y") is None
    assert ts.declarar("y", "bool", 2) is not None   # pode declarar de novo


def test_sair_escopo_devolve_os_simbolos_do_bloco():
    ts = TabelaSimbolos()
    ts.entrar_escopo()
    a = ts.declarar("a", "int", 1)
    b = ts.declarar("b", "bool", 2)
    assert ts.sair_escopo() == {"a": a, "b": b}
    assert ts.nivel == 0


def test_nao_sai_do_escopo_global():
    ts = TabelaSimbolos()
    with pytest.raises(RuntimeError):
        ts.sair_escopo()
    assert ts.escopos == [{}]


def test_niveis_aumentam_e_diminuem_com_a_pilha():
    ts = TabelaSimbolos()
    for esperado in (1, 2, 3):
        ts.entrar_escopo()
        assert ts.nivel == esperado
        assert ts.declarar(f"v{esperado}", "int", esperado).nivel == esperado
    for esperado in (2, 1, 0):
        ts.sair_escopo()
        assert ts.nivel == esperado
    assert ts.buscar("v1") is None


def test_nomes_sao_sensiveis_a_maiusculas():
    ts = TabelaSimbolos()
    ts.declarar("x", "int", 1)
    assert ts.buscar("X") is None
    assert ts.declarar("X", "bool", 2) is not None

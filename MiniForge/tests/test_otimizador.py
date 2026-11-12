"""Testes estruturais dos passes reaproveitados do ZIP, sem execução."""
import pytest
from pathlib import Path
from miniforge.ir import Instr, gerar_tac, formatar_tac
from miniforge.parser import parse
from miniforge.otimizador import *
RAIZ=Path(__file__).resolve().parent.parent
EXEMPLOS=RAIZ/'exemplos'
def ler(p): return p.read_text(encoding='utf-8')
PROGRAMAS=[ler(p) for p in EXEMPLOS.glob('*.mini') if not p.name.startswith(('erro_', 'semantico'))]
def test_eh_const():
    assert eh_const(0) and eh_const(-3) and eh_const(True) and eh_const(False)
    assert not eh_const("x") and not eh_const("t1") and not eh_const(None)

def test_eh_temporario():
    assert eh_temporario("t1") and eh_temporario("t27")
    for nome in ("t1.1", "x", "t", "tx", "x.2", None, 3):
        assert not eh_temporario(nome)

def test_passes_na_ordem_do_slide():
    assert PASSES == [propagar_constantes, dobrar_constantes,
                      eliminar_saltos_constantes,
                      eliminar_codigo_morto, limpar_rotulos]

@pytest.mark.parametrize("passe", PASSES, ids=lambda p: p.__name__)
def test_passe_nao_altera_a_lista_recebida(passe):
    cod = gerar_tac(parse(ler(EXEMPLOS / "constantes.mini")))
    copia = [Instr(i.op, i.dest, i.a1, i.a2, i.linha) for i in cod]
    novo, mudou = passe(cod)
    assert cod == copia                     # entrada intacta
    assert isinstance(novo, list) and isinstance(mudou, bool)

@pytest.mark.parametrize("passe", PASSES, ids=lambda p: p.__name__)
def test_passe_sobre_lista_vazia(passe):
    assert passe([]) == ([], False)

def test_propagacao_do_slide():
    cod = [Instr("=", "x", 5), Instr("+", "t2", "x", 1)]
    assert propagar_constantes(cod) == (
        [Instr("=", "x", 5), Instr("+", "t2", 5, 1)], True)

def test_propagacao_mantem_a_linha():
    novo, _ = propagar_constantes([Instr("=", "x", 5, linha=1),
                                   Instr("print", None, "x", linha=7)])
    assert novo[1] == Instr("print", None, 5, linha=7)
    assert novo[1].linha == 7

def test_propagacao_nos_dois_operandos_e_em_cadeia():
    cod = [Instr("=", "x", 2), Instr("=", "y", "x"),
           Instr("*", "t1", "x", "y")]
    novo, _ = propagar_constantes(cod)
    assert novo == [Instr("=", "x", 2), Instr("=", "y", 2),
                    Instr("*", "t1", 2, 2)]

def test_propagacao_esquece_no_rotulo():
    cod = [Instr("=", "n", 5), Instr("label", "L1"),
           Instr(">", "t1", "n", 0)]
    assert propagar_constantes(cod) == (cod, False)

@pytest.mark.parametrize("salto", [Instr("goto", "L1"),
                                   Instr("iffalse", "L1", "c")])
def test_propagacao_esquece_no_salto(salto):
    cod = [Instr("=", "n", 5), salto, Instr("print", None, "n")]
    novo, _ = propagar_constantes(cod)
    assert novo[2] == Instr("print", None, "n")

def test_propagacao_troca_a_condicao_do_iffalse():
    cod = [Instr("=", "t4", True), Instr("iffalse", "L1", "t4")]
    novo, mudou = propagar_constantes(cod)
    assert novo[1] == Instr("iffalse", "L1", True) and mudou

def test_propagacao_esquece_valor_reatribuido():
    cod = [Instr("=", "x", 1), Instr("+", "x", "y", 1),
           Instr("print", None, "x")]
    novo, _ = propagar_constantes(cod)
    assert novo[2] == Instr("print", None, "x")
    cod = [Instr("=", "x", 1), Instr("=", "x", "y"),
           Instr("print", None, "x")]
    novo, _ = propagar_constantes(cod)
    assert novo[2] == Instr("print", None, "x")

def test_propagacao_de_bool():
    cod = [Instr("=", "b", False), Instr("print", None, "b")]
    novo, _ = propagar_constantes(cod)
    assert novo[1].a1 is False

def test_propagacao_nao_mexe_no_destino():
    cod = [Instr("=", "x", 1), Instr("=", "x", 2)]
    assert propagar_constantes(cod) == (cod, False)

def test_dobramento_do_slide():
    cod = [Instr("*", "t1", 2, 3, linha=4)]
    novo, mudou = dobrar_constantes(cod)
    assert novo == [Instr("=", "t1", 6, linha=4)] and mudou

@pytest.mark.parametrize("op, a, b, esperado", [
    ("+", 2, 3, 5), ("-", 2, 3, -1), ("*", 4, 5, 20),
    ("/", 7, 2, 3), ("/", -7, 2, -3), ("/", 7, -2, -3), ("/", -7, -2, 3),
    ("<", 1, 2, True), (">", 1, 2, False), ("<=", 2, 2, True),
    (">=", 1, 2, False), ("==", 3, 3, True), ("!=", 3, 3, False),
    ("==", True, False, False), ("!=", True, False, True),
])
def test_dobramento_igual_a_vm(op, a, b, esperado):
    novo, _ = dobrar_constantes([Instr(op, "t1", a, b)])
    assert novo == [Instr("=", "t1", esperado)]
    assert type(novo[0].a1) is type(esperado)     # bool continua bool

def test_dobramento_nunca_dobra_divisao_por_zero():
    cod = [Instr("/", "t1", 5, 0, linha=3)]
    assert dobrar_constantes(cod) == (cod, False)

def test_dobramento_do_unario():
    novo, mudou = dobrar_constantes([Instr("neg", "t1", 5)])
    assert novo == [Instr("=", "t1", -5)] and mudou

def test_dobramento_precisa_das_duas_constantes():
    cod = [Instr("+", "t1", "x", 1), Instr("neg", "t2", "x"),
           Instr("=", "y", 3), Instr("print", None, 4)]
    assert dobrar_constantes(cod) == (cod, False)

def test_iffalse_false_vira_goto():
    novo, mudou = eliminar_saltos_constantes(
        [Instr("iffalse", "L1", False, linha=2)])
    assert novo == [Instr("goto", "L1", linha=2)] and mudou

def test_iffalse_true_e_removido():
    assert eliminar_saltos_constantes(
        [Instr("iffalse", "L1", True)]) == ([], True)

def test_iffalse_com_variavel_fica():
    cod = [Instr("iffalse", "L1", "t1"), Instr("goto", "L2")]
    assert eliminar_saltos_constantes(cod) == (cod, False)

def test_remove_depois_do_goto_ate_o_rotulo():
    cod = [Instr("goto", "L1"), Instr("print", None, 1),
           Instr("=", "x", 2), Instr("label", "L1"),
           Instr("print", None, "x")]
    novo, mudou = eliminar_codigo_morto(cod)
    assert novo == [Instr("goto", "L1"), Instr("label", "L1"),
                    Instr("print", None, "x")] and mudou

def test_remove_depois_do_goto_ate_o_fim():
    cod = [Instr("print", None, 1), Instr("goto", "L1"),
           Instr("print", None, 2)]
    novo, _ = eliminar_codigo_morto(cod)
    assert novo == cod[:2]

def test_depois_do_iffalse_continua_alcancavel():
    cod = [Instr("iffalse", "L1", "c"), Instr("print", None, 1),
           Instr("label", "L1")]
    assert eliminar_codigo_morto(cod) == (cod, False)

def test_remove_temporario_nunca_lido():
    cod = [Instr("=", "t1", 6), Instr("+", "t2", "x", 1),
           Instr("neg", "t3", "x"), Instr("print", None, 1)]
    assert eliminar_codigo_morto(cod) == ([Instr("print", None, 1)], True)

def test_temporario_lido_fica():
    cod = [Instr("=", "t1", 6), Instr("print", None, "t1"),
           Instr("<", "t2", 1, 2), Instr("iffalse", "L1", "t2"),
           Instr("label", "L1")]
    assert eliminar_codigo_morto(cod) == (cod, False)

def test_variavel_do_programa_nunca_e_removida():
    cod = [Instr("=", "base", 10), Instr("=", "t1.1", 3),
           Instr("+", "x", 1, 2)]
    assert eliminar_codigo_morto(cod) == (cod, False)

def test_divisao_que_pode_falhar_fica():
    cod = [Instr("/", "t1", "x", "z"), Instr("/", "t2", 5, 0),
           Instr("/", "t3", "x", 0)]
    assert eliminar_codigo_morto(cod) == (cod, False)

def test_divisao_por_constante_nao_nula_sai():
    assert eliminar_codigo_morto([Instr("/", "t1", "x", 2)]) == ([], True)

def test_goto_para_o_rotulo_seguinte_sai():
    cod = [Instr("iffalse", "L2", "c"), Instr("goto", "L2"),
           Instr("label", "L2")]
    novo, mudou = limpar_rotulos(cod)
    assert novo == [Instr("iffalse", "L2", "c"), Instr("label", "L2")]
    assert mudou

def test_rotulo_sem_referencia_sai():
    cod = [Instr("label", "L1"), Instr("print", None, 1),
           Instr("label", "L2")]
    assert limpar_rotulos(cod) == ([Instr("print", None, 1)], True)

def test_rotulo_referenciado_fica():
    cod = [Instr("label", "L1"), Instr("iffalse", "L2", "c"),
           Instr("goto", "L1"), Instr("label", "L2")]
    assert limpar_rotulos(cod) == (cod, False)

def test_goto_para_outro_rotulo_fica():
    cod = [Instr("goto", "L2"), Instr("label", "L1"), Instr("label", "L2"),
           Instr("iffalse", "L1", "c")]
    assert limpar_rotulos(cod) == (cod, False)

def tac_otimizado(fonte):
    return formatar_tac(otimizar(gerar_tac(parse(fonte)))).splitlines()

def test_ponto_fixo_encadeia_os_passes():
    # propagação -> dobramento -> salto constante -> código morto -> rótulos
    assert tac_otimizado("trem a: inteirim = 10; uai (1 > 2) { mostra_so(a); } "
                         "sinao { mostra_so(a + 1); }") == [
        "    a = 10", "    print 11"]

def test_ponto_fixo_e_idempotente():
    for prog in PROGRAMAS:
        cod = otimizar(gerar_tac(parse(prog)))
        assert otimizar(cod) == cod
        for passe in PASSES:
            assert passe(cod)[1] is False

def test_while_false_some():
    assert tac_otimizado("trem x: inteirim = 0; enquanto_tiver (num_eh) { x = x + 1; } "
                         "mostra_so(x);") == ["    x = 0", "    print 0"]

def test_while_true_fica_sem_o_teste():
    # laço infinito: não roda, só confere o código
    assert tac_otimizado("trem x: inteirim = 0; enquanto_tiver (eh_memo) { x = x + 1; }") == [
        "    x = 0", "L1:", "    t1 = x + 1", "    x = t1", "    goto L1"]

def test_laco_nao_recebe_constante_de_fora():
    linhas = tac_otimizado("trem n: inteirim = 5; enquanto_tiver (n > 0) { n = n - 1; }")
    assert "    t1 = n > 0" in linhas

def test_divisao_por_zero_sobrevive_ao_ponto_fixo():
    assert tac_otimizado("trem z: inteirim = 0; mostra_so(10 / z);") == [
        "    z = 0", "    t1 = 10 / 0", "    print t1"]

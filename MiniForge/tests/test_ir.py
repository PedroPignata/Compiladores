"""Testes TAC estruturais reaproveitados do ZIP; sem executor nem pilha."""
import pathlib
import re
import subprocess
import sys

import pytest

from miniforge import ast as A
from miniforge.ir import (GeradorTAC, Instr,
                          formatar_tac, gerar_tac)
from miniforge.parser import parse
from miniforge.semantica import AnalisadorSemantico, Visitor

RAIZ = pathlib.Path(__file__).parent.parent
VALIDOS = sorted((RAIZ / "tests" / "casos" / "validos").glob("*.mini"))


def tac(fonte):
    arv = parse(fonte)
    assert AnalisadorSemantico().visitar(arv) == []
    return [str(i) for i in GeradorTAC().visitar(arv)]


def tac_de(caminho):
    return tac(pathlib.Path(caminho).read_text(encoding="utf-8"))


def test_expressao():
    assert tac("trem x: inteirim = 1 + 2 * 3;") == [
        "    t1 = 2 * 3",
        "    t2 = 1 + t1",
        "    x = t2"]


def test_while_tem_rotulos_e_saltos():
    cod = tac("trem i: inteirim = 0; enquanto_tiver (i < 3) { i = i + 1; }")
    assert "L1:" in cod and "    goto L1" in cod
    assert "    ifFalse t1 goto L2" in cod


def test_instr_tem_os_campos_do_slide():
    i = Instr("+", "t1", "a", 2, linha=3)
    assert (i.op, i.dest, i.a1, i.a2, i.linha) == ("+", "t1", "a", 2, 3)
    assert Instr("goto", "L1") == Instr("goto", "L1", None, None, 0)

@pytest.mark.parametrize("instr, texto", [
    (Instr("=", "x", "y"), "    x = y"),
    (Instr("=", "x", 5), "    x = 5"),
    (Instr("=", "b", True), "    b = eh_memo"),
    (Instr("=", "b", False), "    b = num_eh"),
    (Instr("*", "t1", 2, 3), "    t1 = 2 * 3"),
    (Instr("<=", "t2", "n", 0), "    t2 = n <= 0"),
    (Instr("!=", "t3", True, "b"), "    t3 = eh_memo != b"),
    (Instr("neg", "t4", "a"), "    t4 = -a"),
    (Instr("goto", "L1"), "    goto L1"),
    (Instr("iffalse", "L2", "t1"), "    ifFalse t1 goto L2"),
    (Instr("label", "L1"), "L1:"),
    (Instr("print", None, "f"), "    print f"),
    (Instr("print", None, 0), "    print 0"),
])
def test_str_no_formato_do_slide_2(instr, texto):
    assert str(instr) == texto


def test_op_desconhecido_e_bug():
    with pytest.raises(ValueError):
        str(Instr("xor", "t1", 1, 2))


def test_gerador_tem_metodo_para_todo_no_da_ast():
    import dataclasses
    nos = [c for c in vars(A).values()
           if isinstance(c, type) and dataclasses.is_dataclass(c)
           and issubclass(c, A.No) and c not in (A.No, A.Expr)]
    for gerador in (GeradorTAC,):
        assert issubclass(gerador, Visitor)
        for classe in nos:
            assert hasattr(gerador, f"visitar_{classe.__name__}"), classe

# expressões


def test_constantes_e_variaveis_nao_geram_temporario():
    assert tac("trem a: inteirim = 7; trem b: booleanim = eh_memo; trem c: inteirim = a;") == [
        "    a = 7",
        "    b = eh_memo",
        "    c = a"]


def test_pos_ordem_e_associatividade_a_esquerda():
    assert tac("trem x: inteirim = 10 - 3 - 2;") == [
        "    t1 = 10 - 3",
        "    t2 = t1 - 2",
        "    x = t2"]


def test_parenteses_mudam_a_ordem():
    assert tac("trem x: inteirim = (1 + 2) * 3;") == [
        "    t1 = 1 + 2",
        "    t2 = t1 * 3",
        "    x = t2"]


def test_unario():
    assert tac("trem a: inteirim = 4; mostra_so(-a); mostra_so(- -a);") == [
        "    a = 4",
        "    t1 = -a",
        "    print t1",
        "    t2 = -a",
        "    t3 = -t2",
        "    print t3"]


def test_unario_em_constante():
    assert tac("mostra_so(-5 + 1);") == [
        "    t1 = -5",
        "    t2 = t1 + 1",
        "    print t2"]

@pytest.mark.parametrize("op", ["+", "-", "*", "/"])
def test_todos_os_aritmeticos(op):
    assert tac(f"mostra_so(8 {op} 2);") == [f"    t1 = 8 {op} 2", "    print t1"]

@pytest.mark.parametrize("op", ["<", ">", "<=", ">=", "==", "!="])
def test_todos_os_relacionais(op):
    assert tac(f"trem b: booleanim = 1 {op} 2;") == [f"    t1 = 1 {op} 2", "    b = t1"]


def test_igualdade_entre_bool():
    assert tac("trem b: booleanim = eh_memo == num_eh;") == [
        "    t1 = eh_memo == num_eh",
        "    b = t1"]


def test_expressao_aninhada_dos_dois_lados():
    assert tac("mostra_so((1 + 2) * (3 - 4));") == [
        "    t1 = 1 + 2",
        "    t2 = 3 - 4",
        "    t3 = t1 * t2",
        "    print t3"]


def test_constantes_sao_valores_python():
    cod = gerar_tac(_validada("trem b: booleanim = eh_memo; mostra_so(3);"))
    assert cod[0].a1 is True
    assert cod[1].a1 == 3 and type(cod[1].a1) is int

# comandos simples


def test_decl_atrib_e_print():
    assert tac("trem x: inteirim = 1; x = x + 1; mostra_so(x);") == [
        "    x = 1",
        "    t1 = x + 1",
        "    x = t1",
        "    print x"]


def test_programa_vazio_gera_codigo_vazio():
    assert tac("") == []
    assert tac("// só comentário\n") == []


def test_bloco_solto_nao_gera_instrucao_propria():
    assert tac("{ trem a: inteirim = 1; mostra_so(a); }") == ["    a = 1", "    print a"]


def test_while_completo():
    assert tac("trem i: inteirim = 0; enquanto_tiver (i < 3) { i = i + 1; }") == [
        "    i = 0",
        "L1:",
        "    t1 = i < 3",
        "    ifFalse t1 goto L2",
        "    t2 = i + 1",
        "    i = t2",
        "    goto L1",
        "L2:"]


def test_if_else():
    assert tac("trem a: inteirim = 1; uai (a > 0) { mostra_so(1); } sinao { mostra_so(2); }") == [
        "    a = 1",
        "    t1 = a > 0",
        "    ifFalse t1 goto L1",
        "    print 1",
        "    goto L2",
        "L1:",
        "    print 2",
        "L2:"]


def test_if_sem_else_usa_o_mesmo_esquema():

    assert tac("trem a: inteirim = 1; uai (a > 0) { mostra_so(a); } mostra_so(0);") == [
        "    a = 1",
        "    t1 = a > 0",
        "    ifFalse t1 goto L1",
        "    print a",
        "    goto L2",
        "L1:",
        "L2:",
        "    print 0"]


def test_condicao_constante_ou_variavel_nao_gera_temporario():
    assert tac("trem b: booleanim = eh_memo; uai (b) { mostra_so(1); } enquanto_tiver (num_eh) { }") == [
        "    b = eh_memo",
        "    ifFalse b goto L1",
        "    print 1",
        "    goto L2",
        "L1:",
        "L2:",
        "L3:",
        "    ifFalse num_eh goto L4",
        "    goto L3",
        "L4:"]


def test_while_aninhados_tem_rotulos_diferentes():
    cod = tac("""
        trem i: inteirim = 0;
        enquanto_tiver (i < 2) {
            trem j: inteirim = 0;
            enquanto_tiver (j < 2) { j = j + 1; }
            i = i + 1;
        }""")
    assert cod == [
        "    i = 0",
        "L1:",
        "    t1 = i < 2",
        "    ifFalse t1 goto L2",
        "    j = 0",
        "L3:",
        "    t2 = j < 2",
        "    ifFalse t2 goto L4",
        "    t3 = j + 1",
        "    j = t3",
        "    goto L3",
        "L4:",
        "    t4 = i + 1",
        "    i = t4",
        "    goto L1",
        "L2:"]


def test_fatorial_e_a_saida_real_do_slide_3():
    assert tac_de(RAIZ / "exemplos" / "fatorial.mini") == [
        "    n = 5",
        "    f = 1",
        "L1:",
        "    t1 = n > 0",
        "    ifFalse t1 goto L2",
        "    t2 = f * n",
        "    f = t2",
        "    t3 = n - 1",
        "    n = t3",
        "    goto L1",
        "L2:",
        "    print f"]


def test_instrucoes_guardam_a_linha_do_fonte():
    cod = gerar_tac(_validada(
        "trem n: inteirim = 5;\nenquanto_tiver (n > 0) {\n    n = n - 1;\n}\nmostra_so(n / 0);"))
    linhas = [(str(i).strip(), i.linha) for i in cod]
    assert linhas == [
        ("n = 5", 1), ("L1:", 2), ("t1 = n > 0", 2), ("ifFalse t1 goto L2", 2),
        ("t2 = n - 1", 3), ("n = t2", 3), ("goto L1", 2), ("L2:", 2),
        ("t3 = n / 0", 5), ("print t3", 5)]

# temporários e rótulos nunca se repetem


def _validada(fonte):
    arv = parse(fonte)
    assert AnalisadorSemantico().visitar(arv) == []
    return arv


def _checar_unicidade(codigo):
    temps = [i.dest for i in codigo if i.op not in ("=", "label", "goto",
                                                    "iffalse", "print")]
    assert all(re.fullmatch(r"t\d+", t) for t in temps)
    assert len(temps) == len(set(temps))            # cada temp definido uma vez
    rotulos = [i.dest for i in codigo if i.op == "label"]
    assert len(rotulos) == len(set(rotulos))        # cada rótulo marcado uma vez
    for i in codigo:                                # todo salto tem destino
        if i.op in ("goto", "iffalse"):
            assert i.dest in rotulos

@pytest.mark.parametrize("arq", VALIDOS, ids=lambda p: p.name)
def test_todo_caso_valido_gera_tac(arq):
    cod = gerar_tac(_validada(arq.read_text(encoding="utf-8")))
    _checar_unicidade(cod)
    for i in cod:
        assert str(i)                               # todo op é imprimível


def test_contadores_continuam_entre_comandos():
    fonte = """
        trem a: inteirim = 1 + 2;
        uai (a > 0) { a = a * 2; }
        enquanto_tiver (a < 10) { uai (a == 4) { a = a + 1; } sinao { a = a + 2; } }
        mostra_so(a - 1);"""
    texto = "\n".join(tac(fonte))
    assert re.findall(r"t\d+ =", texto) == [f"t{k} =" for k in range(1, 9)]
    # if: L1/L2; while: L3/L4; if interno: L5/L6 (L4 fecha o while no fim)
    assert re.findall(r"^L\d+:", texto, re.M) == ["L1:", "L2:", "L3:", "L5:",
                                                  "L6:", "L4:"]
    _checar_unicidade(gerar_tac(_validada(fonte)))

# nomes internos únicos (docs/arquitetura.md, cuidado 4)


def test_sombreamento_ganha_nome_interno_proprio():
    assert tac_de(RAIZ / "exemplos" / "escopos.mini") == [
        "    x = 1",
        "    y = 2",
        "    x.2 = eh_memo",
        "    print x.2",
        "    print y",
        "    print x"]


def test_inicializador_usa_o_x_externo():
    assert tac("trem x: inteirim = 1; { trem x: inteirim = x + 1; mostra_so(x); } mostra_so(x);") == [
        "    x = 1",
        "    t1 = x + 1",
        "    x.2 = t1",
        "    print x.2",
        "    print x"]


def test_atribuicao_no_bloco_interno_vai_para_o_x_certo():
    assert tac("trem x: inteirim = 1; { trem x: inteirim = 2; x = 3; } x = 4;") == [
        "    x = 1",
        "    x.2 = 2",
        "    x.2 = 3",
        "    x = 4"]


def test_blocos_irmaos_tem_nomes_distintos():
    cod = tac("{ trem a: inteirim = 1; } { trem a: inteirim = 2; mostra_so(a); }")
    assert cod == ["    a = 1", "    a.2 = 2", "    print a.2"]


def test_declaracao_no_corpo_do_while_tem_um_nome_so():
    # O corpo é gerado uma vez; a cada volta a declaração reinicializa j.
    cod = tac("trem i: inteirim = 0; enquanto_tiver (i < 2) { trem j: inteirim = i; i = j + 1; }")
    assert "    j = i" in cod and not any("j." in c for c in cod)


def test_variavel_com_nome_de_temporario_nao_colide():
    cod = tac("trem t1: inteirim = 5; trem x: inteirim = t1 + 1; mostra_so(x * t1);")
    assert cod == [
        "    t1.1 = 5",
        "    t1 = t1.1 + 1",
        "    x = t1",
        "    t2 = x * t1.1",
        "    print t2"]
    _checar_unicidade(gerar_tac(_validada(
        "trem t1: inteirim = 5; trem x: inteirim = t1 + 1; mostra_so(x * t1);")))


def test_variavel_com_nome_de_rotulo_e_permitida():
    # Rótulos só aparecem como destino de label/goto/iffalse, nunca como
    # operando: a variável L1 e o rótulo L1 vivem em espaços separados.
    assert tac("trem L1: inteirim = 0; enquanto_tiver (L1 < 1) { L1 = L1 + 1; }") == [
        "    L1 = 0",
        "L1:",
        "    t1 = L1 < 1",
        "    ifFalse t1 goto L2",
        "    t2 = L1 + 1",
        "    L1 = t2",
        "    goto L1",
        "L2:"]


def test_nomes_parecidos_com_temporario_mantem_o_nome():
    assert tac("trem t: inteirim = 1; trem t1x: inteirim = t; trem tt1: inteirim = t1x;") == [
        "    t = 1", "    t1x = t", "    tt1 = t1x"]

# CLI --tac


def rodar(*args):
    return subprocess.run([sys.executable, "-m", "miniforge", *args],
                          cwd=RAIZ, capture_output=True, text=True,
                          encoding="utf-8")


def test_cli_tac_imprime_o_fatorial_do_slide():
    r = rodar("exemplos/fatorial.mini", "--tac")
    assert r.returncode == 0
    assert r.stdout.splitlines() == tac_de(RAIZ / "exemplos" / "fatorial.mini")
    assert r.stderr == ""


def test_cli_tac_com_erro_semantico_nao_gera_codigo():
    r = rodar("exemplos/semantico.mini", "--tac")
    assert r.returncode == 1
    assert r.stdout == ""
    assert "erro semântico" in r.stderr


def test_cli_tac_com_erro_sintatico_ou_lexico():
    assert rodar("exemplos/erro_sintatico.mini", "--tac").returncode == 1
    assert rodar("exemplos/erro_lexico.mini", "--tac").returncode == 1


def test_cli_tac_mantem_avisos_em_stderr():
    r = rodar("tests/casos/validos/derivacao.mini", "--tac")
    assert r.returncode == 0
    assert "aviso" in r.stderr and "aviso" not in r.stdout
    assert r.stdout.strip()


def test_cli_tac_de_programa_vazio_nao_imprime_nada():
    r = rodar("tests/casos/validos/vazio.mini", "--tac")
    assert (r.returncode, r.stdout) == (0, "")


def test_cli_tokens_e_tac_juntos():
    r = rodar("exemplos/fatorial.mini", "--tokens", "--tac")
    assert r.returncode == 0
    assert "EOF" in r.stdout and r.stdout.rstrip().endswith("    print f")


def test_cli_verificar_mantem_a_mensagem_do_frontend():

    r = rodar("exemplos/fatorial.mini", "--verificar")
    assert r.returncode == 0
    assert "tudo certim, sem erros léxicos, sintáticos ou semânticos" in r.stdout


def test_cli_help_menciona_tac():
    assert "--tac" in rodar("--help").stdout

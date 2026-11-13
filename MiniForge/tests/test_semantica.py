"""Testes do analisador semântico, parte de nomes e escopos"""

import pathlib
import subprocess
import sys

import pytest

from miniforge.ast import Bloco, Num, Print, Programa, Var
from miniforge.parser import parse
from miniforge.semantica import AnalisadorSemantico, Visitor, analisar

RAIZ = pathlib.Path(__file__).parent.parent
VALIDOS = sorted((RAIZ / "tests" / "casos" / "validos").glob("*.mini"))


def sem(fonte):
    """Erros semânticos de um fonte (lista vazia se estiver correto)."""
    return analisar(parse(fonte)).erros


def avisos(fonte):
    return analisar(parse(fonte)).avisos

# Visitor


def test_visitor_despacha_pelo_nome_da_classe():
    class Nomes(Visitor):
        def visitar_Num(self, no):
            return f"num {no.valor}"

        def visitar_Var(self, no):
            return f"trem {no.nome}"

    v = Nomes()
    assert v.visitar(Num(7)) == "num 7"
    assert v.visitar(Var("x")) == "trem x"


def test_analisador_tem_metodo_para_todo_no_da_ast():
    import dataclasses
    import miniforge.ast as ast
    nos = [c for c in vars(ast).values()
           if isinstance(c, type) and dataclasses.is_dataclass(c)
           and issubclass(c, ast.No) and c not in (ast.No, ast.Expr)]
    assert len(nos) == 15
    for classe in nos:
        assert hasattr(AnalisadorSemantico, "visitar_" + classe.__name__), classe


def test_fora_do_escopo():
    erros = sem("{ trem y: inteirim = 1; } mostra_so(y);")
    assert erros == [
        "linha 1: erro semântico: 'y' num foi declarado, sô"]


def test_redeclaracao_no_mesmo_escopo():
    erros = sem("trem x: inteirim = 1;\ntrem x: booleanim = eh_memo;\nmostra_so(x);")
    assert erros == ["linha 2: erro semântico: 'x' já foi declarado neste escopo, uai"]


def test_redeclaracao_dentro_de_bloco():
    erros = sem("{\n  trem a: inteirim = 1;\n  trem a: inteirim = 2;\n  mostra_so(a);\n}")
    assert erros == ["linha 3: erro semântico: 'a' já foi declarado neste escopo, uai"]


def test_uso_de_variavel_nao_declarada():
    assert sem("mostra_so(ausente);") == [
        "linha 1: erro semântico: 'ausente' num foi declarado, sô"]


def test_atribuicao_a_variavel_nao_declarada():
    assert sem("trem a: inteirim = 1;\nb = a;") == [
        "linha 2: erro semântico: 'b' num foi declarado, sô"]


def test_sombreamento_em_escopo_interno_e_permitido():
    assert sem("trem x: inteirim = 1;\n{ trem x: booleanim = eh_memo; mostra_so(x); }\nmostra_so(x);") == []


def test_variavel_externa_visivel_no_bloco_interno():
    assert sem("trem x: inteirim = 1;\n{ { x = x + 1; } }\nmostra_so(x);") == []


def test_nome_de_bloco_pode_ser_declarado_de_novo_depois_dele():
    assert sem("{ trem t: inteirim = 1; mostra_so(t); }\ntrem t: inteirim = 2;\nmostra_so(t);") == []

# inicializador visitado antes de declarar


def test_inicializador_nao_ve_a_propria_variavel():
    assert sem("trem x: inteirim = x + 1;") == [
        "linha 1: erro semântico: 'x' num foi declarado, sô"]


def test_inicializador_usa_o_x_externo():
    fonte = "trem x: inteirim = 1;\n{\n  trem x: inteirim = x + 1;\n  mostra_so(x);\n}"
    a = analisar(parse(fonte))
    assert a.erros == []
    assert a.avisos == []                        # o x externo foi lido


def test_redeclaracao_com_inicializador_invalido_gera_os_dois_erros():
    assert sem("trem x: inteirim = 1;\ntrem x: inteirim = y;\nmostra_so(x);") == [
        "linha 2: erro semântico: 'y' num foi declarado, sô",
        "linha 2: erro semântico: 'x' já foi declarado neste escopo, uai",
    ]

# if / while / expressões


def test_bloco_do_if_e_do_else_sao_escopos_separados():
    fonte = ("trem c: booleanim = eh_memo;\n"
             "uai (c) { trem t: inteirim = 1; mostra_so(t); }\n"
             "sinao { trem t: inteirim = 2; mostra_so(t); }\n"
             "mostra_so(t);")
    assert sem(fonte) == ["linha 4: erro semântico: 't' num foi declarado, sô"]


def test_corpo_do_while_e_escopo_novo_a_cada_analise():
    fonte = ("trem i: inteirim = 0;\n"
             "enquanto_tiver (i < 3) { trem d: inteirim = i * 2; mostra_so(d); i = i + 1; }\n"
             "mostra_so(d);")
    assert sem(fonte) == ["linha 3: erro semântico: 'd' num foi declarado, sô"]


def test_nomes_nas_condicoes_e_operadores_sao_resolvidos():
    fonte = ("uai (a == 1) { }\n"
             "enquanto_tiver (-b < 0) { }\n"
             "mostra_so((c + 1) * d);")
    assert sem(fonte) == [
        "linha 1: erro semântico: 'a' num foi declarado, sô",
        "linha 2: erro semântico: 'b' num foi declarado, sô",
        "linha 3: erro semântico: 'c' num foi declarado, sô",
        "linha 3: erro semântico: 'd' num foi declarado, sô",
    ]


def test_acumula_todos_os_erros_em_ordem_de_ocorrencia():
    fonte = ("mostra_so(a);\n"
             "trem k: inteirim = 1;\n"
             "trem k: inteirim = 2;\n"
             "{ z = k; }")
    assert sem(fonte) == [
        "linha 1: erro semântico: 'a' num foi declarado, sô",
        "linha 3: erro semântico: 'k' já foi declarado neste escopo, uai",
        "linha 4: erro semântico: 'z' num foi declarado, sô",
    ]


def test_tabela_volta_ao_global_depois_da_analise():
    a = analisar(parse("{ trem a: inteirim = 1; { trem b: inteirim = a; mostra_so(b); } }"))
    assert a.erros == []
    assert a.tabela.nivel == 0


def test_analisa_ast_montada_a_mao():
    prog = Programa([Bloco([Print(Var("q", linha=7), linha=7)])])
    assert analisar(prog).erros == ["linha 7: erro semântico: 'q' num foi declarado, sô"]

# banco de casos: todo válido também é semanticamente válido

@pytest.mark.parametrize("arq", VALIDOS, ids=lambda p: p.name)
def test_casos_validos_sem_erros_semanticos(arq):
    assert sem(arq.read_text(encoding="utf-8")) == []

@pytest.mark.parametrize("arq", ["fatorial.mini", "if_else.mini", "escopos.mini"])
def test_exemplos_validos(arq):
    a = analisar(parse((RAIZ / "exemplos" / arq).read_text(encoding="utf-8")))
    assert a.erros == [] and a.avisos == []


def test_exemplo_erro_semantico():
    fonte = (RAIZ / "exemplos" / "erro_semantico.mini").read_text(encoding="utf-8")
    assert sem(fonte) == ["linha 3: erro semântico: 'ausente' num foi declarado, sô"]


def test_aviso_variavel_nunca_usada():
    assert avisos("trem x: inteirim = 1;") == [
        "linha 1: aviso: 'x' declarado e nunca usado, sô"]


def test_aviso_nao_e_erro():
    a = analisar(parse("trem x: inteirim = 1;"))
    assert a.erros == []


def test_atribuir_nao_conta_como_uso():
    assert avisos("trem x: inteirim = 1;\nx = 2;") == [
        "linha 1: aviso: 'x' declarado e nunca usado, sô"]


def test_conta_as_leituras_de_cada_variavel():
    a = analisar(parse("trem x: inteirim = 1;\ntrem y: inteirim = x + x;\nmostra_so(x);"))
    # o escopo global continua na tabela depois da análise
    assert a.tabela.buscar("x").usos == 3
    assert a.tabela.buscar("y").usos == 0
    assert a.avisos == ["linha 2: aviso: 'y' declarado e nunca usado, sô"]


def test_avisos_de_blocos_internos_em_ordem_de_linha():
    fonte = ("trem a: inteirim = 1;\n"
             "{\n"
             "  trem b: inteirim = 2;\n"
             "  { trem c: inteirim = 3; }\n"
             "}\n"
             "trem d: inteirim = a;")
    assert avisos(fonte) == [
        "linha 3: aviso: 'b' declarado e nunca usado, sô",
        "linha 4: aviso: 'c' declarado e nunca usado, sô",
        "linha 6: aviso: 'd' declarado e nunca usado, sô",
    ]


def test_sombreada_sem_uso_gera_aviso_so_para_ela():
    fonte = "trem x: inteirim = 1;\n{ trem x: inteirim = 2; }\nmostra_so(x);"
    assert avisos(fonte) == ["linha 2: aviso: 'x' declarado e nunca usado, sô"]

# CLI (integração)


def cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "miniforge", *args],
        cwd=RAIZ, capture_output=True, text=True, encoding="utf-8")


def test_cli_erro_semantico_sai_com_codigo_1():
    r = cli("exemplos/erro_semantico.mini")
    assert r.returncode == 1
    assert r.stdout == ""
    assert r.stderr == "linha 3: erro semântico: 'ausente' num foi declarado, sô\n"


def test_cli_lista_todos_os_erros(tmp_path):
    arq = tmp_path / "varios.mini"
    arq.write_text("trem x: inteirim = 1;\ntrem x: inteirim = 2;\nmostra_so(x + y);\n", encoding="utf-8")
    r = cli(str(arq))
    assert r.returncode == 1
    assert r.stderr.splitlines() == [
        "linha 2: erro semântico: 'x' já foi declarado neste escopo, uai",
        "linha 3: erro semântico: 'y' num foi declarado, sô",
    ]


def test_cli_aviso_nao_impede_sucesso(tmp_path):
    arq = tmp_path / "aviso.mini"
    arq.write_text("trem x: inteirim = 1;\n", encoding="utf-8")
    r = cli(str(arq), "--verificar")
    assert r.returncode == 0
    assert r.stderr == "linha 1: aviso: 'x' declarado e nunca usado, sô\n"
    assert r.stdout == f"{arq}: tudo certim, sem erros léxicos, sintáticos ou semânticos\n"


def test_cli_erro_sintatico_impede_a_semantica():
    r = cli("exemplos/erro_sintatico.mini")
    assert r.returncode == 1
    assert "erro sintático" in r.stderr and "semântico" not in r.stderr

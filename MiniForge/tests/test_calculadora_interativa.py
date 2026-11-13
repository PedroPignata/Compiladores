"""Testa a experiência interativa e a resposta obtida pelo compilador real."""
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch
import pytest
from exemplos.calculadora.interativa import calcular, main
from miniforge.ir import Instr

RAIZ = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('a,b,op,resultado', [
    (18,6,'1',24), (18,6,'2',12), (18,6,'3',108), (18,6,'4',3),
    (-7,2,'4',-3), (7,-2,'4',-3), (-7,-2,'4',3),
    (0,7,'4',0), (0,0,'1',0), (10**100,1,'1',10**100+1),
])
def test_resultado_do_otimizador(a,b,op,resultado):
    conta = calcular(a,b,op)
    assert conta.resultado == resultado
    assert type(conta.resultado) is int
    assert f'print {resultado}' in conta.tac_otimizado
    assert 'mostra_so' in conta.fonte


@pytest.mark.parametrize('a,b,op', [(1,0,'4'),(1,2,'9'),(True,1,'1'),(1,2.5,'1')])
def test_entrada_invalida(a,b,op):
    with pytest.raises(ValueError):
        calcular(a,b,op)


def test_resultado_realmente_vem_do_pipeline():
    # Um resultado não dobrado precisa falhar, não ser recalculado em Python.
    with patch('exemplos.calculadora.interativa.otimizar', return_value=[Instr('print',None,'t1')]):
        with pytest.raises(ValueError, match='não reduziu'):
            calcular(18,6,'1')


@pytest.mark.parametrize('entrada,esperados', [
    ('1\n18\n6\n0\n', ['Resultado: 18 + 6 = 24']),
    ('2\n8\n10\n3\n-3\n4\n0\n', ['Resultado: 8 - 10 = -2','Resultado: -3 * 4 = -12']),
    ('4\n-7\n2\n0\n', ['Resultado: -7 / 2 = -3']),
    ('4\n10\n0\n1\n2\n3\n0\n', ['dividir por zero','Resultado: 2 + 3 = 5']),
    ('9\n1\nabc\n2.5\n18\n6\n0\n', ['Opção inválida','Entrada inválida','Resultado: 18 + 6 = 24']),
    ('0\n', ['Até mais, sô!']),
    ('', ['Até mais, sô!']),
    ('1\n', ['Até mais, sô!']),
])
def test_sessoes_por_subprocesso(entrada,esperados):
    r = subprocess.run([sys.executable,'-m','exemplos.calculadora.interativa'],
                       cwd=RAIZ,input=entrada,capture_output=True,text=True,timeout=10)
    assert r.returncode == 0, r.stderr
    assert not r.stderr
    assert all(t in r.stdout for t in esperados)


def test_detalhes():
    r = subprocess.run([sys.executable,'-m','exemplos.calculadora.interativa','--detalhes'],
                       cwd=RAIZ,input='1\n18\n6\n0\n',capture_output=True,text=True,timeout=10)
    assert r.returncode == 0, r.stderr
    assert all(t in r.stdout for t in ['Fonte mineirês:', 'TAC original:', 'TAC otimizado:', 'print 24', 'Resultado: 18 + 6 = 24'])


def test_ctrl_c(capsys):
    with patch('builtins.input',side_effect=KeyboardInterrupt):
        assert main([]) == 0
    assert 'Até mais, sô!' in capsys.readouterr().out

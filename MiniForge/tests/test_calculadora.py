"""Demonstração da calculadora por compilação, sem executar o TAC."""
from copy import deepcopy
from pathlib import Path
import subprocess
import sys
import pytest
from miniforge.lexer import Lexer
from miniforge.parser import Parser
from miniforge.ir import gerar_tac, formatar_tac
from miniforge.otimizador import otimizar

PASTA = Path(__file__).resolve().parents[1] / 'exemplos' / 'calculadora'


def compilar(fonte):
    lexer = Lexer(fonte)
    tokens = lexer.tokens()
    assert not lexer.erros
    return gerar_tac(Parser(tokens).programa())


@pytest.mark.parametrize('nome', ['calculadora', 'constantes'])
def test_referencias_e_invariantes(nome):
    original = compilar((PASTA / f'{nome}.mini').read_text(encoding='utf-8'))
    copia = deepcopy(original)
    novo = otimizar(original)
    assert original == copia
    assert otimizar(novo) == novo
    for sufixo, codigo in [('original', original), ('otimizado', novo)]:
        assert formatar_tac(codigo) + '\n' == (PASTA / f'{nome}-{sufixo}.tac').read_text()
        rotulos = [i.dest for i in codigo if i.op == 'label']
        assert len(rotulos) == len(set(rotulos))
        assert all(i.dest in rotulos for i in codigo if i.op in ('goto', 'iffalse'))


@pytest.mark.parametrize('operacao,a,b,esperado', [
    (1,18,6,24), (2,18,6,12), (3,18,6,108), (4,18,6,3),
    (4,-7,2,-3), (4,7,-2,-3), (1,0,0,0),
    (4,18,0,None), (0,18,6,None), (9,18,6,None),
])
def test_cenarios_compilados(operacao,a,b,esperado):
    fonte = (PASTA / 'calculadora.mini').read_text(encoding='utf-8')
    fonte = fonte.replace('primeiro: inteirim = 18;', f'primeiro: inteirim = {a};')
    fonte = fonte.replace('segundo: inteirim = 6;', f'segundo: inteirim = {b};')
    fonte = fonte.replace('operacao: inteirim = 1;', f'operacao: inteirim = {operacao};')
    codigo = otimizar(compilar(fonte))
    impressos = [i.a1 for i in codigo if i.op == 'print']
    # Expectativas manuais, sem implementar avaliador do programa nos testes.
    assert impressos == ([False] if esperado is None else [True, esperado])
    assert type(impressos[0]) is bool
    if esperado is not None:
        assert type(impressos[1]) is int
    assert not any(i.op == '/' and i.a2 == 0 for i in codigo)


def test_contas_precedencia_e_divisao():
    codigo = otimizar(compilar((PASTA / 'constantes.mini').read_text()))
    assert [i.a1 for i in codigo if i.op == 'print'] == [24,12,108,3,-3,14,20]


@pytest.mark.parametrize('opcoes', [['--verificar'], ['--tokens'], ['--ast'], ['--tipos'], ['--tac'], ['--tac','-O']])
def test_cli_calculadora(opcoes):
    r = subprocess.run([sys.executable, '-m', 'miniforge', str(PASTA/'calculadora.mini'), *opcoes],
                       cwd=PASTA.parents[1], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert not r.stderr
    assert r.stdout.strip()
    if opcoes == ['--tac','-O']:
        assert r.stdout == (PASTA/'calculadora-otimizado.tac').read_text()

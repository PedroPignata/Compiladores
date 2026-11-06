"""Contrato da entrega parcial, independente de etapas futuras."""
import ast
import itertools
from pathlib import Path
import subprocess
import sys

import pytest

from miniforge import ast as A
from miniforge.parser import parse
from miniforge.semantica import analisar

RAIZ = Path(__file__).resolve().parent.parent


def cli(*args):
    return subprocess.run([sys.executable, '-m', 'miniforge', *map(str, args)],
                          cwd=RAIZ, capture_output=True, text=True, timeout=5)


def test_padrao_apenas_valida():
    r = cli('exemplos/fatorial.mini')
    assert r.returncode == 0 and not r.stderr
    assert r.stdout == ('exemplos/fatorial.mini: tudo certim, sem erros '
                        'léxicos, sintáticos ou semânticos\n')


@pytest.mark.parametrize('fonte', [
    'enquanto_tiver (eh_memo) { mostra_so(999); }',
    'mostra_so(1 / 0);',
])
def test_nao_executa_nem_avalia_expressoes(tmp_path, fonte):
    p = tmp_path / 'sem_execucao.mini'
    p.write_text(fonte, encoding='utf-8')
    r = cli(p)
    assert r.returncode == 0 and not r.stderr
    assert r.stdout == f'{p}: tudo certim, sem erros léxicos, sintáticos ou semânticos\n'


@pytest.mark.parametrize('opcao', ['--tac', '--pilha', '--vm-pilha', '--stats', '-O'])
def test_opcoes_futuras_rejeitadas(opcao):
    r = cli('exemplos/fatorial.mini', opcao)
    assert r.returncode == 2 and not r.stdout
    assert 'unrecognized arguments' in r.stderr


@pytest.mark.parametrize('args', [[], ['--inexistente']])
def test_argumentos_invalidos(args):
    r = cli(*args)
    assert r.returncode == 2 and not r.stdout


def test_leitura_invalida(tmp_path):
    p = tmp_path / 'invalido.mini'
    for existe in [False, True]:
        if existe:
            p.write_bytes(b'\xff')
        r = cli(p)
        assert r.returncode == 1 and not r.stdout and 'erro ao ler' in r.stderr


# Todas as 32 combinações dos cinco sinalizadores públicos.
@pytest.mark.parametrize('flags', [
    [flag for flag, usar in zip(['--tokens', '--ast', '--tipos', '--contexto', '--verificar'], bits) if usar]
    for bits in itertools.product([False, True], repeat=5)
])
def test_combinacoes_documentadas(flags):
    r = cli('exemplos/fatorial.mini', *flags)
    assert r.returncode == 0 and not r.stderr
    tokens = '--tokens' in flags
    arvore = '--ast' in flags
    tipos = '--tipos' in flags
    verificar = '--verificar' in flags
    assert ("VAR          'trem'" in r.stdout) == tokens
    assert r.stdout.count('Programa') == int(arvore) + int(tipos)
    assert ('Num 5 : inteirim' in r.stdout) == tipos
    sucesso = verificar or (not tokens and not arvore and not tipos)
    assert ('tudo certim' in r.stdout) == sucesso


@pytest.mark.parametrize('flags', [['--ast', '--tipos'], ['--ast', '--verificar'], ['--tokens', '--tipos']])
def test_opcao_semantica_nao_e_ignorada(flags):
    r = cli('exemplos/semantico.mini', *flags)
    assert r.returncode == 1
    assert r.stderr.count('erro semântico') == 3
    assert 'tudo certim' not in r.stdout


def test_independencia_estatica_e_dinamica():
    proibidos = {'ir', 'vm', 'otimizador'}
    for arquivo in (RAIZ / 'miniforge').glob('*.py'):
        assert arquivo.stem not in proibidos
    for pasta in ['miniforge', 'tests']:
        for arquivo in (RAIZ / pasta).rglob('*.py'):
            for no in ast.walk(ast.parse(arquivo.read_text())):
                if isinstance(no, ast.ImportFrom):
                    assert not (set((no.module or '').split('.')) & proibidos), arquivo
    script = ('import sys; from miniforge.__main__ import main; '
              'main(["exemplos/fatorial.mini"]); '
              'assert not any(n in sys.modules for n in '
              '["miniforge.ir", "miniforge.vm", "miniforge.otimizador"])')
    r = subprocess.run([sys.executable, '-c', script], cwd=RAIZ, capture_output=True)
    assert r.returncode == 0, r.stderr


@pytest.mark.parametrize('op,esq,dir', itertools.product(
    ['+', '-', '*', '/', '<', '>', '<=', '>=', '==', '!='], ['1', 'eh_memo'], ['1', 'eh_memo']
))
def test_tabela_completa_sem_coercao_python(op, esq, dir):
    # 10 operadores x 4 pares, incluindo bool/int em ambas as ordens.
    prog = parse(f'mostra_so({esq} {op} {dir});')
    a = analisar(prog)
    mesmo_tipo = esq == dir
    permitido = mesmo_tipo if op in ['==', '!='] else esq == dir == '1'
    assert (not a.erros) == permitido
    if permitido:
        assert prog.comandos[0].expr.tipo == ('int' if op in '+-*/' else 'bool')

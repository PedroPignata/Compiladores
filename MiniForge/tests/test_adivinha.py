"""Sessões reais do jogo mineirês, incluindo otimização e configurações."""
from copy import deepcopy
from io import StringIO
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

import pytest
from miniforge.execucao import executar
from miniforge.ir import gerar_tac
from miniforge.lexer import Lexer
from miniforge.otimizador import otimizar
from miniforge.parser import Parser

RAIZ = Path(__file__).resolve().parents[1]
ARQUIVO = RAIZ / 'exemplos/adivinha/adivinha.mini'


def compilar(fonte):
    lexer = Lexer(fonte)
    tokens = lexer.tokens()
    assert not lexer.erros
    return gerar_tac(Parser(tokens).programa())


@pytest.mark.parametrize('otimizado', [False, True])
@pytest.mark.parametrize('entrada,trechos', [
    ('65\n', ['Acertou, trem bão!', 'Quantidade de tentativas:\n1\n']),
    ('40\n80\n65\n', ['Tenta um maior.', 'Tenta um menor.', 'Quantidade de tentativas:\n3\n']),
    ('-2\n101\n65\n', ['fora do intervalo', 'Quantidade de tentativas:\n1\n']),
    ('abc\n2.5\n65\n', ['Acertou, trem bão!', 'Quantidade de tentativas:\n1\n']),
    ('0\n', ['o segredo fica pra próxima prosa!']),
    ('1\n100\n65\n', ['Tenta um maior.', 'Tenta um menor.', 'Quantidade de tentativas:\n3\n']),
])
def test_sessoes(otimizado, entrada, trechos):
    cod = compilar(ARQUIVO.read_text())
    if otimizado:
        cod = otimizar(cod)
    saida = StringIO(); erros = StringIO()
    with patch('miniforge.execucao._sorteador.randint', return_value=65) as sorteio:
        executar(cod, StringIO(entrada), saida, erros)
    texto = saida.getvalue()
    assert all(t in texto for t in trechos)
    assert texto.endswith('Até mais, sô!\n')
    sorteio.assert_called_once_with(1, 100)
    if 'abc' in entrada:
        assert erros.getvalue().count('Entrada inválida') == 2
    else:
        assert not erros.getvalue()
    if entrada == '0\n':
        assert 'Acertou' not in texto and 'Quantidade de tentativas:' not in texto


@pytest.mark.parametrize('segredo', [1, 100, 42])
def test_personalizar_segredo(segredo):
    fonte = ARQUIVO.read_text()
    original = compilar(fonte)
    copia = deepcopy(original)
    sem = StringIO(); com = StringIO()
    with patch('miniforge.execucao._sorteador.randint', return_value=segredo):
        executar(original, StringIO(f'{segredo}\n'), sem)
    novo = otimizar(original)
    with patch('miniforge.execucao._sorteador.randint', return_value=segredo):
        executar(novo, StringIO(f'{segredo}\n'), com)
    assert original == copia
    assert sem.getvalue() == com.getvalue()
    assert 'Quantidade de tentativas:\n1\n' in com.getvalue()
    assert otimizar(novo) == novo
    rotulos = [i.dest for i in novo if i.op == 'label']
    assert len(rotulos) == len(set(rotulos))
    assert all(i.dest in rotulos for i in novo if i.op in ('goto', 'iffalse'))


@pytest.mark.parametrize('de,para', [
    ('minimo: inteirim = 1;', 'minimo: inteirim = 0;'),
    ('minimo: inteirim = 1;', 'minimo: inteirim = 101;'),
])
def test_configuracao_invalida_nao_le_entrada(de, para):
    fonte = ARQUIVO.read_text().replace(de, para)
    saida = StringIO()
    with patch('miniforge.execucao._sorteador.randint') as sorteio:
        executar(otimizar(compilar(fonte)), StringIO(''), saida)
    sorteio.assert_not_called()
    assert 'confira os limites' in saida.getvalue()
    assert 'Qual é seu palpite' not in saida.getvalue()


@pytest.mark.parametrize('opcoes', [['--tokens'], ['--ast'], ['--tipos'], ['--verificar'], ['--tac'], ['--tac', '-O']])
def test_inspecao_sem_teclado(opcoes):
    r = subprocess.run([sys.executable, '-m', 'miniforge', str(ARQUIVO), *opcoes],
                       cwd=RAIZ, input='', capture_output=True, text=True, timeout=10)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() and not r.stderr


def test_eof_durante_palpite():
    r = subprocess.run([sys.executable, '-m', 'miniforge', str(ARQUIVO), '--executar'],
                       cwd=RAIZ, input='', capture_output=True, text=True, timeout=10)
    assert r.returncode == 1 and 'fim da entrada' in r.stderr


@pytest.mark.parametrize('otimizado', [False, True])
def test_cli_sorteio_real_intervalo_unitario(tmp_path, otimizado):
    fonte = ARQUIVO.read_text().replace('minimo: inteirim = 1;', 'minimo: inteirim = 42;')
    fonte = fonte.replace('maximo: inteirim = 100;', 'maximo: inteirim = 42;')
    caminho = tmp_path / 'jogo.mini'
    caminho.write_text(fonte, encoding='utf-8')
    args = [sys.executable, '-m', 'miniforge', str(caminho), '--executar']
    if otimizado:
        args.append('-O')
    r = subprocess.run(args, cwd=RAIZ, input='42\n', capture_output=True, text=True, timeout=10)
    assert r.returncode == 0, r.stderr
    assert 'Quantidade de tentativas:\n1\n' in r.stdout

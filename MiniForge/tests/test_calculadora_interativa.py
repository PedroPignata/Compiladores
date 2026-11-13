"""A calculadora é fonte mineirês executado pelo MiniForge, não aplicativo Python."""
from pathlib import Path
import subprocess
import sys
import pytest
from miniforge.lexer import Lexer
from miniforge.parser import Parser, ErroSintatico
from miniforge.semantica import analisar
from miniforge.ir import gerar_tac
from miniforge.otimizador import otimizar
from miniforge.execucao import executar, ErroExecucao
from io import StringIO

RAIZ = Path(__file__).resolve().parents[1]
ARQUIVO = RAIZ/'exemplos/calculadora/interativa.mini'


def codigo(fonte):
    l = Lexer(fonte)
    tokens = l.tokens()
    assert not l.erros
    return gerar_tac(Parser(tokens).programa())


@pytest.mark.parametrize('otimizado', [False,True])
@pytest.mark.parametrize('entrada,esperado', [
    ('1\n18\n6\n0\n','Resultado:\n24'),
    ('2\n8\n10\n0\n','Resultado:\n-2'),
    ('3\n-3\n4\n0\n','Resultado:\n-12'),
    ('4\n-7\n2\n0\n','Resultado:\n-3'),
    ('4\n7\n-2\n0\n','Resultado:\n-3'),
    ('4\n10\n0\n0\n','Nao e possivel dividir por zero.'),
    ('9\n0\n','Opcao invalida.'),
    ('-1\n0\n','Opcao invalida.'),
    ('1\nabc\n18\n6\n0\n','Resultado:\n24'),
    ('0\n','Ate mais, so!'),
])
def test_calculadora_mineires(entrada,esperado,otimizado):
    args=[sys.executable,'-m','miniforge',str(ARQUIVO),'--executar']
    if otimizado: args.append('-O')
    r=subprocess.run(args,cwd=RAIZ,input=entrada,capture_output=True,text=True,timeout=10)
    assert r.returncode==0,r.stderr
    assert esperado in r.stdout
    assert r.stdout.endswith('Ate mais, so!\n')


@pytest.mark.parametrize('otimizado',[False,True])
def test_repeticao_nao_congela_entrada(otimizado):
    cod=codigo(ARQUIVO.read_text())
    original=list(cod)
    if otimizado: cod=otimizar(cod)
    saida=StringIO()
    executar(cod,StringIO('1\n2\n3\n4\n10\n0\n3\n4\n5\n0\n'),saida)
    assert 'Resultado:\n5\n' in saida.getvalue()
    assert 'Resultado:\n20\n' in saida.getvalue()
    assert 'Nao e possivel dividir por zero.' in saida.getvalue()
    assert original==codigo(ARQUIVO.read_text())


def test_leitura_invalida_constantes_e_preserva_texto():
    cod=codigo('trem x: inteirim = 5; le_so(x); mostra_so("x"); mostra_so(x);')
    saida=StringIO(); erros=StringIO()
    executar(otimizar(cod),StringIO('2.5\n7\n'),saida,erros)
    assert saida.getvalue()=='x\n7\n'
    assert 'Entrada inválida' in erros.getvalue()


@pytest.mark.parametrize('fonte', ['le_so(x);','trem x: booleanim = eh_memo; le_so(x);'])
def test_semantica_leitura(fonte):
    assert analisar(Parser(Lexer(fonte).tokens()).programa()).erros


@pytest.mark.parametrize('fonte',['le_so(1);','mostra_so("a" + 1);','trem x: inteirim = "a";'])
def test_sintaxe_extensao_restrita(fonte):
    with pytest.raises(ErroSintatico):
        Parser(Lexer(fonte).tokens()).programa()


def test_lexer_texto_e_posicao():
    l=Lexer('mostra_so("olá // x");\nle_so(x);')
    tokens=l.tokens()
    assert not l.erros
    t=next(t for t in tokens if t.tipo.name=='TEXTO')
    assert (t.linha,t.coluna,t.lexema)==(1,11,'"olá // x"')
    l=Lexer('mostra_so("aberto\nle_so(x);');l.tokens()
    assert 'texto não fechado' in l.erros[0]


@pytest.mark.parametrize('fonte,entrada,erro',[
    ('mostra_so(1 / 0);','','divisão por zero'),
    ('trem x: inteirim = 0; le_so(x);','','fim da entrada'),
])
def test_erros_execucao(fonte,entrada,erro):
    with pytest.raises(ErroExecucao,match=erro):
        executar(otimizar(codigo(fonte)),StringIO(entrada),StringIO())


@pytest.mark.parametrize('opcoes',[['--ast'],['--tokens'],['--tipos'],['--tac'],['--verificar']])
def test_cli_rejeita_execucao_com_inspecao(opcoes):
    r=subprocess.run([sys.executable,'-m','miniforge',str(ARQUIVO),'--executar',*opcoes],
                     cwd=RAIZ,capture_output=True,text=True,timeout=10)
    assert r.returncode==2


def test_cli_fim_entrada_codigo_um():
    r=subprocess.run([sys.executable,'-m','miniforge',str(ARQUIVO),'--executar'],
                     cwd=RAIZ,input='',capture_output=True,text=True,timeout=10)
    assert r.returncode==1 and 'fim da entrada' in r.stderr


def test_leitura_sem_uso_nao_pode_ser_eliminada():
    cod=otimizar(codigo('trem x: inteirim = 0; le_so(x);'))
    assert any(i.op=='read' for i in cod)

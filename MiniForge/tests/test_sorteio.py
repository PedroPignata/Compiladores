"""Sorteio em execução, com tipos, ordem de avaliação e efeitos preservados."""
from copy import deepcopy
from io import StringIO
from unittest.mock import patch
import pytest
from miniforge.lexer import Lexer
from miniforge.parser import Parser, ErroSintatico
from miniforge.ast import formatar_ast
from miniforge.semantica import analisar
from miniforge.ir import gerar_tac, formatar_tac
from miniforge.execucao import executar, ErroExecucao
from miniforge.otimizador import otimizar


def arvore(fonte):
    l = Lexer(fonte); t = l.tokens()
    assert not l.erros
    return Parser(t).programa()


def test_tokens_posicao_e_identificador_completo():
    l = Lexer('sorteia_so(1, 10) sorteia_so2')
    t = l.tokens()
    assert [i.tipo.name for i in t] == ['SORTEIO','ABRE_PAR','NUM','VIRGULA','NUM','FECHA_PAR','ID','EOF']
    assert (t[3].linha,t[3].coluna)==(1,13)


def test_ast_tipo_e_tac():
    a=arvore('mostra_so(sorteia_so(1 + 2, 10));')
    assert not analisar(a).erros
    assert 'Sorteio : inteirim' in formatar_ast(a)
    assert 'sorteia t1, 10' in formatar_tac(gerar_tac(a))


@pytest.mark.parametrize('expr', ['sorteia_so(eh_memo, 10)','sorteia_so(1, num_eh)','sorteia_so(1, 2) == eh_memo'])
def test_rejeita_tipos_invalidos(expr):
    assert analisar(arvore(f'mostra_so({expr});')).erros


def test_erros_independentes_sem_cascata():
    a=analisar(arvore('trem b: booleanim = sorteia_so(x, y);'))
    assert len(a.erros)==2


@pytest.mark.parametrize('expr', ['sorteia_so(1)','sorteia_so(1 2)','sorteia_so(1,2,3)'])
def test_aridade_e_separador(expr):
    with pytest.raises(ErroSintatico):
        arvore(f'mostra_so({expr});')


@pytest.mark.parametrize('otimizado',[False,True])
@pytest.mark.parametrize('minimo,maximo',[(-9,4),(1,1),(1,100),(-10**30,10**30)])
def test_sorteio_real_respeita_intervalo(minimo,maximo,otimizado):
    c=gerar_tac(arvore(f'mostra_so(sorteia_so({minimo}, {maximo}));'))
    if otimizado:c=otimizar(c)
    # Não se exige que resultados aleatórios sejam diferentes para o teste passar.
    for _ in range(20):
        s=StringIO();executar(c,StringIO(''),s)
        assert minimo<=int(s.getvalue())<=maximo


@pytest.mark.parametrize('otimizado',[False,True])
def test_falha_intervalo_preservada_mesmo_sem_uso(otimizado):
    c=gerar_tac(arvore('trem x: inteirim = sorteia_so(5, 1);'))
    if otimizado:c=otimizar(c)
    with pytest.raises(ErroExecucao,match='linha 1: intervalo inválido'):
        executar(c,StringIO(''),StringIO())


def test_otimizador_nao_sorteia_nao_muta_e_preserva_chamadas():
    c=gerar_tac(arvore('mostra_so(sorteia_so(1,10) + sorteia_so(1,10));'))
    copia=deepcopy(c)
    with patch('miniforge.execucao._sorteador.randint', side_effect=[2,7]) as sortear:
        novo=otimizar(c)
        assert not sortear.called
        s=StringIO();executar(novo,StringIO(''),s)
        assert sortear.call_count==2
    assert s.getvalue()=='9\n'
    assert c==copia and otimizar(novo)==novo
    assert sum(i.op=='random' for i in novo)==2


def test_ordem_avaliacao_limites():
    c=gerar_tac(arvore('mostra_so(sorteia_so(sorteia_so(1,2), sorteia_so(8,9)));'))
    with patch('miniforge.execucao._sorteador.randint',side_effect=[2,8,5]) as sorteio:
        s=StringIO();executar(otimizar(c),StringIO(''),s)
    assert sorteio.call_args_list==[((1,2),),((8,9),),((2,8),)]
    assert s.getvalue()=='5\n'


def test_loop_sorteia_em_cada_iteracao():
    c=gerar_tac(arvore('trem n: inteirim = 0; enquanto_tiver (n < 2) { mostra_so(sorteia_so(1, 10)); n = n + 1; }'))
    with patch('miniforge.execucao._sorteador.randint',side_effect=[3,9]) as sorteio:
        s=StringIO();executar(otimizar(c),StringIO(''),s)
        assert sorteio.call_count==2
    assert s.getvalue()=='3\n9\n'


def test_nova_execucao_sorteia_novamente_sem_recompilar():
    c=otimizar(gerar_tac(arvore('mostra_so(sorteia_so(1, 100));')))
    with patch('miniforge.execucao._sorteador.randint',side_effect=[17,83]) as sorteio:
        a=StringIO();b=StringIO()
        executar(c,StringIO(''),a)
        executar(c,StringIO(''),b)
        assert sorteio.call_count==2
    assert a.getvalue()=='17\n' and b.getvalue()=='83\n'


def test_sorteio_temporario_sem_uso_continua_observavel():
    from miniforge.ir import Instr
    c=[Instr('random','t1',1,10,linha=3)]
    assert otimizar(c)==c

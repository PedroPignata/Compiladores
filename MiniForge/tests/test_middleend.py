"""Evidências estruturais independentes, sem executor ou VM."""
from copy import deepcopy
from itertools import product
import subprocess
import sys
from pathlib import Path
import pytest
from miniforge.ir import gerar_tac, Instr
from miniforge.parser import parse
from miniforge.otimizador import otimizar, PASSES, dobrar_constantes
from miniforge.constantes import avaliar, dividir

def tac(s): return gerar_tac(parse(s))

@pytest.mark.parametrize('a,b', product([-10**100, -7, 0, 7, 10**100],[-3,2,10**30]))
def test_divisao_exata(a,b):
    q=dividir(a,b)
    assert abs(q)==abs(a)//abs(b)
    assert q==0 or (q>0)==((a>=0)==(b>=0))

@pytest.mark.parametrize('op', ['+','-','*','/','<','>','<=','>=','==','!='])
@pytest.mark.parametrize('a,b', [(True,1),(1,False)])
def test_nao_coage_bool_int(op,a,b):
    with pytest.raises(ValueError): avaliar(op,a,b)
    cod=[Instr(op,'t1',a,b)]
    assert dobrar_constantes(cod)==(cod,False)

@pytest.mark.parametrize('arquivo', sorted(Path('tests/casos/validos').glob('*.mini')))
def test_determinismo_alvos_e_ponto_fixo(arquivo):
    fonte=arquivo.read_text()
    original=tac(fonte); copia=deepcopy(original)
    assert original==tac(fonte)
    novo=otimizar(original)
    assert original==copia
    assert novo==otimizar(novo)
    labels=[i.dest for i in novo if i.op=='label']
    assert len(labels)==len(set(labels))
    assert all(i.dest in labels for i in novo if i.op in ('goto','iffalse'))
    assert all(p(novo)[1] is False for p in PASSES)

@pytest.mark.parametrize('fonte,divisoes', [
 ('mostra_so(1 / 0);',1),
 ('trem x: inteirim = 0; trem y: inteirim = 1 / x;',1),
 ('uai (num_eh) { mostra_so(1 / 0); } mostra_so(2);',0),
 ('trem x: inteirim = 2; enquanto_tiver (x > 0) { mostra_so(0 / x); x = x - 1; }',1),
])
def test_falha_alcancavel_e_inalcancavel(fonte,divisoes):
    assert sum(i.op=='/' for i in otimizar(tac(fonte)))==divisoes

def test_api_rejeita_semantica_invalida():
    with pytest.raises(ValueError): gerar_tac(parse('mostra_so(ausente);'))

def test_juncao_nao_herda_constante_de_um_ramo():
    c=[Instr('iffalse','L1','c'),Instr('=','x',1),Instr('goto','L2'),
       Instr('label','L1'),Instr('=','x',2),Instr('label','L2'),Instr('print',None,'x')]
    assert otimizar(c)[-1].a1=='x'

@pytest.mark.parametrize('bits',product([False,True],repeat=7))
def test_cli_combinacoes(bits):
    flags=[f for f,b in zip(['--tokens','--ast','--tipos','--verificar','--contexto','--tac','-O'],bits) if b]
    inspect=any(f in flags for f in ['--tokens','--ast','--tipos','--verificar'])
    gera='--tac' in flags or not inspect
    r=subprocess.run([sys.executable,'-m','miniforge','exemplos/fatorial.mini',*flags],capture_output=True,text=True)
    assert r.returncode==(2 if '-O' in flags and not gera else 0),r.stderr
    if r.returncode==0:
        assert ('goto L1' in r.stdout)==gera
        assert ('tudo certim' in r.stdout)==('--verificar' in flags)

def test_imports_sem_backend():
    r=subprocess.run([sys.executable,'-c','import sys; import miniforge.ir, miniforge.otimizador; assert "miniforge.vm" not in sys.modules'],capture_output=True)
    assert r.returncode==0
    assert not Path('miniforge/vm.py').exists()

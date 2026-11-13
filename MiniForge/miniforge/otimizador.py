"""Passes locais que devolvem código novo e indicador de alteração."""

import re

from .ir import OPERADORES, Instr
from .semantica import REGRAS
from .constantes import OPS, avaliar, tipo_constante

_TEMPORARIO = re.compile(r"t[0-9]+")

# Toda escrita invalida a constante anterior, inclusive read.
_ESCREVEM = ("=", "neg", "read") + OPERADORES

# Instruções que terminam um bloco básico (além do rótulo, que inicia outro).
_SALTOS = ("goto", "iffalse")


def eh_const(x):
    """Constante do TAC: int ou bool (bool é subclasse de int). Nomes são str."""
    return isinstance(x, int)


def eh_temporario(nome):
    """t1, t2, ... criados pelo GeradorTAC (variáveis do fonte nunca casam)."""
    return isinstance(nome, str) and _TEMPORARIO.fullmatch(nome) is not None


def _pode_falhar(ins):
    """Divisão cujo divisor pode ser zero: a VM levantaria ErroExecucao."""
    return ins.op == "read" or ins.op == "/" and not (eh_const(ins.a2) and ins.a2 != 0)


def _trocar(ins, **campos):
    """Nova Instr igual a ins, com os campos dados trocados (mantém a linha)."""
    novo = dict(op=ins.op, dest=ins.dest, a1=ins.a1, a2=ins.a2,
                linha=ins.linha)
    novo.update(campos)
    return Instr(**novo)

# 1 · propagação de constantes


def propagar_constantes(codigo):
    """Invalida destinos escritos e esquece constantes nos limites de fluxo."""
    novo, mudou, conhecidas = [], False, {}
    for i in codigo:
        if i.op == "label":                  # início de bloco: esquece tudo
            conhecidas.clear()
            novo.append(i)
            continue
        a1, a2 = i.a1, i.a2
        if isinstance(a1, str) and a1 in conhecidas:
            a1 = conhecidas[a1]
        if isinstance(a2, str) and a2 in conhecidas:
            a2 = conhecidas[a2]
        if a1 is not i.a1 or a2 is not i.a2:
            i = _trocar(i, a1=a1, a2=a2)
            mudou = True
        if i.op in _SALTOS:                  # fim de bloco: esquece tudo
            conhecidas.clear()
        elif i.op in _ESCREVEM:
            conhecidas.pop(i.dest, None)
            if i.op == "=" and eh_const(i.a1):
                conhecidas[i.dest] = i.a1
        novo.append(i)
    return novo, mudou

# 2 · dobramento de constantes


def dobrar_constantes(codigo):
    """Avalia operandos literais válidos, preservando divisões por zero."""
    novo, mudou = [], False
    for i in codigo:
        if i.op in OPS and eh_const(i.a1) and eh_const(i.a2) \
                and (i.op, tipo_constante(i.a1), tipo_constante(i.a2)) in REGRAS \
                and not (i.op == "/" and i.a2 == 0):
            i = Instr("=", i.dest, avaliar(i.op, i.a1, i.a2), linha=i.linha)
            mudou = True
        elif i.op == "neg" and type(i.a1) is int:
            i = Instr("=", i.dest, -i.a1, linha=i.linha)
            mudou = True
        novo.append(i)
    return novo, mudou

# 3 · saltos constantes


def eliminar_saltos_constantes(codigo):
    """ifFalse false goto L vira goto L; ifFalse true goto L é removido."""
    novo, mudou = [], False
    for i in codigo:
        if i.op == "iffalse" and isinstance(i.a1, bool):
            mudou = True
            if i.a1:                         # nunca salta
                continue
            i = Instr("goto", i.dest, linha=i.linha)   # sempre salta
        novo.append(i)
    return novo, mudou

# 4 · código morto


def eliminar_codigo_morto(codigo):
    """Remove código inalcançável e temporários dispensáveis, preservando efeitos e falhas."""
    lidos = {a for i in codigo for a in (i.a1, i.a2) if isinstance(a, str)}
    novo, mudou, alcancavel = [], False, True
    for i in codigo:
        if i.op == "label":
            alcancavel = True
        if not alcancavel:
            mudou = True
            continue
        if i.op in _ESCREVEM and eh_temporario(i.dest) \
                and i.dest not in lidos and not _pode_falhar(i):
            mudou = True
            continue
        if i.op == "goto":
            alcancavel = False
        novo.append(i)
    return novo, mudou

# 5 · limpeza de rótulos


def limpar_rotulos(codigo):
    """Remove goto L seguido de L: e os rótulos sem referência."""
    novo, mudou = [], False
    for k, i in enumerate(codigo):
        seguinte = codigo[k + 1] if k + 1 < len(codigo) else None
        if i.op == "goto" and seguinte is not None \
                and seguinte.op == "label" and seguinte.dest == i.dest:
            mudou = True                     # saltaria para onde já vai
            continue
        novo.append(i)
    alvos = {i.dest for i in novo if i.op in _SALTOS}
    sem_orfaos = [i for i in novo if i.op != "label" or i.dest in alvos]
    return sem_orfaos, mudou or len(sem_orfaos) != len(novo)

# ponto fixo

PASSES = [propagar_constantes, dobrar_constantes,
          eliminar_saltos_constantes,
          eliminar_codigo_morto, limpar_rotulos]


def otimizar(codigo):
    """Aplica todos os PASSES até o ponto fixo (nenhum mudar nada)."""
    mudou = True
    while mudou:                         # até o ponto fixo
        mudou = False
        for passe in PASSES:
            codigo, m = passe(codigo)
            mudou = mudou or m
    return codigo

"""Passes de otimização sobre o TAC, preservando o comportamento (aula 30).

Contrato dos passes (slide 4): cada passe recebe a lista de Instr e devolve
(nova_lista, mudou). Os passes nunca alteram as instruções recebidas: quando
precisam mudar uma, criam outra Instr (com a mesma linha do fonte, que a VM
usa nos erros de execução).

Os cinco passes da tabela do slide 2, todos locais:

    PASSE                     ANTES                         DEPOIS
    propagar_constantes       x = 5 / t2 = x + 1            x = 5 / t2 = 5 + 1
    dobrar_constantes         t1 = 2 * 3                    t1 = 6
    eliminar_saltos_constantes
                              ifFalse false goto L          goto L
                              ifFalse true goto L           (removido)
    eliminar_codigo_morto     instruções após goto até o próximo rótulo;
                              temporários nunca lidos       (removidos)
    limpar_rotulos            goto L seguido de L: ;
                              rótulo sem referência         (removidos)

Bloco básico: sequência de instruções sem rótulo no meio e sem salto exceto no
fim. A propagação só vale dentro de um bloco básico, por isso o dicionário de
constantes conhecidas é zerado em rótulos e saltos (docs/arquitetura.md,
cuidado 6): no início de um while, n pode ter vindo do n = 5 de antes do laço
ou do n = t3 do fim do corpo; propagar o 5 ali seria um erro.

Ponto fixo: um passe cria oportunidades para outro (propagação -> dobramento
-> salto constante -> código morto). otimizar() repete todos os passes até
nenhum mudar nada. Todo passe só remove instruções ou troca uma instrução por
outra no mesmo lugar, nunca acrescenta; e cada troca torna a instrução mais
simples (variável -> constante, conta -> cópia, ifFalse -> goto). Por isso o
laço sempre termina.

Erros de execução são preservados: x / 0 nunca é dobrado (o erro deve
continuar acontecendo em tempo de execução, slide 3), e um temporário nunca
lido só é removido se a instrução que o calcula não puder falhar, ou seja,
se não for uma divisão por um divisor que pode ser zero.

O que é "temporário": o GeradorTAC (aula 26) cria t1, t2, ... e dá a uma
variável do fonte com essa forma o nome interno t1.1. Então todo nome que casa
com t[0-9]+ é temporário. Variáveis do programa nunca são removidas: no slide
3, base = 10 e lim = 100 continuam no código otimizado.
"""

import re

from .ir import OPERADORES, Instr
from .semantica import REGRAS
from .constantes import OPS, avaliar, tipo_constante

_TEMPORARIO = re.compile(r"t[0-9]+")

# Instruções que escrevem em dest (cópia, binárias e neg).
_ESCREVEM = ("=", "neg") + OPERADORES

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
    return ins.op == "/" and not (eh_const(ins.a2) and ins.a2 != 0)


def _trocar(ins, **campos):
    """Nova Instr igual a ins, com os campos dados trocados (mantém a linha)."""
    novo = dict(op=ins.op, dest=ins.dest, a1=ins.a1, a2=ins.a2,
                linha=ins.linha)
    novo.update(campos)
    return Instr(**novo)


# ----------------------------------------------------------------------
# 1 · propagação de constantes
# ----------------------------------------------------------------------
def propagar_constantes(codigo):
    """x = 5 seguido de t2 = x + 1 vira t2 = 5 + 1, dentro do bloco básico.

    O dicionário de constantes conhecidas (nome -> valor) é zerado em rótulos
    e saltos. Toda escrita em dest invalida o valor antigo; só uma cópia de
    constante (x = 5) registra um novo. Os operandos de ifFalse são trocados
    antes de zerar o dicionário: a condição ainda pertence ao bloco.
    """
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


# ----------------------------------------------------------------------
# 2 · dobramento de constantes
# ----------------------------------------------------------------------
def dobrar_constantes(codigo):
    """t1 = 2 * 3 vira t1 = 6 (código do slide 4).

    Nunca dobra x / 0: o erro deve continuar acontecendo em tempo de
    execução. As contas usam o avaliador constante independente, então / trunca
    para zero exatamente como na execução. Também dobra o menos unário de uma
    constante: t1 = -5 (neg de 5) vira a cópia t1 = -5, sem conversão para float.
    """
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


# ----------------------------------------------------------------------
# 3 · saltos constantes
# ----------------------------------------------------------------------
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


# ----------------------------------------------------------------------
# 4 · código morto
# ----------------------------------------------------------------------
def eliminar_codigo_morto(codigo):
    """Remove o inalcançável e os temporários nunca lidos.

    * Depois de um goto, nada é alcançado até o próximo rótulo (só se chega a
      uma instrução pela anterior ou por um salto, que sempre mira um rótulo).
    * t = ... cujo temporário nunca aparece como operando não serve para nada
      e sai, a menos que seja uma divisão que pode falhar (divisor que pode
      ser zero): aí o erro de execução é observável e a instrução fica.
    """
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


# ----------------------------------------------------------------------
# 5 · limpeza de rótulos
# ----------------------------------------------------------------------
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


# ----------------------------------------------------------------------
# ponto fixo
# ----------------------------------------------------------------------
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

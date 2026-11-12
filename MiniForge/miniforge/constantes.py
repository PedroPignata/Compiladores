"""Avaliação de uma operação literal em compilação; não percorre TAC nem executa programas."""
import operator
from .semantica import REGRAS


def tipo_constante(valor):
    return {int: 'int', bool: 'bool'}.get(type(valor))


def dividir(a, b):
    """Divisão inteira exata, truncada para zero, inclusive inteiros grandes."""
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b >= 0) else -q


OPS = {'+': operator.add, '-': operator.sub, '*': operator.mul, '/': dividir,
       '<': operator.lt, '>': operator.gt, '<=': operator.le, '>=': operator.ge,
       '==': operator.eq, '!=': operator.ne}


def avaliar(op, a, b):
    if (op, tipo_constante(a), tipo_constante(b)) not in REGRAS:
        raise ValueError('operação constante com tipos inválidos')
    return OPS[op](a, b)

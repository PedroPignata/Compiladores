"""Execução de TAC válido com memória, saltos e entrada e saída."""
import sys
from random import SystemRandom

_sorteador = SystemRandom()
from .constantes import avaliar
from .ir import OPERADORES, formatar


class ErroExecucao(Exception):
    pass


def executar(codigo, entrada=None, saida=None, erros=None):
    entrada = sys.stdin if entrada is None else entrada
    saida = sys.stdout if saida is None else saida
    erros = sys.stderr if erros is None else erros
    memoria = {}
    rotulos = {i.dest: k for k, i in enumerate(codigo) if i.op == 'label'}

    def valor(a):
        return memoria[a] if isinstance(a, str) else a

    pc = 0
    while pc < len(codigo):
        i = codigo[pc]
        try:
            if i.op == '=':
                memoria[i.dest] = valor(i.a1)
            elif i.op in OPERADORES:
                memoria[i.dest] = avaliar(i.op, valor(i.a1), valor(i.a2))
            elif i.op == 'neg':
                memoria[i.dest] = -valor(i.a1)
            elif i.op == 'random':
                minimo, maximo = valor(i.a1), valor(i.a2)
                if minimo > maximo:
                    raise ErroExecucao(f'linha {i.linha}: intervalo inválido em sorteia_so')
                memoria[i.dest] = _sorteador.randint(minimo, maximo)
            elif i.op == 'read':
                while True:
                    saida.flush()
                    texto = entrada.readline()
                    if texto == '':
                        raise ErroExecucao(f'linha {i.linha}: fim da entrada durante le_so')
                    texto = texto.strip()
                    digitos = texto[1:] if texto.startswith(('+', '-')) else texto
                    try:
                        if not digitos or any(c not in '0123456789' for c in digitos):
                            raise ValueError()
                        memoria[i.dest] = int(texto)
                        break
                    except ValueError:
                        print('Entrada inválida: digite um inteiro.', file=erros, flush=True)
            elif i.op == 'texto':
                print(i.dest, file=saida, flush=True)
            elif i.op == 'print':
                print(formatar(valor(i.a1)), file=saida, flush=True)
            elif i.op == 'goto':
                pc = rotulos[i.dest]
                continue
            elif i.op == 'iffalse':
                if not valor(i.a1):
                    pc = rotulos[i.dest]
                    continue
            elif i.op != 'label':
                raise ErroExecucao(f'linha {i.linha}: instrução desconhecida: {i.op}')
        except ZeroDivisionError as erro:
            raise ErroExecucao(f'linha {i.linha}: divisão por zero') from erro
        pc += 1
    return memoria

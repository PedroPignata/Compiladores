"""Interface de teclado: compila uma conta em mineirês e apresenta a constante.

Não interpreta TAC: aceita apenas o resultado literal produzido pelo otimizador
para uma conta fechada, sem laços ou entrada pendente no programa gerado.
Execute da raiz MiniForge/: python -m exemplos.calculadora.interativa
"""
import argparse
from dataclasses import dataclass

from miniforge.lexer import Lexer
from miniforge.parser import Parser
from miniforge.ir import formatar_tac, gerar_tac
from miniforge.otimizador import otimizar

OPERACOES = {'1': '+', '2': '-', '3': '*', '4': '/'}


@dataclass(frozen=True)
class ContaCompilada:
    fonte: str
    tac: str
    tac_otimizado: str
    resultado: int


def calcular(primeiro: int, segundo: int, operacao: str) -> ContaCompilada:
    """Obtém uma resposta inteira exclusivamente do TAC dobrado pelo MiniForge."""
    if type(primeiro) is not int or type(segundo) is not int:
        raise ValueError('Use somente números inteiros.')
    if operacao not in OPERACOES:
        raise ValueError('Escolha uma operação de 1 a 4.')
    if operacao == '4' and segundo == 0:
        raise ValueError('Não é possível dividir por zero. Escolha outro divisor.')
    op = OPERACOES[operacao]
    fonte = (f'trem primeiro: inteirim = {primeiro};\n'
             f'trem segundo: inteirim = {segundo};\n'
             f'mostra_so(primeiro {op} segundo);\n')
    lexer = Lexer(fonte)
    tokens = lexer.tokens()
    if lexer.erros:
        raise ValueError('; '.join(lexer.erros))
    # gerar_tac também exige uma AST semanticamente válida.
    original = gerar_tac(Parser(tokens).programa())
    otimizado = otimizar(original)
    # Esta interface não percorre saltos nem mantém memória de um programa.
    # O contrato é uma conta fechada: só cópias literais e uma saída literal.
    saidas = [i for i in otimizado if i.op == 'print']
    if (len(saidas) != 1 or type(saidas[0].a1) is not int
            or any(i.op not in ('=', 'print') for i in otimizado)
            or any(i.op == '=' and type(i.a1) is not int for i in otimizado)):
        raise ValueError('O compilador não reduziu a conta a um resultado inteiro.')
    return ContaCompilada(fonte, formatar_tac(original),
                         formatar_tac(otimizado), saidas[0].a1)


def ler_inteiro(pergunta: str) -> int:
    while True:
        texto = input(pergunta).strip()
        # Mesma escrita decimal do mineirês, com sinal opcional.
        digitos = texto[1:] if texto.startswith(('+', '-')) else texto
        if not digitos or any(c not in '0123456789' for c in digitos):
            print('Entrada inválida. Digite um número inteiro, como 18 ou -7.')
            continue
        try:
            return int(texto)
        except ValueError:
            print('Número maior que o limite de conversão deste Python. Tente outro.')


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='Calculadora Mineira interativa')
    parser.add_argument('--detalhes', action='store_true',
                        help='mostra o fonte mineirês e os TAC de cada conta')
    args = parser.parse_args(argv)
    print('Calculadora Mineira | MiniForge')
    print('Divisão inteira: 7 / 2 = 3. Use 0 no menu para sair.')
    try:
        while True:
            print('\n1 - Somar\n2 - Subtrair\n3 - Multiplicar\n4 - Dividir\n0 - Sair')
            operacao = input('Escolha a operação: ').strip()
            if operacao == '0':
                break
            if operacao not in OPERACOES:
                print('Opção inválida. Escolha 1, 2, 3, 4 ou 0.')
                continue
            primeiro = ler_inteiro('Primeiro número: ')
            segundo = ler_inteiro('Segundo número: ')
            try:
                conta = calcular(primeiro, segundo, operacao)
            except ValueError as erro:
                print(f'Não foi possível calcular: {erro}')
                continue
            if args.detalhes:
                print('\nFonte mineirês:\n' + conta.fonte)
                print('TAC original:\n' + conta.tac)
                print('TAC otimizado:\n' + conta.tac_otimizado)
            print(f'Resultado: {primeiro} {OPERACOES[operacao]} {segundo} = {conta.resultado}')
    except (EOFError, KeyboardInterrupt):
        print()
    print('Até mais, sô!')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

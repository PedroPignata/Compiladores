"""Ponto de entrada do nucleo do simulador"""

# deixa as duas classes principais disponiveis para o restante do projeto
from .simulator import EmptyInputError, TransformerSimulator

__all__ = ["EmptyInputError", "TransformerSimulator"]

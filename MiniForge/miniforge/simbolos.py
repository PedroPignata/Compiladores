"""Pilha de escopos e registro de declarações e usos."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Simbolo:
    nome: str
    tipo: str            # 'int' | 'bool'
    categoria: str       # 'variavel' (única categoria nesta versão)
    linha: int           # linha da declaração
    nivel: int           # 0 = global, 1 = primeiro bloco, ...

    # A contagem de leituras não altera a identidade do símbolo.
    usos: int = field(default=0, compare=False)


class TabelaSimbolos:
    """Busca nomes do escopo mais interno ao global."""

    def __init__(self):
        self.escopos: List[Dict[str, Simbolo]] = [{}]    # [global, bloco1, ...]

    @property
    def nivel(self) -> int:
        """Nível do escopo atual (0 = global)."""
        return len(self.escopos) - 1

    def entrar_escopo(self) -> None:
        self.escopos.append({})

    def sair_escopo(self) -> Dict[str, Simbolo]:
        """Desempilha o escopo atual e devolve os símbolos que ele tinha."""
        if len(self.escopos) == 1:
            raise RuntimeError("não é possível sair do escopo global")
        return self.escopos.pop()

    def declarar(self, nome: str, tipo: str, linha: int) -> Optional[Simbolo]:
        """Insere o nome no escopo atual. Devolve None se for redeclaração."""
        atual = self.escopos[-1]
        if nome in atual:
            return None                                   # redeclaração
        s = Simbolo(nome, tipo, "variavel", linha, len(self.escopos) - 1)
        atual[nome] = s
        return s

    def buscar(self, nome: str) -> Optional[Simbolo]:
        """Procura do escopo mais interno ao global; None se não existir."""
        for escopo in reversed(self.escopos):
            if nome in escopo:
                return escopo[nome]
        return None

"""Símbolos e pilha de escopos léxicos (aula 20).

Cada nome declarado vira um Simbolo com seus atributos. A TabelaSimbolos é
uma pilha de dicionários: a base é o escopo global (nível 0) e cada bloco
{ ... } empilha um dicionário novo. A busca vai do topo para a base, então um
nome declarado num bloco interno sombreia o de mesmo nome dos níveis abaixo;
ao sair do bloco o dicionário é desempilhado e o nome externo volta a valer.

    trem x: inteirim = 1;              // nível 0
    {
        trem y: inteirim = 2;          // nível 1
        {
            trem x: booleanim = eh_memo;   // nível 2: sombreia x
            mostra_so(y);                  // buscar("y") acha no nível 1
        }
    }

Decisão da turma (registrada em docs/especificacao.md): redeclarar no mesmo
escopo é erro; declarar o mesmo nome em escopo interno é permitido.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Simbolo:
    nome: str
    tipo: str            # 'int' | 'bool'
    categoria: str       # 'variavel' (única categoria nesta versão)
    linha: int           # linha da declaração
    nivel: int           # 0 = global, 1 = primeiro bloco, ...
    # Desafio da aula 20: quantas vezes o valor foi lido. Fica fora da
    # comparação para Simbolo("x", "int", "variavel", 1, 0) continuar igual
    # a um símbolo já usado.
    usos: int = field(default=0, compare=False)


class TabelaSimbolos:
    """Pilha de escopos com as 4 operações do slide da aula 20."""

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

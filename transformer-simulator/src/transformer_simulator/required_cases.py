"""Os dez cenários mínimos definidos no enunciado da atividade."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RequiredCase:
    number: int
    title: str
    input_text: str
    expected_behavior: str
    secondary_input: str | None = None


REQUIRED_CASES = (
    RequiredCase(1, "Pergunta curta", "Tudo bem?", "Executar todo o pipeline e gerar um fallback."),
    RequiredCase(2, "Frase afirmativa", "O Brasil é um país.", "Reconhecer uma afirmação e responder sem falhar."),
    RequiredCase(3, "Frase com pontuação", "Olá, mundo!", "Separar vírgula e exclamação em tokens próprios."),
    RequiredCase(4, "Palavra desconhecida", "Xilofone quântico.", "Marcar palavras ausentes com o ID de <UNK>."),
    RequiredCase(5, "Palavras repetidas", "Brasil Brasil Brasil.", "Reutilizar o ID e manter posições distintas."),
    RequiredCase(
        6,
        "Mesmas palavras em ordens diferentes",
        "O cachorro mordeu o homem.",
        "Produzir vetores posicionados diferentes quando a ordem muda.",
        secondary_input="O homem mordeu o cachorro.",
    ),
    RequiredCase(
        7,
        "Pergunta respondível",
        "Qual é a capital do Brasil?",
        "Gerar a resposta cadastrada token por token.",
    ),
    RequiredCase(
        8,
        "Pergunta não respondível",
        "Qual é a capital de Marte?",
        "Informar honestamente que não há resposta cadastrada.",
    ),
    RequiredCase(9, "Texto vazio", "   ", "Bloquear o processamento com uma mensagem de validação."),
    RequiredCase(
        10,
        "Caracteres especiais",
        "IA & compiladores #2026!",
        "Tokenizar caracteres especiais sem encerrar com erro.",
    ),
)

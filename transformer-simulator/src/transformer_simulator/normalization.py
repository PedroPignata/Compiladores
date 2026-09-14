"""Normalização explícita e conservadora da entrada."""

from __future__ import annotations

import re
import unicodedata

from .models import NormalizationResult


class EmptyInputError(ValueError):
    """Erro apresentado quando não existe texto útil para processar."""


def normalize_text(text: str) -> NormalizationResult:
    """Normaliza Unicode e espaços, preservando caixa e pontuação."""

    if not text or not text.strip():
        raise EmptyInputError("Digite uma frase ou pergunta antes de processar.")

    unicode_normalized = unicodedata.normalize("NFKC", text)
    normalized = re.sub(r"\s+", " ", unicode_normalized).strip()

    changes: list[str] = []
    if unicode_normalized != text:
        changes.append("Caracteres Unicode equivalentes foram padronizados.")
    if normalized != unicode_normalized:
        changes.append("Espaços duplicados e espaços nas extremidades foram removidos.")
    if not changes:
        changes.append("A entrada já respeitava as regras de normalização.")

    return NormalizationResult(
        original=text,
        normalized=normalized,
        rules=(
            "Padronizar caracteres Unicode com NFKC.",
            "Substituir sequências de espaços por um único espaço.",
            "Preservar letras maiúsculas e minúsculas.",
            "Preservar pontuação e caracteres especiais para a tokenização.",
        ),
        changes=tuple(changes),
    )

"""Geração didática token a token com probabilidades explícitas."""

from __future__ import annotations

import re
import unicodedata
import math
from collections.abc import Callable

from .models import CandidateProbability, GenerationStep
from .tokenization import detokenize, tokenize


ContextEncoder = Callable[[tuple[str, ...]], tuple[float, ...]]


def _canonicalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text.casefold())
    without_accents = "".join(char for char in decomposed if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", without_accents).strip()


def select_didactic_answer(text: str) -> tuple[str, str]:
    """Escolhe uma resposta cadastrada ou um fallback honesto."""

    canonical = _canonicalize(text)
    if "qual e a capital do brasil" in canonical:
        return "A capital do Brasil é Brasília.", "pergunta cadastrada: capital do Brasil"
    if "o que e um compilador" in canonical:
        return (
            "Um compilador traduz código-fonte para outra representação.",
            "pergunta cadastrada: definição de compilador",
        )
    if re.search(r"\b2\s*\+\s*2\b", canonical):
        return "2 + 2 é igual a 4.", "pergunta cadastrada: soma 2 + 2"
    if canonical.endswith("?"):
        return (
            "Não tenho uma resposta cadastrada para essa pergunta.",
            "fallback para pergunta desconhecida",
        )
    return (
        "Entendi: você apresentou uma frase afirmativa.",
        "fallback para frase afirmativa",
    )


DISTRACTORS = (
    "São",
    "Rio",
    "Salvador",
    "Recife",
    "não",
    "uma",
    "resposta",
    "?",
    ".",
    "!",
)


def _candidate_distribution(
    target: str,
    iteration: int,
    context_summary: tuple[float, ...],
) -> tuple[CandidateProbability, ...]:
    contextual_signal = 0.5 + 0.5 * math.tanh(sum(context_summary) / len(context_summary))
    target_probability = min(0.92, 0.76 + 0.08 * contextual_signal + iteration * 0.004)
    remaining = 1.0 - target_probability
    candidates = [target]
    offset = iteration % len(DISTRACTORS)
    rotated = DISTRACTORS[offset:] + DISTRACTORS[:offset]
    candidates.extend(token for token in rotated if token != target)
    candidates = candidates[:4]
    ratios = (4.0, 3.0, 2.0)
    ratio_total = sum(ratios[: len(candidates) - 1])
    probabilities = [target_probability]
    probabilities.extend(remaining * ratio / ratio_total for ratio in ratios[: len(candidates) - 1])
    return tuple(
        CandidateProbability(token=token, probability=float(probability))
        for token, probability in zip(candidates, probabilities, strict=True)
    )


def generate_response(
    input_tokens: tuple[str, ...],
    normalized_input: str,
    context_encoder: ContextEncoder,
    max_new_tokens: int = 64,
) -> tuple[tuple[GenerationStep, ...], tuple[str, ...], str, str]:
    """Reprocessa o contexto e seleciona o maior valor a cada iteração."""

    answer, answer_source = select_didactic_answer(normalized_input)
    target_tokens = tokenize(answer)[:max_new_tokens]
    generated: list[str] = []
    steps: list[GenerationStep] = []

    for iteration, target in enumerate(target_tokens, start=1):
        context = input_tokens + tuple(generated)
        context_summary = context_encoder(context)
        candidates = _candidate_distribution(target, iteration - 1, context_summary)
        selected = max(candidates, key=lambda candidate: candidate.probability).token
        generated.append(selected)
        steps.append(
            GenerationStep(
                iteration=iteration,
                context_tokens=context,
                context_token_count=len(context),
                context_summary=context_summary,
                candidates=candidates,
                selected_token=selected,
                progressive_text=detokenize(generated),
            )
        )

    final_answer = detokenize(generated)
    completion_reason = f"Resposta concluída após {len(generated)} tokens; {answer_source}."
    return tuple(steps), tuple(generated), final_answer, completion_reason

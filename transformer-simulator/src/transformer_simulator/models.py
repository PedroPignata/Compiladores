"""Contratos de dados imutáveis usados pelo núcleo e pela interface."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class NormalizationResult:
    original: str
    normalized: str
    rules: tuple[str, ...]
    changes: tuple[str, ...]


@dataclass(frozen=True)
class TokenInfo:
    text: str
    position: int
    token_id: int
    known: bool
    category: str


@dataclass(frozen=True)
class VectorInfo:
    token: str
    position: int
    values: tuple[float, ...]


@dataclass(frozen=True)
class AttentionHeadResult:
    name: str
    didactic_focus: str
    queries: tuple[tuple[float, ...], ...]
    keys: tuple[tuple[float, ...], ...]
    values: tuple[tuple[float, ...], ...]
    scores: tuple[tuple[float, ...], ...]
    weights: tuple[tuple[float, ...], ...]
    output: tuple[tuple[float, ...], ...]
    matrices: dict[str, tuple[tuple[float, ...], ...]]


@dataclass(frozen=True)
class LayerResult:
    name: str
    description: str
    input_vectors: tuple[tuple[float, ...], ...]
    output_vectors: tuple[tuple[float, ...], ...]
    mean_change: float


@dataclass(frozen=True)
class CandidateProbability:
    token: str
    probability: float


@dataclass(frozen=True)
class GenerationStep:
    iteration: int
    context_tokens: tuple[str, ...]
    context_token_count: int
    context_summary: tuple[float, ...]
    candidates: tuple[CandidateProbability, ...]
    selected_token: str
    progressive_text: str


@dataclass(frozen=True)
class SimulationResult:
    normalization: NormalizationResult
    input_tokens: tuple[TokenInfo, ...]
    embeddings: tuple[VectorInfo, ...]
    positional_encodings: tuple[VectorInfo, ...]
    positioned_vectors: tuple[VectorInfo, ...]
    attention_heads: tuple[AttentionHeadResult, ...]
    combined_attention: tuple[tuple[float, ...], ...]
    layers: tuple[LayerResult, ...]
    generation_steps: tuple[GenerationStep, ...]
    generated_tokens: tuple[str, ...]
    final_answer: str
    processing_cycles: int
    selection_strategy: str
    completion_reason: str
    real_parts: tuple[str, ...]
    simulated_parts: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Converte o resultado completo em dados serializáveis em JSON."""

        return asdict(self)

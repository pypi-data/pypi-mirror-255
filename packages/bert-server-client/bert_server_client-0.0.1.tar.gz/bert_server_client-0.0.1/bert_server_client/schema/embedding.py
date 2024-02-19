from dataclasses import dataclass, field


@dataclass
class EmbeddingData:
    object: str
    embedding: list[float]
    index: int


@dataclass
class EmbeddingUsage:
    prompt_tokens: int
    total_tokens: int


@dataclass
class Embedding:
    object: str
    data: list[EmbeddingData]
    model: str
    usage: EmbeddingUsage = field(default=None)


@dataclass
class EmbeddingRequest:
    input: str
    model: str

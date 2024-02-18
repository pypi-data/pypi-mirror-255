from __future__ import annotations

from typing import Sequence

import numpy as np
import pyarrow as pa

from chalk.features._embedding.embedding_provider import EmbeddingProvider
from chalk.features._vector import Vector
from chalk.utils.missing_dependency import missing_dependency_exception

try:
    import openai
    import tiktoken
except ImportError:
    openai = None
    tiktoken = None


MAX_INPUT_TOKENS = 8191


class OpenAIProvider(EmbeddingProvider):
    def __init__(self, model: str) -> None:
        super().__init__()
        if not openai or not tiktoken:
            raise missing_dependency_exception("chalkpy[openai]")
        if model != "text-embedding-ada-002":
            raise ValueError(
                f"Unsupported model '{model}' for OpenAI. The supported models are ['text-embedding-ada-002']."
            )
        self.model = model
        try:
            self.encoding = tiktoken.encoding_for_model(self.model)
        except KeyError:
            # Use cl100k_base encoding by default
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def get_provider_name(self) -> str:
        return "openai"

    def get_model_name(self) -> str:
        return self.model

    def validate_input_schema(self, input_schema: Sequence[pa.DataType]) -> str | None:
        if len(input_schema) != 1:
            return f"OpenAI emeddings support only 1 input, but got {len(input_schema)} inputs"
        if input_schema[0] != pa.large_utf8():
            return f"OpenAI embeddings require a large_utf8() feature, but got a feature of type {input_schema[0]}"

        return super().validate_input_schema(input_schema)

    def _truncate_embedding_input(self, input: str) -> str:
        input_tokens = self.encoding.encode(input)
        if len(input_tokens) > MAX_INPUT_TOKENS:
            return self.encoding.decode(input_tokens[:MAX_INPUT_TOKENS])
        return input

    def generate_embedding(self, input: pa.Table) -> Sequence[Vector]:
        assert openai
        inputs: list[str] = [self._truncate_embedding_input(i) for i in input.column(0).to_pylist()]
        response = openai.embeddings.create(input=inputs, model=self.model)
        vectors = np.array(
            [entry.embedding for entry in response.data],
            dtype=np.dtype(self.get_vector_class().precision.replace("fp", "float")),
        )
        return pa.FixedSizeListArray.from_arrays(vectors.reshape(-1), self.get_vector_class().num_dimensions)

    def get_vector_class(self) -> type[Vector]:
        return Vector[1536]

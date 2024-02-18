from __future__ import annotations

from datetime import timedelta
from typing import Any, Callable

import pyarrow as pa

from chalk._lsp.error_builder import get_resolver_error_builder
from chalk.features._embedding.cohere import CohereProvider
from chalk.features._embedding.embedding_provider import EmbeddingProvider
from chalk.features._embedding.openai import OpenAIProvider
from chalk.features.dataframe import DataFrame
from chalk.features.feature_field import Feature
from chalk.features.feature_set import Features
from chalk.features.feature_wrapper import FeatureWrapper, unwrap_feature
from chalk.features.resolver import RESOLVER_REGISTRY, OnlineResolver
from chalk.serialization.parsed_annotation import ParsedAnnotation
from chalk.utils.collections import ensure_tuple


def _get_provider(provider: str, model: str) -> EmbeddingProvider:
    """Factory function to get an EmbeddingProvider"""
    if provider == "openai":
        return OpenAIProvider(model)
    elif provider == "cohere":
        return CohereProvider(model)
    raise ValueError(f"Unsupported embedding provider: {provider}. The supported providers are ['openai', 'cohere'].")


def embed(
    input: Callable[[], Any],
    provider: str,
    model: str,
    name: str | None = None,
    owner: str | None = None,
    tags: list[str] | None = None,
    max_staleness: str | timedelta | None | ellipsis = ...,
    description: str | None = None,
    version: int | None = None,
    default_version: int = 1,
    etl_offline_to_online: bool | None = None,
    offline_ttl: ellipsis | str | timedelta | None = ...,
) -> Any:
    """Specify an embedding feature.

    Parameters
    ----------
    input
        The input for the embedding. This argument is callable
        to allow for forward references to features of the same
        class.
    provider
        The AI provider to use for the embedding.
    model
        The model to generate the embedding.
    name
        An alternative name for the feature. By default, Chalk will use
        the attribute name as the feature name
    owner
        The feature owner
    tags
        Tags for th
    """
    embedding_provider = _get_provider(provider, model)
    # Manually set the dimensions of the Vector when using embedding
    typ = ParsedAnnotation(underlying=embedding_provider.get_vector_class())
    output_feature = Feature(
        name=name,
        owner=owner,
        tags=tags,
        typ=typ,
        max_staleness=max_staleness,
        description=description,
        version=version,
        default_version=default_version,
        etl_offline_to_online=etl_offline_to_online,
        offline_ttl=offline_ttl,
    )
    previous_hook = output_feature.hook

    def hook(features: type[Features]) -> None:
        if previous_hook:
            previous_hook(features)

        def resolver_factory():
            inputs = ensure_tuple(input())
            input_features_or_literals = tuple(
                unwrap_feature(x) if isinstance(x, (Feature, FeatureWrapper)) else x for x in inputs
            )
            input_features: set[Feature] = set()
            input_schema: list[pa.DataType] = []
            for x in input_features_or_literals:
                if isinstance(x, Feature):
                    input_features.add(x)
                    input_schema.append(x.converter.pyarrow_dtype)
                    continue
                if not isinstance(x, str):
                    raise TypeError("Embedding function literals must be strings")
                input_schema.append(pa.large_utf8())
            if features.__chalk_primary__ not in input_features:
                assert features.__chalk_primary__ is not None
                input_features.add(features.__chalk_primary__)
            error_str = embedding_provider.validate_input_schema(input_schema)
            if error_str:
                raise ValueError(
                    (
                        f"The first argument of the `embedding` function for feature '{output_feature.root_fqn}' returned an "
                        f"unsupported input schema for embedding model "
                        f"'{embedding_provider.get_provider_name()}/{embedding_provider.get_model_name()}': {error_str}."
                    )
                )

            def fn(raw_inputs: DataFrame):
                # We need to build the input table by combinding the literals with the features
                input_arrays: list[pa.Array | pa.ChunkedArray] = []
                raw_input_table = raw_inputs.to_pyarrow()
                assert features.__chalk_primary__ is not None
                pkeys = raw_input_table.column(features.__chalk_primary__.root_fqn)
                for x in input_features_or_literals:
                    if isinstance(x, Feature):
                        input_arrays.append(raw_input_table.column(x.root_fqn))
                    else:
                        input_arrays.append(pa.nulls(len(raw_input_table), pa.large_utf8()).fill_null(x))
                unified_inputs_table = pa.Table.from_arrays(
                    input_arrays, names=[f"col_{i}" for i in range(len(input_arrays))]
                )
                embeddings = embedding_provider.generate_embedding(unified_inputs_table)
                return pa.Table.from_arrays(
                    [embeddings, pkeys], [output_feature.root_fqn, features.__chalk_primary__.root_fqn]
                )

            return OnlineResolver(
                function_definition="",
                filename="",
                fqn=f"__chalk__embedding__resolver__namespace__{output_feature.namespace}__name__{output_feature.name}",
                name=None,
                doc=None,
                inputs=[DataFrame[tuple(input_features)]],
                state=None,
                output=Features[DataFrame[output_feature, features.__chalk_primary__]],
                fn=fn,
                environment=None,
                tags=output_feature.tags,
                machine_type=None,
                default_args=[None],
                owner=output_feature.owner,
                timeout=None,
                cron=None,
                when=None,
                data_sources=None,
                is_sql_file_resolver=False,
                source_line=None,
                lsp_builder=get_resolver_error_builder(fn),
            )

        RESOLVER_REGISTRY.add_to_deferred_registry(resolver_factory, override=False)

    output_feature.hook = hook

    return output_feature

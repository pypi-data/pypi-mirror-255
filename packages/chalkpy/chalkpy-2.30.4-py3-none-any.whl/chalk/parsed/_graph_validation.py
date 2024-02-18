from __future__ import annotations

import collections
import traceback
from collections import defaultdict
from typing import DefaultDict, Dict, List, Literal, Mapping, Optional, Tuple, Union

import pyarrow as pa

from chalk._lsp.error_builder import FeatureClassErrorBuilder, LSPErrorBuilder, ResolverErrorBuilder
from chalk.features import FeatureSetBase
from chalk.features._encoding.serialized_dtype import deserialize_dtype
from chalk.features.resolver import RESOLVER_REGISTRY
from chalk.parsed.duplicate_input_gql import (
    GraphLogSeverity,
    ProjectSettingsGQL,
    UpdateGraphError,
    UpsertFeatureGQL,
    UpsertGraphGQL,
    UpsertResolverGQL,
)
from chalk.utils import string
from chalk.utils.duration import parse_chalk_duration
from chalk.utils.string import oxford_comma_list, to_camel_case

_METADATA_STRING_TO_FEATURE_ATTRIBUTE_MAP: Dict[str, str] = {
    "owner": "owner",
    "tags": "tags",
    "description": "description",
}

_METADATA_STRING_TO_RESOLVER_ATTRIBUTE_MAP: Dict[str, str] = {
    "owner": "owner",
    "tags": "tags",
    "description": "doc",
    "doc": "doc",
    "docstring": "doc",
}


class _LogBuilder:
    def __init__(self):
        self._logs: List[UpdateGraphError] = []

    def add_log(self, header: str, subheader: str, severity: GraphLogSeverity):
        self._logs.append(UpdateGraphError(header=header, subheader=subheader, severity=severity))

    def add_error(self, header: str, subheader: str):
        self.add_log(header=header, subheader=subheader, severity=GraphLogSeverity.ERROR)

    def add_warning(self, header: str, subheader: str):
        self.add_log(header=header, subheader=subheader, severity=GraphLogSeverity.WARNING)

    def add_info(self, header: str, subheader: str):
        self.add_log(header=header, subheader=subheader, severity=GraphLogSeverity.INFO)

    def get_logs(self) -> List[UpdateGraphError]:
        return self._logs


def _validate_primary_key(
    feature: UpsertFeatureGQL,
    builder: _LogBuilder,
    lsp_builder: FeatureClassErrorBuilder,
):
    if feature.scalarKind is not None and feature.scalarKind.primary:
        assert feature.scalarKind.dtype is not None, f"The serialized dtype is not set for feature '{feature.id.fqn}'"
        pa_dtype = deserialize_dtype(feature.scalarKind.dtype)
        if (
            not pa.types.is_integer(pa_dtype)
            and not pa.types.is_large_string(pa_dtype)
            and not pa.types.is_string(pa_dtype)
        ):
            lsp_builder.add_diagnostic(
                label="invalid type",
                message=f"Primary keys must be integers or strings. Feature '{feature.id.attributeName}' has a type of '{pa_dtype}'",
                range=lsp_builder.annotation_range(feature.id.attributeName),
                code="23",
            )
            builder.add_error(
                header=f'Invalid primary key type "{feature.id.fqn}"',
                subheader=(
                    f"Primary keys must be integers or strings. " f'Feature "{feature.id.fqn}" has a type of {pa_dtype}'
                ),
            )


def _validate_max_staleness(
    feature: UpsertFeatureGQL,
    builder: _LogBuilder,
    lsp_builder: FeatureClassErrorBuilder,
):
    if feature.maxStaleness is not None and feature.maxStaleness != "infinity":
        try:
            parse_chalk_duration(feature.maxStaleness)
        except:
            builder.add_error(
                header=f'Could not parse max_staleness for feature "{feature.id.fqn}"',
                subheader=f'Received "{feature.maxStaleness}". See https://docs.chalk.ai/docs/duration for valid formats.',
            )


def _validate_etl_to_online(
    feature: UpsertFeatureGQL,
    builder: _LogBuilder,
    lsp_builder: FeatureClassErrorBuilder,
):
    if feature.etlOfflineToOnline and feature.maxStaleness is None:
        builder.add_error(
            header=f'Missing max staleness for "{feature.id.fqn}"',
            subheader=f'The feature "{feature.id.fqn}" is set to ETL to online, but doesn\'t specify a max staleness. Any ETL to online would be immediately invalidated.',
        )


def _validate_no_feature_times_as_input(
    fqn_to_feature: Mapping[str, UpsertFeatureGQL],
    resolver: UpsertResolverGQL,
    builder: _LogBuilder,
    lsp_builder: ResolverErrorBuilder,
):
    for i, inp in enumerate(resolver.inputs or []):
        if inp.underlying.fqn not in fqn_to_feature:
            lsp_builder.add_diagnostic(
                message=f"Resolver '{resolver.fqn}' requires an unrecognized feature '{inp.underlying.fqn}'",
                code="135",
                range=lsp_builder.function_arg_annotation_by_index(i),
                label="invalid resolver input",
            )
            builder.add_error(
                header=f"Resolver '{resolver.fqn}' requires an unknown feature '{inp.underlying.fqn}'",
                subheader="Please check the inputs to this resolver, and make sure they are all features.",
            )
        elif fqn_to_feature[inp.underlying.fqn].featureTimeKind is not None and resolver.kind != "offline":
            lsp_builder.add_diagnostic(
                message=(
                    f'The resolver "{resolver.fqn}" takes as input the\n'
                    f'feature "{inp.underlying.fqn}", a feature_time() type.\n'
                    f"Feature times can be returned from {resolver.kind} resolvers to\n"
                    "indicate data from the past, but cannot be accepted\n"
                    "as inputs."
                ),
                code="136",
                range=lsp_builder.function_arg_annotation_by_index(i),
                label="invalid resolver input",
            )
            builder.add_error(
                header=f"Feature times cannot be accepted as input to {resolver.kind} resolvers.",
                subheader=(
                    f'The resolver "{resolver.fqn}" takes as input the\n'
                    f'feature "{inp.underlying.fqn}", a feature_time() type.\n'
                    f"Feature times can be returned from {resolver.kind} resolvers to\n"
                    "indicate data from the past, but cannot be accepted\n"
                    "as inputs."
                ),
            )


def _validate_feature_names_unique(features: List[UpsertFeatureGQL], builder: _LogBuilder):
    counter: DefaultDict[str, int] = defaultdict(lambda: 0)
    for r in features:
        counter[r.id.fqn] += 1

    for fqn, count in counter.items():
        if count > 1:
            builder.add_error(
                header="Duplicate feature names",
                subheader=(
                    f'There are {count} features with the same name of "{fqn}". All features require a '
                    f"distinct name"
                ),
            )


def _validate_resolver_names_unique(resolvers: List[UpsertResolverGQL], builder: _LogBuilder):
    counter: DefaultDict[str, int] = defaultdict(lambda: 0)
    for r in resolvers:
        counter[r.fqn.split(".")[-1]] += 1

    for name, count in counter.items():
        if count > 1:
            builder.add_error(
                header="Duplicate resolver names",
                subheader=(
                    f'There are {count} resolvers with the same name of "{name}". All resolvers require a '
                    f"distinct name"
                ),
            )


def _validate_resolver_input(
    singleton_namespaces: set[str],
    resolver: UpsertResolverGQL,
    builder: _LogBuilder,
    lsp_builder: ResolverErrorBuilder,
):
    namespaces = []
    ns_to_arg_num: Dict[str, int] = {}

    for idx, input_ in enumerate(resolver.inputs or []):
        f = input_.path[0].parent if input_.path is not None and len(input_.path) > 0 else input_.underlying
        if f.namespace not in singleton_namespaces:
            ns_to_arg_num[f.namespace] = idx
            if f.namespace not in namespaces:
                namespaces.append(f.namespace)

    if len(namespaces) > 1:
        arg_num = list(ns_to_arg_num.values())[0]
        d = lsp_builder.add_diagnostic(
            message=f"""All inputs to a resolver should be rooted in the same namespace.
The resolver "{resolver.fqn}" takes inputs in the namespaces {oxford_comma_list(string.add_quotes(namespaces))}.

If you require features from many feature classes, reference them via their relationships, such as:
  User.bank_account.title,
  User.full_name""",
            code="131",
            range=lsp_builder.function_arg_annotation_by_index(arg_num),
            label="secondary namespace",
        )
        for ns, arg in ns_to_arg_num.items():
            if arg != arg_num:
                d.with_range(
                    lsp_builder.function_arg_annotation_by_index(arg),
                    label=f"other namespace {ns}",
                )

        builder.add_error(
            header=f'Resolver "{resolver.fqn}" requires features from multiple namespaces.',
            subheader=f"""All inputs to a resolver should be rooted in the same namespace.
The resolver "{resolver.fqn}" takes inputs in the namespaces {oxford_comma_list(string.add_quotes(namespaces))}.

If you require features from many feature classes, reference them via their relationships, such as:
  User.bank_account.title,
  User.full_name

{resolver.functionDefinition}
""",
        )


def _validate_resolver_output(resolver: UpsertResolverGQL, builder: _LogBuilder, lsp_builder: ResolverErrorBuilder):
    output = resolver.output
    features = output.features or []
    dataframes = output.dataframes or []
    if len(features) == 0 and len(dataframes) == 0:
        lsp_builder.add_diagnostic(
            message=f'Resolver "{resolver.fqn}" does not define outputs. All resolvers must have an output',
            code="132",
            range=lsp_builder.function_return_annotation(),
            label="invalid resolver output",
            code_href="https://docs.chalk.ai/docs/resolver-outputs",
        )
        builder.add_error(
            header=f'Resolver "{resolver.fqn}" does not define outputs.',
            subheader="See https://docs.chalk.ai/docs/resolver-outputs for information about valid resolver outputs.",
        )

    if len(dataframes) > 1:
        lsp_builder.add_diagnostic(
            message=f'Resolver "{resolver.fqn}" defines multiple DataFrames as output. At most one is permitted',
            code="133",
            range=lsp_builder.function_return_annotation(),
            label="invalid resolver output",
            code_href="https://docs.chalk.ai/docs/resolver-outputs",
        )
        builder.add_error(
            header=f'Resolver "{resolver.fqn}" defines multiple DataFrames as output.',
            subheader="See https://docs.chalk.ai/docs/resolver-outputs for information about valid resolver outputs.",
        )

    if len(features) > 0 and len(dataframes) > 0:
        lsp_builder.add_diagnostic(
            message=(
                f'Resolver "{resolver.fqn}" returns both relationships and scalar features. '
                f"Only one or the other is permitted."
            ),
            code="134",
            range=lsp_builder.function_return_annotation(),
            label="invalid resolver output",
            code_href="https://docs.chalk.ai/docs/resolver-outputs",
        )
        builder.add_error(
            header=f'Resolver "{resolver.fqn}" returns both relationships and scalar features.',
            subheader="See https://docs.chalk.ai/docs/resolver-outputs for information about valid resolver outputs.",
        )

    # Want to validate this but only have feature id instead of feature
    # if len(resolver.inputs) == 0 and len(dataframes) == 1 and len([pkey for pkey in dataframes[0].columns if pkey.primary]) != 1:
    #     builder.add_error(
    #         header=f'Resolver "{resolver.fqn}" must return a primary feature',
    #         subheader="See https://docs.chalk.ai/docs/resolver-outputs for information about valid resolver outputs.",
    #     )

    # Bring this back.


#     if len(features) > 0:
#         namespaces = list(set(f.namespace for f in features))
#         if len(namespaces) > 1:
#             builder.add_error(
#                 header=f'Resolver "{resolver.fqn}" outputs features from multiple namespaces.',
#                 subheader=f"""All outputs of a resolver should be rooted in the same namespace.
# The resolver "{resolver.fqn}" outputs features in the namespaces {oxford_comma_list(namespaces)}.
# See https://docs.chalk.ai/docs/resolver-outputs for information about valid resolver outputs.
#
# {resolver.functionDefinition}
# """,
#             )


# FIXME CHA-66 we should validate that joins are all pkey on pkey joins. no non-primary keys, no self-joins, no constants
def _validate_joins(feature: UpsertFeatureGQL, builder: _LogBuilder, lsp_builder: FeatureClassErrorBuilder):
    pass


def _validate_feature_names(feature: UpsertFeatureGQL, builder: _LogBuilder, lsp_builder: FeatureClassErrorBuilder):
    if feature.id.name.startswith("__") or feature.id.name.startswith("_chalk"):
        lsp_builder.add_diagnostic(
            message="Feature names cannot begin with '_chalk' or '__'.",
            range=lsp_builder.property_range(feature.id.attributeName),
            label="protected name",
            code="24",
        )
        builder.add_error(
            header="Feature uses protected name",
            subheader="Feature names cannot begin with '_chalk' or '__'.",
        )

    if feature.id.namespace.startswith("__") or feature.id.namespace.startswith("_chalk"):
        lsp_builder.add_diagnostic(
            message="Feature classes cannot have names that begin with '_chalk' or '__'.",
            label="protected namespace",
            range=lsp_builder.decorator_kwarg_value_range("name") or lsp_builder.class_definition_range(),
            code="25",
        )
        builder.add_error(
            header="Feature class uses protected namespace",
            subheader=(
                f'The feature "{feature.id.fqn}" belongs to the protected namespace "{feature.id.namespace}". '
                f'Feature namespaces cannot begin with "_chalk" or "__". Please rename this feature set.'
            ),
        )


def _validate_resolver_feature_cycles(
    fqn_to_feature: Mapping[str, UpsertFeatureGQL],
    resolver: UpsertResolverGQL,
    builder: _LogBuilder,
    lsp_builder: ResolverErrorBuilder,
):
    input_root_fqns: set[str] = set()
    for inp in resolver.inputs or []:
        if fqn_to_feature[inp.underlying.fqn].scalarKind and not fqn_to_feature[inp.underlying.fqn].scalarKind.primary:
            if not inp.path:
                input_root_fqns.add(inp.underlying.fqn)
            else:
                path_parsed: List[str] = []
                path_parsed.append(inp.path[0].parent.namespace)
                path_parsed.append(inp.path[0].parent.name)
                for x in inp.path:
                    path_parsed.append(x.child.name)
                input_root_fqns.add(".".join(path_parsed))
        # FIXME: Validate cycles for has-one and has-many features

    output_features = list(resolver.output.features or [])
    output_features += [f for df in resolver.output.dataframes for f in (df.columns or [])]
    output_fqns: set[str] = set()
    for f in output_features:
        fqn = f"{f.namespace}.{f.name}"
        root_fqn = f.fqn  # for output features, the fqn is the root fqn
        if fqn_to_feature[fqn].scalarKind is not None and not fqn_to_feature[fqn].scalarKind.primary:
            output_fqns.add(root_fqn)

    shared_features = output_fqns & input_root_fqns
    if len(shared_features) > 0:
        builder.add_error(
            header=f'Resolver "{resolver.fqn}" has the same feature in its input and output (i.e. a cycle).',
            subheader=f"""The inputs and outputs of a resolver can't contain the same exact feature.
The resolver "{resolver.fqn}" contains the following shared features in its inputs and outputs: {sorted(shared_features)}
""",
        )


def _validate_resolver_input_and_output_namespace(resolver: UpsertResolverGQL, builder: _LogBuilder):
    input_features = [i.underlying for i in (resolver.inputs or [])]
    output_features = resolver.output.features or []
    all_features = input_features + output_features
    all_namespaces = {f.namespace for f in all_features}
    if len(all_namespaces) > 1:
        builder.add_warning(
            header=f'Resolver "{resolver.fqn}" has output and input features from multiple namespaces.',
            subheader=f"""All outputs and inputs of a resolver should be rooted in the same namespace.
The resolver "{resolver.fqn}" references features in the namespaces {oxford_comma_list(sorted(all_namespaces))}.
See https://docs.chalk.ai/docs/resolver-outputs for information about valid resolver outputs.
""",
        )


MissingMetadata = Dict[GraphLogSeverity, List[str]]


def _validate_metadata(
    features: List[UpsertFeatureGQL],
    resolvers: List[UpsertResolverGQL],
    builder: _LogBuilder,
    request_config: Optional[ProjectSettingsGQL],
):
    class MissingMetadataFeature:
        def __init__(self, feature: UpsertFeatureGQL, missing_metadata: MissingMetadata):
            self.feature = feature
            self.missing_metadata = missing_metadata

    class MissingMetadataResolver:
        def __init__(self, resolver: UpsertResolverGQL, missing_metadata: MissingMetadata):
            self.resolver = resolver
            self.missing_metadata = missing_metadata

    def get_missing_metadata(
        entity: Union[UpsertFeatureGQL, UpsertResolverGQL],
        attribute_map: Dict[str, str],
        entity_type: Literal["feature", "resolver"],
    ) -> MissingMetadata:
        res: MissingMetadata = collections.defaultdict(list)
        if entity_type == "feature":
            settings = request_config.validation.feature.metadata
        elif entity_type == "resolver":
            settings = request_config.validation.resolver.metadata
        else:
            raise ValueError(f"Unrecognized type {entity_type}")
        for setting in settings:
            metadata_name = setting.name
            try:
                severity = GraphLogSeverity(setting.missing.upper())
            except:
                """If this fails, _validate_metadata_config should log the error"""
                continue
            if metadata_name in attribute_map:
                attribute_name = attribute_map[metadata_name]
                value = getattr(entity, attribute_name)
                is_missing = value is None or (isinstance(value, list) and len(value) == 0)
                if is_missing:
                    res[severity].append(metadata_name)
        return res

    def get_missing_metadata_features_log(
        missing_metadata_features: List[MissingMetadataFeature], severity: GraphLogSeverity
    ) -> Union[Tuple[str, str], None]:
        if not missing_metadata_features:
            return None

        missing_messages = []
        feature_str = "feature"
        missing_metadata_header_str = "missing metadata"
        max_name_len = max([len(w.feature.id.name) for w in missing_metadata_features])
        feature_column_width = max(max_name_len, len(feature_str)) + 1
        get_padding = lambda s: feature_column_width - len(s)

        first_feature = missing_metadata_features[0].feature
        header = f'"{to_camel_case(first_feature.id.namespace)}" features have missing metadata'
        subheader = f"  Filepath: {first_feature.namespacePath}\n\n"

        for wrapper in missing_metadata_features:
            missing_metadata = wrapper.missing_metadata.get(severity)
            if not missing_metadata:
                continue
            padding_1 = get_padding(wrapper.feature.id.name)
            missing_metadata_str = ", ".join(missing_metadata)
            missing_messages.append(f"      {wrapper.feature.id.name}{' ' * padding_1}: {missing_metadata_str}")

        if not missing_messages:
            return None

        padding_2 = get_padding(feature_str)
        subheader += f"      {'-' * len(feature_str)}{' ' * padding_2}  {'-' * len(missing_metadata_header_str)}\n"
        subheader += f"      {feature_str}{' ' * padding_2}  {missing_metadata_header_str}\n"
        subheader += f"      {'-' * len(feature_str)}{' ' * padding_2}  {'-' * len(missing_metadata_header_str)}\n"
        subheader += "\n".join(missing_messages)

        return header, subheader

    def get_missing_metadata_resolver_log(
        missing_metadata_resolver: MissingMetadataResolver, severity: GraphLogSeverity
    ) -> Union[Tuple[str, str], None]:
        missing_metadata = missing_metadata_resolver.missing_metadata.get(severity)
        if missing_metadata is None:
            return
        missing_metadata_str = ", ".join(missing_metadata)
        resolver_str = "resolver"
        missing_metadata_header_str = "missing metadata"
        resolver = missing_metadata_resolver.resolver
        max_name_len = len(resolver.fqn)
        feature_column_width = max(max_name_len, len(resolver_str)) + 1
        get_padding = lambda s: feature_column_width - len(s)
        padding_1 = get_padding(resolver.fqn)

        header = f'Resolver "{resolver.fqn}" has missing metadata'
        subheader = f"  Filepath: {missing_metadata_resolver.resolver.filename}\n\n"
        message = f"      {resolver.fqn}{' ' * padding_1}: {missing_metadata_str}"

        padding_2 = get_padding(resolver_str)
        subheader += f"      {'-' * len(resolver_str)}{' ' * padding_2}  {'-' * len(missing_metadata_header_str)}\n"
        subheader += f"      {resolver_str}{' ' * padding_2}  {missing_metadata_header_str}\n"
        subheader += f"      {'-' * len(resolver_str)}{' ' * padding_2}  {'-' * len(missing_metadata_header_str)}\n"
        subheader += message

        return header, subheader

    def build_feature_log_for_each_severity(missing_metadata_features: List[MissingMetadataFeature]):
        if not missing_metadata_features:
            return

        for severity in GraphLogSeverity:
            log_or_none = get_missing_metadata_features_log(
                missing_metadata_features=missing_metadata_features, severity=GraphLogSeverity(severity)
            )
            if log_or_none is None:
                continue
            header, subheader = log_or_none
            builder.add_log(header=header, subheader=subheader, severity=GraphLogSeverity(severity))

    def build_resolver_log_for_each_severity(missing_metadata_resolvers: List[MissingMetadataResolver]):
        if not missing_metadata_resolvers:
            return

        for severity in GraphLogSeverity:
            for resolver in missing_metadata_resolvers:
                log_or_none = get_missing_metadata_resolver_log(
                    missing_metadata_resolver=resolver, severity=GraphLogSeverity(severity)
                )
                if log_or_none is None:
                    continue
                header, subheader = log_or_none
                builder.add_log(header=header, subheader=subheader, severity=GraphLogSeverity(severity))

    def validate_feature_metadata(
        namespace_features: List[UpsertFeatureGQL],
    ) -> List[MissingMetadataFeature]:
        wrapped_features = []
        for nf in namespace_features:
            missing_metadata = get_missing_metadata(
                entity=nf,
                attribute_map=_METADATA_STRING_TO_FEATURE_ATTRIBUTE_MAP,
                entity_type="feature",
            )
            if not missing_metadata:
                continue
            wrapped_features.append(MissingMetadataFeature(feature=nf, missing_metadata=missing_metadata))

        return wrapped_features

    if not (request_config and request_config.validation):
        return

    if request_config.validation.feature and request_config.validation.feature.metadata:
        namespace_to_features = collections.defaultdict(list)
        for f in features:
            namespace_to_features[f.id.namespace].append(f)

        for ns_features in namespace_to_features.values():
            wf = validate_feature_metadata(namespace_features=ns_features)
            build_feature_log_for_each_severity(missing_metadata_features=wf)
    if request_config.validation.resolver and request_config.validation.resolver.metadata:
        missing_resolver_metadatas: List[MissingMetadataResolver] = []
        for r in resolvers:
            metadata = get_missing_metadata(r, _METADATA_STRING_TO_RESOLVER_ATTRIBUTE_MAP, "resolver")
            missing_resolver_metadatas.append(MissingMetadataResolver(resolver=r, missing_metadata=metadata))
        build_resolver_log_for_each_severity(missing_resolver_metadatas)


def _validate_metadata_config(
    builder: _LogBuilder,
    request_config: Optional[ProjectSettingsGQL],
):
    if not (request_config and request_config.validation):
        return

    severities_lower = [e.lower() for e in GraphLogSeverity]

    if request_config.validation.feature and request_config.validation.feature.metadata:
        for missing_metadata in request_config.validation.feature.metadata:
            metadata_name = missing_metadata.name
            severity = missing_metadata.missing

            severity_upper = severity.upper()
            try:
                GraphLogSeverity(severity_upper)
            except ValueError:
                severity_choices = '" or "'.join(severities_lower)
                builder.add_warning(
                    header=f'Found invalid log severity "{severity}" config for missing metadata',
                    subheader=(
                        f'The required feature metadata "{metadata_name}" is associated with an invalid log severity "{severity}".'
                        f' Please use "{severity_choices}" in chalk.yml'
                    ),
                )

            if metadata_name not in _METADATA_STRING_TO_FEATURE_ATTRIBUTE_MAP:
                builder.add_warning(
                    header=f'Found invalid feature metadata "{metadata_name}" in config',
                    subheader=(
                        f'The required metadata "{metadata_name}" is not a valid feature metadata.'
                        f" Please consider removing it from chalk.yml"
                    ),
                )
    if request_config.validation.resolver and request_config.validation.resolver.metadata:
        for missing_metadata in request_config.validation.resolver.metadata:
            metadata_name = missing_metadata.name
            severity = missing_metadata.missing

            severity_upper = severity.upper()
            try:
                GraphLogSeverity(severity_upper)
            except ValueError:
                severity_choices = '" or "'.join(severities_lower)
                builder.add_warning(
                    header=f'Found invalid log severity "{severity}" config for missing metadata',
                    subheader=(
                        f'The required feature metadata "{metadata_name}" is associated with an invalid log severity "{severity}".'
                        f' Please use "{severity_choices}" in chalk.yml'
                    ),
                )

            if metadata_name not in _METADATA_STRING_TO_RESOLVER_ATTRIBUTE_MAP:
                builder.add_warning(
                    header=f'Found invalid feature metadata "{metadata_name}" in config',
                    subheader=(
                        f'The required metadata "{metadata_name}" is not a valid feature metadata.'
                        f" Please consider removing it from chalk.yml"
                    ),
                )


def _validate_namespace_primary_key(
    namespace: str,
    features: List[UpsertFeatureGQL],
    builder: _LogBuilder,
    singleton_namespaces: set[str],
):
    if namespace in singleton_namespaces:
        return

    primary_features = list(f for f in features if f.scalarKind and f.scalarKind.primary)

    if len(primary_features) == 0:
        builder.add_error(
            header=f"Feature set '{namespace}' is missing a primary feature",
            subheader=f"Please add an 'int' or 'str' feature to '{namespace}', annotated with '= feature(primary=True)'",
        )
    elif len(primary_features) > 1:
        names = ", ".join([f.id.name for f in primary_features])
        builder.add_error(
            header=f"Feature set '{namespace}' has too many primary features",
            subheader=f"Found primary features: {names}. Composite primary keys are not supported. Please mark only a single feature as primary.",
        )


def validate_graph(request: UpsertGraphGQL) -> List[UpdateGraphError]:
    """Beware: errors here will only be acted upon `chalk apply --branch`.
    Regular deployments will have their graph errors acted upon by the server.
    """
    singleton_namespaces = {c.name for c in request.featureClasses or [] if c.isSingleton}

    namespaces: Dict[str, List[UpsertFeatureGQL]] = defaultdict(list)

    for feature in request.features or []:
        namespaces[feature.id.namespace].append(feature)

    builder = _LogBuilder()

    # Validate the features
    _validate_feature_names_unique(request.features or [], builder)
    _validate_metadata_config(builder, request.config)
    _validate_metadata(request.features or [], request.resolvers or [], builder, request.config)

    for namespace, features in namespaces.items():
        _validate_namespace_primary_key(
            namespace=namespace,
            features=features,
            builder=builder,
            singleton_namespaces=singleton_namespaces,
        )

    garbage_feature_builder = FeatureClassErrorBuilder(uri="garbage.py", namespace="garbage", node=None)
    for feature in request.features or []:
        lsp_builder = (
            FeatureSetBase.registry[feature.id.namespace].__chalk_error_builder__
            if feature.id.namespace in FeatureSetBase.registry and LSPErrorBuilder.lsp
            else garbage_feature_builder
        )
        _validate_primary_key(feature, builder, lsp_builder)
        _validate_max_staleness(feature, builder, lsp_builder)
        _validate_joins(feature, builder, lsp_builder)
        _validate_etl_to_online(feature, builder, lsp_builder)
        _validate_feature_names(feature, builder, lsp_builder)

    # Validate the resolvers
    fqn_to_feature = {f.id.fqn: f for f in request.features or []}

    _validate_resolver_names_unique(request.resolvers or [], builder)
    garbage_resolver_builder = ResolverErrorBuilder(fn=None)
    for resolver in request.resolvers or []:
        try:
            lsp_builder = garbage_resolver_builder
            if LSPErrorBuilder.lsp:
                maybe_resolver = RESOLVER_REGISTRY.get_resolver(resolver.fqn)
                if maybe_resolver is not None:
                    if maybe_resolver.is_sql_file_resolver:
                        continue
                    lsp_builder = maybe_resolver.lsp_builder
            _validate_resolver_input(
                singleton_namespaces=singleton_namespaces,
                resolver=resolver,
                builder=builder,
                lsp_builder=lsp_builder,
            )
            _validate_resolver_output(resolver, builder, lsp_builder)

            # TODO we still allow this
            # _validate_resolver_feature_cycles(fqn_to_feature=fqn_to_feature, resolver=resolver, builder=builder)

            # TODO Some customers currently still do stuff like:
            # >>> def some_resolver(uid: User.id) -> DataFrame[Transaction]: ....
            # So don't even warn about it
            # _validate_resolver_input_and_output_namespace(resolver, builder)

            _validate_no_feature_times_as_input(
                fqn_to_feature=fqn_to_feature, resolver=resolver, builder=builder, lsp_builder=lsp_builder
            )
        except Exception as e:
            err = traceback.format_exc()
            builder.add_error(
                header=f'Failed to validate resolver "{resolver.fqn}"',
                subheader=f"Please check the resolver for syntax errors.\nRaw error: {err}",
            )

    return builder.get_logs()

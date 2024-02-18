from typing import ClassVar as _ClassVar
from typing import Iterable as _Iterable
from typing import Mapping as _Mapping
from typing import Optional as _Optional
from typing import Union as _Union

from google.protobuf import descriptor as _descriptor
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import message as _message
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper

from chalk._gen.chalk.arrow.v1 import arrow_pb2 as _arrow_pb2
from chalk._gen.chalk.expression.v1 import expression_pb2 as _expression_pb2
from chalk._gen.chalk.graph.v1 import sources_pb2 as _sources_pb2

DESCRIPTOR: _descriptor.FileDescriptor

class ResolverKind(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RESOLVER_KIND_UNSPECIFIED: _ClassVar[ResolverKind]
    RESOLVER_KIND_ONLINE: _ClassVar[ResolverKind]
    RESOLVER_KIND_OFFLINE: _ClassVar[ResolverKind]

class WindowMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    WINDOW_MODE_UNSPECIFIED: _ClassVar[WindowMode]
    WINDOW_MODE_CONTINUOUS: _ClassVar[WindowMode]
    WINDOW_MODE_TUMBLING: _ClassVar[WindowMode]
    WINDOW_MODE_CDC: _ClassVar[WindowMode]

RESOLVER_KIND_UNSPECIFIED: ResolverKind
RESOLVER_KIND_ONLINE: ResolverKind
RESOLVER_KIND_OFFLINE: ResolverKind
WINDOW_MODE_UNSPECIFIED: WindowMode
WINDOW_MODE_CONTINUOUS: WindowMode
WINDOW_MODE_TUMBLING: WindowMode
WINDOW_MODE_CDC: WindowMode

class Graph(_message.Message):
    __slots__ = (
        "feature_sets",
        "resolvers",
        "stream_resolvers",
        "sink_resolvers",
        "database_sources",
        "stream_sources",
    )
    FEATURE_SETS_FIELD_NUMBER: _ClassVar[int]
    RESOLVERS_FIELD_NUMBER: _ClassVar[int]
    STREAM_RESOLVERS_FIELD_NUMBER: _ClassVar[int]
    SINK_RESOLVERS_FIELD_NUMBER: _ClassVar[int]
    DATABASE_SOURCES_FIELD_NUMBER: _ClassVar[int]
    STREAM_SOURCES_FIELD_NUMBER: _ClassVar[int]
    feature_sets: _containers.RepeatedCompositeFieldContainer[FeatureSet]
    resolvers: _containers.RepeatedCompositeFieldContainer[Resolver]
    stream_resolvers: _containers.RepeatedCompositeFieldContainer[StreamResolver]
    sink_resolvers: _containers.RepeatedCompositeFieldContainer[SinkResolver]
    database_sources: _containers.RepeatedCompositeFieldContainer[_sources_pb2.DatabaseSource]
    stream_sources: _containers.RepeatedCompositeFieldContainer[_sources_pb2.StreamSource]
    def __init__(
        self,
        feature_sets: _Optional[_Iterable[_Union[FeatureSet, _Mapping]]] = ...,
        resolvers: _Optional[_Iterable[_Union[Resolver, _Mapping]]] = ...,
        stream_resolvers: _Optional[_Iterable[_Union[StreamResolver, _Mapping]]] = ...,
        sink_resolvers: _Optional[_Iterable[_Union[SinkResolver, _Mapping]]] = ...,
        database_sources: _Optional[_Iterable[_Union[_sources_pb2.DatabaseSource, _Mapping]]] = ...,
        stream_sources: _Optional[_Iterable[_Union[_sources_pb2.StreamSource, _Mapping]]] = ...,
    ) -> None: ...

class FeatureSet(_message.Message):
    __slots__ = (
        "name",
        "features",
        "max_staleness_duration",
        "is_singleton",
        "tags",
        "owner",
        "doc",
        "etl_offline_to_online",
    )
    NAME_FIELD_NUMBER: _ClassVar[int]
    FEATURES_FIELD_NUMBER: _ClassVar[int]
    MAX_STALENESS_DURATION_FIELD_NUMBER: _ClassVar[int]
    IS_SINGLETON_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    DOC_FIELD_NUMBER: _ClassVar[int]
    ETL_OFFLINE_TO_ONLINE_FIELD_NUMBER: _ClassVar[int]
    name: str
    features: _containers.RepeatedCompositeFieldContainer[FeatureType]
    max_staleness_duration: _duration_pb2.Duration
    is_singleton: bool
    tags: _containers.RepeatedScalarFieldContainer[str]
    owner: str
    doc: str
    etl_offline_to_online: bool
    def __init__(
        self,
        name: _Optional[str] = ...,
        features: _Optional[_Iterable[_Union[FeatureType, _Mapping]]] = ...,
        max_staleness_duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...,
        is_singleton: bool = ...,
        tags: _Optional[_Iterable[str]] = ...,
        owner: _Optional[str] = ...,
        doc: _Optional[str] = ...,
        etl_offline_to_online: bool = ...,
    ) -> None: ...

class FeatureType(_message.Message):
    __slots__ = ("scalar", "has_one", "has_many", "feature_time", "windowed")
    SCALAR_FIELD_NUMBER: _ClassVar[int]
    HAS_ONE_FIELD_NUMBER: _ClassVar[int]
    HAS_MANY_FIELD_NUMBER: _ClassVar[int]
    FEATURE_TIME_FIELD_NUMBER: _ClassVar[int]
    WINDOWED_FIELD_NUMBER: _ClassVar[int]
    scalar: ScalarFeatureType
    has_one: HasOneFeatureType
    has_many: HasManyFeatureType
    feature_time: FeatureTimeFeatureType
    windowed: WindowedFeatureType
    def __init__(
        self,
        scalar: _Optional[_Union[ScalarFeatureType, _Mapping]] = ...,
        has_one: _Optional[_Union[HasOneFeatureType, _Mapping]] = ...,
        has_many: _Optional[_Union[HasManyFeatureType, _Mapping]] = ...,
        feature_time: _Optional[_Union[FeatureTimeFeatureType, _Mapping]] = ...,
        windowed: _Optional[_Union[WindowedFeatureType, _Mapping]] = ...,
    ) -> None: ...

class FeatureReference(_message.Message):
    __slots__ = ("name", "namespace", "path", "df")
    NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    DF_FIELD_NUMBER: _ClassVar[int]
    name: str
    namespace: str
    path: _containers.RepeatedCompositeFieldContainer[FeatureReference]
    df: DataFrameType
    def __init__(
        self,
        name: _Optional[str] = ...,
        namespace: _Optional[str] = ...,
        path: _Optional[_Iterable[_Union[FeatureReference, _Mapping]]] = ...,
        df: _Optional[_Union[DataFrameType, _Mapping]] = ...,
    ) -> None: ...

class DataFrameType(_message.Message):
    __slots__ = (
        "root_namespace",
        "required_columns",
        "optional_columns",
        "filter",
        "limit",
    )
    ROOT_NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_COLUMNS_FIELD_NUMBER: _ClassVar[int]
    OPTIONAL_COLUMNS_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    root_namespace: str
    required_columns: _containers.RepeatedCompositeFieldContainer[FeatureReference]
    optional_columns: _containers.RepeatedCompositeFieldContainer[FeatureReference]
    filter: _expression_pb2.LogicalExprNode
    limit: int
    def __init__(
        self,
        root_namespace: _Optional[str] = ...,
        required_columns: _Optional[_Iterable[_Union[FeatureReference, _Mapping]]] = ...,
        optional_columns: _Optional[_Iterable[_Union[FeatureReference, _Mapping]]] = ...,
        filter: _Optional[_Union[_expression_pb2.LogicalExprNode, _Mapping]] = ...,
        limit: _Optional[int] = ...,
    ) -> None: ...

class ScalarFeatureType(_message.Message):
    __slots__ = (
        "name",
        "namespace",
        "is_autogenerated",
        "no_display",
        "is_primary",
        "is_nullable",
        "internal_version",
        "max_staleness_duration",
        "offline_ttl_duration",
        "arrow_type",
        "version",
        "window_info",
        "default_value",
        "tags",
        "description",
        "owner",
        "expression",
        "validations",
        "last_for",
        "etl_offline_to_online",
        "is_distance_pseudofeature",
    )
    NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    IS_AUTOGENERATED_FIELD_NUMBER: _ClassVar[int]
    NO_DISPLAY_FIELD_NUMBER: _ClassVar[int]
    IS_PRIMARY_FIELD_NUMBER: _ClassVar[int]
    IS_NULLABLE_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_VERSION_FIELD_NUMBER: _ClassVar[int]
    MAX_STALENESS_DURATION_FIELD_NUMBER: _ClassVar[int]
    OFFLINE_TTL_DURATION_FIELD_NUMBER: _ClassVar[int]
    ARROW_TYPE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    WINDOW_INFO_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    VALIDATIONS_FIELD_NUMBER: _ClassVar[int]
    LAST_FOR_FIELD_NUMBER: _ClassVar[int]
    ETL_OFFLINE_TO_ONLINE_FIELD_NUMBER: _ClassVar[int]
    IS_DISTANCE_PSEUDOFEATURE_FIELD_NUMBER: _ClassVar[int]
    name: str
    namespace: str
    is_autogenerated: bool
    no_display: bool
    is_primary: bool
    is_nullable: bool
    internal_version: int
    max_staleness_duration: _duration_pb2.Duration
    offline_ttl_duration: _duration_pb2.Duration
    arrow_type: _arrow_pb2.ArrowType
    version: VersionInfo
    window_info: WindowInfo
    default_value: _arrow_pb2.ScalarValue
    tags: _containers.RepeatedScalarFieldContainer[str]
    description: str
    owner: str
    expression: _expression_pb2.LogicalExprNode
    validations: _containers.RepeatedCompositeFieldContainer[FeatureValidation]
    last_for: FeatureReference
    etl_offline_to_online: bool
    is_distance_pseudofeature: bool
    def __init__(
        self,
        name: _Optional[str] = ...,
        namespace: _Optional[str] = ...,
        is_autogenerated: bool = ...,
        no_display: bool = ...,
        is_primary: bool = ...,
        is_nullable: bool = ...,
        internal_version: _Optional[int] = ...,
        max_staleness_duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...,
        offline_ttl_duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...,
        arrow_type: _Optional[_Union[_arrow_pb2.ArrowType, _Mapping]] = ...,
        version: _Optional[_Union[VersionInfo, _Mapping]] = ...,
        window_info: _Optional[_Union[WindowInfo, _Mapping]] = ...,
        default_value: _Optional[_Union[_arrow_pb2.ScalarValue, _Mapping]] = ...,
        tags: _Optional[_Iterable[str]] = ...,
        description: _Optional[str] = ...,
        owner: _Optional[str] = ...,
        expression: _Optional[_Union[_expression_pb2.LogicalExprNode, _Mapping]] = ...,
        validations: _Optional[_Iterable[_Union[FeatureValidation, _Mapping]]] = ...,
        last_for: _Optional[_Union[FeatureReference, _Mapping]] = ...,
        etl_offline_to_online: bool = ...,
        is_distance_pseudofeature: bool = ...,
    ) -> None: ...

class HasOneFeatureType(_message.Message):
    __slots__ = (
        "name",
        "namespace",
        "foreign_namespace",
        "join",
        "is_nullable",
        "is_autogenerated",
    )
    NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    FOREIGN_NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    JOIN_FIELD_NUMBER: _ClassVar[int]
    IS_NULLABLE_FIELD_NUMBER: _ClassVar[int]
    IS_AUTOGENERATED_FIELD_NUMBER: _ClassVar[int]
    name: str
    namespace: str
    foreign_namespace: str
    join: _expression_pb2.LogicalExprNode
    is_nullable: bool
    is_autogenerated: bool
    def __init__(
        self,
        name: _Optional[str] = ...,
        namespace: _Optional[str] = ...,
        foreign_namespace: _Optional[str] = ...,
        join: _Optional[_Union[_expression_pb2.LogicalExprNode, _Mapping]] = ...,
        is_nullable: bool = ...,
        is_autogenerated: bool = ...,
    ) -> None: ...

class HasManyFeatureType(_message.Message):
    __slots__ = (
        "name",
        "namespace",
        "foreign_namespace",
        "join",
        "is_autogenerated",
        "max_staleness_duration",
    )
    NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    FOREIGN_NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    JOIN_FIELD_NUMBER: _ClassVar[int]
    IS_AUTOGENERATED_FIELD_NUMBER: _ClassVar[int]
    MAX_STALENESS_DURATION_FIELD_NUMBER: _ClassVar[int]
    name: str
    namespace: str
    foreign_namespace: str
    join: _expression_pb2.LogicalExprNode
    is_autogenerated: bool
    max_staleness_duration: _duration_pb2.Duration
    def __init__(
        self,
        name: _Optional[str] = ...,
        namespace: _Optional[str] = ...,
        foreign_namespace: _Optional[str] = ...,
        join: _Optional[_Union[_expression_pb2.LogicalExprNode, _Mapping]] = ...,
        is_autogenerated: bool = ...,
        max_staleness_duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...,
    ) -> None: ...

class FeatureTimeFeatureType(_message.Message):
    __slots__ = ("name", "namespace", "is_autogenerated")
    NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    IS_AUTOGENERATED_FIELD_NUMBER: _ClassVar[int]
    name: str
    namespace: str
    is_autogenerated: bool
    def __init__(
        self,
        name: _Optional[str] = ...,
        namespace: _Optional[str] = ...,
        is_autogenerated: bool = ...,
    ) -> None: ...

class WindowedFeatureType(_message.Message):
    __slots__ = ("name", "namespace", "is_autogenerated", "window_durations")
    NAME_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    IS_AUTOGENERATED_FIELD_NUMBER: _ClassVar[int]
    WINDOW_DURATIONS_FIELD_NUMBER: _ClassVar[int]
    name: str
    namespace: str
    is_autogenerated: bool
    window_durations: _containers.RepeatedCompositeFieldContainer[_duration_pb2.Duration]
    def __init__(
        self,
        name: _Optional[str] = ...,
        namespace: _Optional[str] = ...,
        is_autogenerated: bool = ...,
        window_durations: _Optional[_Iterable[_Union[_duration_pb2.Duration, _Mapping]]] = ...,
    ) -> None: ...

class WindowInfo(_message.Message):
    __slots__ = ("duration",)
    DURATION_FIELD_NUMBER: _ClassVar[int]
    duration: _duration_pb2.Duration
    def __init__(self, duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class FeatureInput(_message.Message):
    __slots__ = ("feature", "default_value")
    FEATURE_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_VALUE_FIELD_NUMBER: _ClassVar[int]
    feature: FeatureReference
    default_value: _arrow_pb2.ScalarValue
    def __init__(
        self,
        feature: _Optional[_Union[FeatureReference, _Mapping]] = ...,
        default_value: _Optional[_Union[_arrow_pb2.ScalarValue, _Mapping]] = ...,
    ) -> None: ...

class ResolverInput(_message.Message):
    __slots__ = ("feature", "df", "state")
    FEATURE_FIELD_NUMBER: _ClassVar[int]
    DF_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    feature: FeatureInput
    df: DataFrameType
    state: ResolverState
    def __init__(
        self,
        feature: _Optional[_Union[FeatureInput, _Mapping]] = ...,
        df: _Optional[_Union[DataFrameType, _Mapping]] = ...,
        state: _Optional[_Union[ResolverState, _Mapping]] = ...,
    ) -> None: ...

class ResolverOutput(_message.Message):
    __slots__ = ("feature", "df")
    FEATURE_FIELD_NUMBER: _ClassVar[int]
    DF_FIELD_NUMBER: _ClassVar[int]
    feature: FeatureReference
    df: DataFrameType
    def __init__(
        self,
        feature: _Optional[_Union[FeatureReference, _Mapping]] = ...,
        df: _Optional[_Union[DataFrameType, _Mapping]] = ...,
    ) -> None: ...

class Resolver(_message.Message):
    __slots__ = (
        "fqn",
        "kind",
        "inputs",
        "outputs",
        "is_generator",
        "data_sources",
        "machine_type",
        "tags",
        "owner",
        "doc",
        "environments",
        "timeout_duration",
        "schedule",
        "when",
        "cron_filter",
        "function",
    )
    FQN_FIELD_NUMBER: _ClassVar[int]
    KIND_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    IS_GENERATOR_FIELD_NUMBER: _ClassVar[int]
    DATA_SOURCES_FIELD_NUMBER: _ClassVar[int]
    MACHINE_TYPE_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    DOC_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENTS_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_DURATION_FIELD_NUMBER: _ClassVar[int]
    SCHEDULE_FIELD_NUMBER: _ClassVar[int]
    WHEN_FIELD_NUMBER: _ClassVar[int]
    CRON_FILTER_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_FIELD_NUMBER: _ClassVar[int]
    fqn: str
    kind: ResolverKind
    inputs: _containers.RepeatedCompositeFieldContainer[ResolverInput]
    outputs: _containers.RepeatedCompositeFieldContainer[ResolverOutput]
    is_generator: bool
    data_sources: _containers.RepeatedCompositeFieldContainer[_sources_pb2.DatabaseSourceReference]
    machine_type: str
    tags: _containers.RepeatedScalarFieldContainer[str]
    owner: str
    doc: str
    environments: _containers.RepeatedScalarFieldContainer[str]
    timeout_duration: _duration_pb2.Duration
    schedule: Schedule
    when: _expression_pb2.LogicalExprNode
    cron_filter: CronFilterWithFeatureArgs
    function: FunctionReference
    def __init__(
        self,
        fqn: _Optional[str] = ...,
        kind: _Optional[_Union[ResolverKind, str]] = ...,
        inputs: _Optional[_Iterable[_Union[ResolverInput, _Mapping]]] = ...,
        outputs: _Optional[_Iterable[_Union[ResolverOutput, _Mapping]]] = ...,
        is_generator: bool = ...,
        data_sources: _Optional[_Iterable[_Union[_sources_pb2.DatabaseSourceReference, _Mapping]]] = ...,
        machine_type: _Optional[str] = ...,
        tags: _Optional[_Iterable[str]] = ...,
        owner: _Optional[str] = ...,
        doc: _Optional[str] = ...,
        environments: _Optional[_Iterable[str]] = ...,
        timeout_duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...,
        schedule: _Optional[_Union[Schedule, _Mapping]] = ...,
        when: _Optional[_Union[_expression_pb2.LogicalExprNode, _Mapping]] = ...,
        cron_filter: _Optional[_Union[CronFilterWithFeatureArgs, _Mapping]] = ...,
        function: _Optional[_Union[FunctionReference, _Mapping]] = ...,
    ) -> None: ...

class SinkResolver(_message.Message):
    __slots__ = (
        "fqn",
        "inputs",
        "buffer_size",
        "debounce_duration",
        "max_delay_duration",
        "upsert",
        "stream_source",
        "database_source",
        "machine_type",
        "doc",
        "owner",
        "environments",
        "timeout_duration",
        "function",
    )
    FQN_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    BUFFER_SIZE_FIELD_NUMBER: _ClassVar[int]
    DEBOUNCE_DURATION_FIELD_NUMBER: _ClassVar[int]
    MAX_DELAY_DURATION_FIELD_NUMBER: _ClassVar[int]
    UPSERT_FIELD_NUMBER: _ClassVar[int]
    STREAM_SOURCE_FIELD_NUMBER: _ClassVar[int]
    DATABASE_SOURCE_FIELD_NUMBER: _ClassVar[int]
    MACHINE_TYPE_FIELD_NUMBER: _ClassVar[int]
    DOC_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENTS_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_DURATION_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_FIELD_NUMBER: _ClassVar[int]
    fqn: str
    inputs: _containers.RepeatedCompositeFieldContainer[ResolverInput]
    buffer_size: int
    debounce_duration: _duration_pb2.Duration
    max_delay_duration: _duration_pb2.Duration
    upsert: bool
    stream_source: _sources_pb2.StreamSourceReference
    database_source: _sources_pb2.DatabaseSourceReference
    machine_type: str
    doc: str
    owner: str
    environments: _containers.RepeatedScalarFieldContainer[str]
    timeout_duration: _duration_pb2.Duration
    function: FunctionReference
    def __init__(
        self,
        fqn: _Optional[str] = ...,
        inputs: _Optional[_Iterable[_Union[ResolverInput, _Mapping]]] = ...,
        buffer_size: _Optional[int] = ...,
        debounce_duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...,
        max_delay_duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...,
        upsert: bool = ...,
        stream_source: _Optional[_Union[_sources_pb2.StreamSourceReference, _Mapping]] = ...,
        database_source: _Optional[_Union[_sources_pb2.DatabaseSourceReference, _Mapping]] = ...,
        machine_type: _Optional[str] = ...,
        doc: _Optional[str] = ...,
        owner: _Optional[str] = ...,
        environments: _Optional[_Iterable[str]] = ...,
        timeout_duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...,
        function: _Optional[_Union[FunctionReference, _Mapping]] = ...,
    ) -> None: ...

class ParseInfo(_message.Message):
    __slots__ = (
        "parse_function",
        "parse_function_input_type",
        "parse_function_output_type",
        "is_parse_function_output_optional",
    )
    PARSE_FUNCTION_FIELD_NUMBER: _ClassVar[int]
    PARSE_FUNCTION_INPUT_TYPE_FIELD_NUMBER: _ClassVar[int]
    PARSE_FUNCTION_OUTPUT_TYPE_FIELD_NUMBER: _ClassVar[int]
    IS_PARSE_FUNCTION_OUTPUT_OPTIONAL_FIELD_NUMBER: _ClassVar[int]
    parse_function: FunctionReference
    parse_function_input_type: _arrow_pb2.ArrowType
    parse_function_output_type: _arrow_pb2.ArrowType
    is_parse_function_output_optional: bool
    def __init__(
        self,
        parse_function: _Optional[_Union[FunctionReference, _Mapping]] = ...,
        parse_function_input_type: _Optional[_Union[_arrow_pb2.ArrowType, _Mapping]] = ...,
        parse_function_output_type: _Optional[_Union[_arrow_pb2.ArrowType, _Mapping]] = ...,
        is_parse_function_output_optional: bool = ...,
    ) -> None: ...

class StreamResolver(_message.Message):
    __slots__ = (
        "fqn",
        "params",
        "outputs",
        "explicit_schema",
        "keys",
        "source",
        "parse_info",
        "mode",
        "environments",
        "timeout_duration",
        "timestamp_attribute_name",
        "owner",
        "doc",
        "machine_type",
        "function",
    )
    FQN_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    EXPLICIT_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    KEYS_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    PARSE_INFO_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENTS_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_DURATION_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_ATTRIBUTE_NAME_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    DOC_FIELD_NUMBER: _ClassVar[int]
    MACHINE_TYPE_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_FIELD_NUMBER: _ClassVar[int]
    fqn: str
    params: _containers.RepeatedCompositeFieldContainer[StreamResolverParam]
    outputs: _containers.RepeatedCompositeFieldContainer[ResolverOutput]
    explicit_schema: _arrow_pb2.ArrowType
    keys: _containers.RepeatedCompositeFieldContainer[StreamKey]
    source: _sources_pb2.StreamSourceReference
    parse_info: ParseInfo
    mode: WindowMode
    environments: _containers.RepeatedScalarFieldContainer[str]
    timeout_duration: _duration_pb2.Duration
    timestamp_attribute_name: str
    owner: str
    doc: str
    machine_type: str
    function: FunctionReference
    def __init__(
        self,
        fqn: _Optional[str] = ...,
        params: _Optional[_Iterable[_Union[StreamResolverParam, _Mapping]]] = ...,
        outputs: _Optional[_Iterable[_Union[ResolverOutput, _Mapping]]] = ...,
        explicit_schema: _Optional[_Union[_arrow_pb2.ArrowType, _Mapping]] = ...,
        keys: _Optional[_Iterable[_Union[StreamKey, _Mapping]]] = ...,
        source: _Optional[_Union[_sources_pb2.StreamSourceReference, _Mapping]] = ...,
        parse_info: _Optional[_Union[ParseInfo, _Mapping]] = ...,
        mode: _Optional[_Union[WindowMode, str]] = ...,
        environments: _Optional[_Iterable[str]] = ...,
        timeout_duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...,
        timestamp_attribute_name: _Optional[str] = ...,
        owner: _Optional[str] = ...,
        doc: _Optional[str] = ...,
        machine_type: _Optional[str] = ...,
        function: _Optional[_Union[FunctionReference, _Mapping]] = ...,
    ) -> None: ...

class ResolverState(_message.Message):
    __slots__ = ("initial", "arrow_type")
    INITIAL_FIELD_NUMBER: _ClassVar[int]
    ARROW_TYPE_FIELD_NUMBER: _ClassVar[int]
    initial: _arrow_pb2.ScalarValue
    arrow_type: _arrow_pb2.ArrowType
    def __init__(
        self,
        initial: _Optional[_Union[_arrow_pb2.ScalarValue, _Mapping]] = ...,
        arrow_type: _Optional[_Union[_arrow_pb2.ArrowType, _Mapping]] = ...,
    ) -> None: ...

class StreamResolverParam(_message.Message):
    __slots__ = ("message", "message_window", "state")
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_WINDOW_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    message: StreamResolverParamMessage
    message_window: StreamResolverParamMessageWindow
    state: ResolverState
    def __init__(
        self,
        message: _Optional[_Union[StreamResolverParamMessage, _Mapping]] = ...,
        message_window: _Optional[_Union[StreamResolverParamMessageWindow, _Mapping]] = ...,
        state: _Optional[_Union[ResolverState, _Mapping]] = ...,
    ) -> None: ...

class StreamResolverParamMessageWindow(_message.Message):
    __slots__ = ("name", "arrow_type")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ARROW_TYPE_FIELD_NUMBER: _ClassVar[int]
    name: str
    arrow_type: _arrow_pb2.ArrowType
    def __init__(
        self,
        name: _Optional[str] = ...,
        arrow_type: _Optional[_Union[_arrow_pb2.ArrowType, _Mapping]] = ...,
    ) -> None: ...

class StreamResolverParamMessage(_message.Message):
    __slots__ = ("name", "arrow_type")
    NAME_FIELD_NUMBER: _ClassVar[int]
    ARROW_TYPE_FIELD_NUMBER: _ClassVar[int]
    name: str
    arrow_type: _arrow_pb2.ArrowType
    def __init__(
        self,
        name: _Optional[str] = ...,
        arrow_type: _Optional[_Union[_arrow_pb2.ArrowType, _Mapping]] = ...,
    ) -> None: ...

class FunctionReference(_message.Message):
    __slots__ = ("name", "module", "file_name", "function_definition")
    NAME_FIELD_NUMBER: _ClassVar[int]
    MODULE_FIELD_NUMBER: _ClassVar[int]
    FILE_NAME_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_DEFINITION_FIELD_NUMBER: _ClassVar[int]
    name: str
    module: str
    file_name: str
    function_definition: str
    def __init__(
        self,
        name: _Optional[str] = ...,
        module: _Optional[str] = ...,
        file_name: _Optional[str] = ...,
        function_definition: _Optional[str] = ...,
    ) -> None: ...

class StreamKey(_message.Message):
    __slots__ = ("key", "feature")
    KEY_FIELD_NUMBER: _ClassVar[int]
    FEATURE_FIELD_NUMBER: _ClassVar[int]
    key: str
    feature: FeatureReference
    def __init__(
        self,
        key: _Optional[str] = ...,
        feature: _Optional[_Union[FeatureReference, _Mapping]] = ...,
    ) -> None: ...

class CronFilterWithFeatureArgs(_message.Message):
    __slots__ = ("filter", "args")
    FILTER_FIELD_NUMBER: _ClassVar[int]
    ARGS_FIELD_NUMBER: _ClassVar[int]
    filter: FunctionReference
    args: _containers.RepeatedCompositeFieldContainer[FeatureReference]
    def __init__(
        self,
        filter: _Optional[_Union[FunctionReference, _Mapping]] = ...,
        args: _Optional[_Iterable[_Union[FeatureReference, _Mapping]]] = ...,
    ) -> None: ...

class Schedule(_message.Message):
    __slots__ = ("crontab", "duration", "filter", "sample")
    CRONTAB_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    FILTER_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_FIELD_NUMBER: _ClassVar[int]
    crontab: str
    duration: _duration_pb2.Duration
    filter: FunctionReference
    sample: FunctionReference
    def __init__(
        self,
        crontab: _Optional[str] = ...,
        duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...,
        filter: _Optional[_Union[FunctionReference, _Mapping]] = ...,
        sample: _Optional[_Union[FunctionReference, _Mapping]] = ...,
    ) -> None: ...

class FeatureValidation(_message.Message):
    __slots__ = ("min", "max", "min_length", "max_length", "strict")
    MIN_FIELD_NUMBER: _ClassVar[int]
    MAX_FIELD_NUMBER: _ClassVar[int]
    MIN_LENGTH_FIELD_NUMBER: _ClassVar[int]
    MAX_LENGTH_FIELD_NUMBER: _ClassVar[int]
    STRICT_FIELD_NUMBER: _ClassVar[int]
    min: float
    max: float
    min_length: int
    max_length: int
    strict: bool
    def __init__(
        self,
        min: _Optional[float] = ...,
        max: _Optional[float] = ...,
        min_length: _Optional[int] = ...,
        max_length: _Optional[int] = ...,
        strict: bool = ...,
    ) -> None: ...

class VersionInfo(_message.Message):
    __slots__ = ("default", "maximum")
    DEFAULT_FIELD_NUMBER: _ClassVar[int]
    MAXIMUM_FIELD_NUMBER: _ClassVar[int]
    default: int
    maximum: int
    def __init__(self, default: _Optional[int] = ..., maximum: _Optional[int] = ...) -> None: ...

class StrictValidation(_message.Message):
    __slots__ = ("feature", "validations")
    FEATURE_FIELD_NUMBER: _ClassVar[int]
    VALIDATIONS_FIELD_NUMBER: _ClassVar[int]
    feature: FeatureReference
    validations: _containers.RepeatedCompositeFieldContainer[FeatureValidation]
    def __init__(
        self,
        feature: _Optional[_Union[FeatureReference, _Mapping]] = ...,
        validations: _Optional[_Iterable[_Union[FeatureValidation, _Mapping]]] = ...,
    ) -> None: ...

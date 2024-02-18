import collections
import inspect
import json
from datetime import timedelta
from typing import Any, Callable, ClassVar, Dict, List, Optional, Sequence, Set, Tuple, Type, Union, cast

import pyarrow as pa
from pydantic import BaseModel

from chalk import DataFrame
from chalk._gen.chalk.arrow.v1 import arrow_pb2 as arrow_pb
from chalk._gen.chalk.expression.v1 import expression_pb2 as expr_pb
from chalk._gen.chalk.graph.v1 import graph_pb2 as pb
from chalk._gen.chalk.graph.v1 import sources_pb2 as sources_pb
from chalk._gen.chalk.graph.v1.graph_pb2 import CronFilterWithFeatureArgs
from chalk._validation.feature_validation import FeatureValidation
from chalk.features import (
    Feature,
    FeatureConverter,
    Features,
    FeatureWrapper,
    Filter,
    TimeDelta,
    TPrimitive,
    Underscore,
    ensure_feature,
)
from chalk.features._encoding.rich import TRich
from chalk.features.pseudofeatures import PSEUDONAMESPACE
from chalk.features.resolver import (
    Cron,
    OfflineResolver,
    OnlineResolver,
    Resolver,
    ResolverArgErrorHandler,
    ResolverRegistry,
    SinkResolver,
    StateDescriptor,
    StreamResolver,
)
from chalk.features.underscore import (
    UnderscoreAttr,
    UnderscoreBinaryOp,
    UnderscoreCall,
    UnderscoreItem,
    UnderscoreRoot,
    UnderscoreUnaryOp,
)
from chalk.parsed.expressions import is_valid_operation
from chalk.parsed.utils import convert_raw_duration, seconds_to_proto_duration, timedelta_to_proto_duration
from chalk.sql import (
    BigQuerySourceImpl,
    CloudSQLSourceImpl,
    DatabricksSourceImpl,
    MySQLSourceImpl,
    PostgreSQLSourceImpl,
    RedshiftSourceImpl,
    SnowflakeSourceImpl,
    SQLiteSourceImpl,
)
from chalk.sql._internal.sql_source import BaseSQLSource
from chalk.streams import KafkaSource, KinesisSource, StreamSource
from chalk.streams.types import (
    StreamResolverParam,
    StreamResolverParamKeyedState,
    StreamResolverParamMessage,
    StreamResolverParamMessageWindow,
)
from chalk.utils.collections import get_unique_item
from chalk.utils.duration import CronTab, Duration, parse_chalk_duration


class ToProtoConverter:
    _agg_to_protobuf: ClassVar[Dict[str, int]] = {
        "sum": expr_pb.AGGREGATE_FUNCTION_SUM,
        "max": expr_pb.AGGREGATE_FUNCTION_MAX,
        "min": expr_pb.AGGREGATE_FUNCTION_MIN,
        "median": expr_pb.AGGREGATE_FUNCTION_MEDIAN,
        "mean": expr_pb.AGGREGATE_FUNCTION_AVG,
        "std": expr_pb.AGGREGATE_FUNCTION_STDDEV,
        "variance": expr_pb.AGGREGATE_FUNCTION_VARIANCE,
        "count": expr_pb.AGGREGATE_FUNCTION_COUNT,
        "last": expr_pb.AGGREGATE_FUNCTION_LAST_VALUE,
        "first": expr_pb.AGGREGATE_FUNCTION_FIRST_VALUE,
        # "product": expr_pb.AGGREGATE_FUNCTION_PRODUCT,
    }
    _arg_taking_aggs: ClassVar[Set[str]] = {
        "concat",
        "concat_str",
        "quantile",
    }
    _mode_to_enum: ClassVar[Dict[str, int]] = {
        "tumbling": pb.WINDOW_MODE_TUMBLING,
        "continuous": pb.WINDOW_MODE_CONTINUOUS,
        "cdc": pb.WINDOW_MODE_CDC,
    }
    _supported_stream_source_types: ClassVar[Tuple[Type[StreamSource], ...]] = (KafkaSource, KinesisSource)
    _supported_db_source_types: ClassVar[Tuple[Type[BaseSQLSource], ...]] = (
        BigQuerySourceImpl,
        CloudSQLSourceImpl,
        DatabricksSourceImpl,
        MySQLSourceImpl,
        PostgreSQLSourceImpl,
        RedshiftSourceImpl,
        SnowflakeSourceImpl,
        SQLiteSourceImpl,
    )

    @staticmethod
    def convert_underscore(underscore: Union[Underscore, TPrimitive]) -> expr_pb.LogicalExprNode:
        if not isinstance(underscore, Underscore):
            converter = FeatureConverter(name="helper", is_nullable=False, rich_type=type(underscore))
            return expr_pb.LogicalExprNode(literal=converter.from_rich_to_protobuf(underscore))
        if isinstance(underscore, UnderscoreRoot):
            return expr_pb.LogicalExprNode(column=expr_pb.Column(name="_"))
        if isinstance(underscore, UnderscoreAttr):
            parent_operand = ToProtoConverter.convert_underscore(underscore._chalk__parent)
            current_operand = expr_pb.LogicalExprNode(
                column=expr_pb.Column(name=underscore._chalk__attr, relation=expr_pb.ColumnRelation(relation="_"))
            )
            return expr_pb.LogicalExprNode(
                binary_expr=expr_pb.BinaryExprNode(operands=[parent_operand, current_operand], op="attr")
            )
        if isinstance(underscore, UnderscoreItem):
            parent_operand = ToProtoConverter.convert_underscore(underscore._chalk__parent)
            key = expr_pb.ListIndex(key=ToProtoConverter.convert_underscore(underscore._chalk__key))
            return expr_pb.LogicalExprNode(
                get_indexed_field=expr_pb.GetIndexedField(expr=parent_operand, list_index=key)
            )
        if isinstance(underscore, UnderscoreCall):
            if underscore._chalk__kwargs:
                raise NotImplementedError("kwargs are not supported in underscore calls")

            if not isinstance(underscore._chalk__parent, UnderscoreAttr):
                raise ValueError("underscore call must be on an attribute")

            operation = underscore._chalk__parent._chalk__attr

            if operation in ToProtoConverter._arg_taking_aggs:
                return expr_pb.LogicalExprNode(
                    aggregate_udf_expr=expr_pb.AggregateUDFExprNode(
                        fun_name=operation,
                        args=[ToProtoConverter.convert_underscore(a) for a in underscore._chalk__args],
                    )
                )
            else:
                if operation not in ToProtoConverter._agg_to_protobuf:
                    raise ValueError(f"Unknown aggregate function: {operation}")
                aggr_function = ToProtoConverter._agg_to_protobuf[operation]

                if len(underscore._chalk__args):
                    raise ValueError(
                        f"Aggregate function '{operation}' does not take arguments but was provided with at least one"
                    )

                return expr_pb.LogicalExprNode(
                    aggregate_expr=expr_pb.AggregateExprNode(
                        expr=[ToProtoConverter.convert_underscore(underscore._chalk__parent._chalk__parent)],
                        aggr_function=aggr_function,
                    )
                )
        if isinstance(underscore, UnderscoreBinaryOp):
            return expr_pb.LogicalExprNode(
                binary_expr=expr_pb.BinaryExprNode(
                    operands=[
                        ToProtoConverter.convert_underscore(underscore._chalk__left),
                        ToProtoConverter.convert_underscore(underscore._chalk__right),
                    ],
                    op=underscore._chalk__op,
                )
            )
        if isinstance(underscore, UnderscoreUnaryOp):
            if underscore._chalk__op == "~":
                return expr_pb.LogicalExprNode(
                    not_expr=expr_pb.Not(
                        expr=ToProtoConverter.convert_underscore(underscore._chalk__operand),
                    )
                )
            if underscore._chalk__op == "-":
                return expr_pb.LogicalExprNode(
                    negative=expr_pb.NegativeNode(
                        expr=ToProtoConverter.convert_underscore(underscore._chalk__operand),
                    )
                )
            if underscore._chalk__op == "+":
                return ToProtoConverter.convert_underscore(underscore._chalk__operand)

        raise TypeError(f"Unknown underscore type: {type(underscore).__name__}")

    @staticmethod
    def _convert_stream_source(source: StreamSource) -> sources_pb.StreamSource:
        source_name = ToProtoConverter._resolve_source_name(source)
        if isinstance(source, KafkaSource):
            return sources_pb.StreamSource(
                kafka=sources_pb.KafkaSource(
                    name=source_name,
                    bootstrap_servers=source.bootstrap_server,
                    topic=source.topic,
                    ssl_keystore_location=source.ssl_keystore_location,
                    ssl_ca_file=source.ssl_ca_file,
                    client_id_prefix=source.client_id_prefix,
                    group_id_prefix=source.group_id_prefix,
                    security_protocol=source.security_protocol,
                    sasl_mechanism=source.sasl_mechanism,
                    sasl_username=source.sasl_username,
                    sasl_password=source.sasl_password,
                    late_arrival_deadline=timedelta_to_proto_duration(
                        convert_raw_duration(duration=source.late_arrival_deadline)
                    ),
                    dead_letter_queue_topic=source.dead_letter_queue_topic,
                )
            )
        elif isinstance(source, KinesisSource):
            return sources_pb.StreamSource(
                kinesis=sources_pb.KinesisSource(
                    name=source_name,
                    stream_name=source.stream_name,
                    stream_arn=source.stream_arn,
                    region_name=source.region_name,
                    late_arrival_deadline=timedelta_to_proto_duration(
                        convert_raw_duration(duration=source.late_arrival_deadline)
                    ),
                    dead_letter_queue_stream_name=source.dead_letter_queue_stream_name,
                    aws_access_key_id=source.aws_access_key_id,
                    aws_secret_access_key=source.aws_secret_access_key,
                    aws_session_token=source.aws_session_token,
                    endpoint_url=source.endpoint_url,
                    consumer_role_arn=source.consumer_role_arn,
                )
            )
        else:
            raise TypeError(f"Unknown stream source type: {type(source).__name__}")

    @staticmethod
    def convert_stream_source(source: StreamSource) -> sources_pb.StreamSource:
        try:
            return ToProtoConverter._convert_stream_source(source)
        except Exception as e:
            raise ValueError(f"Could not convert stream source '{source.name}': {e}")

    @staticmethod
    def convert_engine_args(engine_args: Dict[str, Any]) -> Dict[str, arrow_pb.ScalarValue]:
        res = {}
        for k, v in engine_args.items():
            try:
                json_val = json.dumps(v)
            except Exception as e:
                raise ValueError(f"Could not convert engine arg '{k}' to JSON: {e}")
            res[k] = arrow_pb.ScalarValue(large_utf8_value=json_val)
        return res

    @staticmethod
    def _convert_sql_source(source: BaseSQLSource) -> sources_pb.DatabaseSource:
        source_name = ToProtoConverter._resolve_source_name(source)
        if isinstance(source, BigQuerySourceImpl):
            return sources_pb.DatabaseSource(
                bigquery=sources_pb.BigQuerySource(
                    name=source_name,
                    project=source.project,
                    dataset=source.dataset,
                    location=source.location,
                    credentials_base64=source.credentials_base64,
                    credentials_path=source.credentials_path,
                    engine_args=ToProtoConverter.convert_engine_args(source._engine_args),
                    async_engine_args=ToProtoConverter.convert_engine_args(source._async_engine_args),
                )
            )
        elif isinstance(source, CloudSQLSourceImpl):
            return sources_pb.DatabaseSource(
                cloudsql=sources_pb.CloudSQLSource(
                    name=source_name,
                    db=source.db,
                    user=source.user,
                    password=source.password,
                    instance_name=source.instance_name,
                    engine_args=ToProtoConverter.convert_engine_args(source._engine_args),
                    async_engine_args=ToProtoConverter.convert_engine_args(source._async_engine_args),
                )
            )
        elif isinstance(source, DatabricksSourceImpl):
            return sources_pb.DatabaseSource(
                databricks=sources_pb.DatabricksSource(
                    name=source_name,
                    host=source.host,
                    port=str(source.port),
                    db=source.db,
                    http_path=source.http_path,
                    access_token=source.access_token,
                    engine_args=ToProtoConverter.convert_engine_args(source._engine_args),
                    async_engine_args=ToProtoConverter.convert_engine_args(source._async_engine_args),
                )
            )
        elif isinstance(source, MySQLSourceImpl):
            return sources_pb.DatabaseSource(
                mysql=sources_pb.MySQLSource(
                    name=source_name,
                    host=source.host,
                    port=str(source.port),
                    db=source.db,
                    user=source.user,
                    password=source.password,
                    engine_args=ToProtoConverter.convert_engine_args(source._engine_args),
                    async_engine_args=ToProtoConverter.convert_engine_args(source._async_engine_args),
                )
            )
        elif isinstance(source, RedshiftSourceImpl):
            return sources_pb.DatabaseSource(
                redshift=sources_pb.RedshiftSource(
                    name=source_name,
                    host=source.host,
                    port=str(source.port),
                    db=source.db,
                    user=source.user,
                    password=source.password,
                    s3_client=source._s3_client,
                    s3_bucket=source._s3_bucket,
                    engine_args=ToProtoConverter.convert_engine_args(source._engine_args),
                    async_engine_args=ToProtoConverter.convert_engine_args(source._async_engine_args),
                )
            )
        elif isinstance(source, SnowflakeSourceImpl):
            return sources_pb.DatabaseSource(
                snowflake=sources_pb.SnowflakeSource(
                    name=source_name,
                    db=source.name,
                    schema=source.schema,
                    role=source.role,
                    user=source.user,
                    password=source.password,
                    account_identifier=source.account_identifier,
                    warehouse=source.warehouse,
                    engine_args=ToProtoConverter.convert_engine_args(source._engine_args),
                    async_engine_args=ToProtoConverter.convert_engine_args(source._async_engine_args),
                )
            )
        elif isinstance(source, SQLiteSourceImpl):
            return sources_pb.DatabaseSource(
                sqlite=sources_pb.SQLiteSource(
                    name=source_name,
                    file_name=source.filename,
                    engine_args=ToProtoConverter.convert_engine_args(source._engine_args),
                    async_engine_args=ToProtoConverter.convert_engine_args(source._async_engine_args),
                )
            )
        elif isinstance(source, PostgreSQLSourceImpl):
            return sources_pb.DatabaseSource(
                postgres=sources_pb.PostgresSource(
                    name=source_name,
                    host=source.host,
                    port=str(source.port),
                    db=source.db,
                    user=source.user,
                    password=source.password,
                    engine_args=ToProtoConverter.convert_engine_args(source._engine_args),
                    async_engine_args=ToProtoConverter.convert_engine_args(source._async_engine_args),
                )
            )
        else:
            raise ValueError(f"Unknown database source type: {type(source).__name__}")

    @staticmethod
    def convert_sql_source(source: BaseSQLSource) -> sources_pb.DatabaseSource:
        try:
            return ToProtoConverter._convert_sql_source(source)
        except Exception as e:
            raise ValueError(f"Could not convert SQL source '{source.name}': {e}")

    @staticmethod
    def convert_cron_filter(cron: Union[CronTab, Duration, Cron]) -> Optional[CronFilterWithFeatureArgs]:
        if isinstance(cron, Cron) and cron.filter is not None:
            sig = inspect.signature(cron.filter)
            features = []
            for parameter in sig.parameters.values():
                try:
                    feature = ensure_feature(parameter.annotation)
                except:
                    raise ValueError(f"Cron filter arguments must be features")
                if not feature.is_feature_time and not feature.is_scalar:
                    raise ValueError("Cron filters must be scalars or feature time features")
                features.append(ToProtoConverter.create_feature_reference(feature))
            return CronFilterWithFeatureArgs(
                filter=ToProtoConverter.create_function_reference(cron.filter),
                args=features,
            )
        return None

    @staticmethod
    def convert_feature_to_filter_node(raw: Feature) -> expr_pb.LogicalExprNode:
        if raw.path:
            path_converted = []
            for p in raw.path:
                path_converted.append(
                    expr_pb.Column(name=p.parent.name, relation=expr_pb.ColumnRelation(relation=p.parent.namespace))
                )
            path_converted.append(
                expr_pb.Column(name=raw.name, relation=expr_pb.ColumnRelation(relation=raw.namespace))
            )

            return expr_pb.LogicalExprNode(
                binary_expr=expr_pb.BinaryExprNode(
                    operands=[expr_pb.LogicalExprNode(column=p) for p in path_converted],
                    op="foreign_feature_access",
                )
            )

        return expr_pb.LogicalExprNode(
            column=expr_pb.Column(name=raw.name, relation=expr_pb.ColumnRelation(relation=raw.namespace)),
        )

    @staticmethod
    def convert_filter(f: Filter) -> expr_pb.LogicalExprNode:

        if not is_valid_operation(f.operation):
            raise ValueError(f"Unknown operation '{f.operation}'")

        if f.operation in ("and", "or"):
            if not isinstance(f.lhs, Filter):
                raise ValueError("lhs of and/or must be a Filter")
            if not isinstance(f.rhs, Filter):
                raise ValueError("rhs of and/or must be a Filter")
            return expr_pb.LogicalExprNode(
                binary_expr=expr_pb.BinaryExprNode(
                    operands=[
                        ToProtoConverter.convert_filter(f.lhs),
                        ToProtoConverter.convert_filter(f.rhs),
                    ],
                    op=f.operation,
                ),
            )

        raw_lhs = f.lhs
        raw_rhs = f.rhs

        if isinstance(raw_lhs, FeatureWrapper):
            raw_lhs = raw_lhs._chalk_feature
        if isinstance(raw_rhs, FeatureWrapper):
            raw_rhs = raw_rhs._chalk_feature

        converted_lhs = raw_lhs
        converted_rhs = raw_rhs

        if isinstance(raw_lhs, Feature):
            if not raw_lhs.is_scalar and not raw_lhs.is_feature_time:
                raise ValueError("lhs of filter is a feature that is not scalar or feature-time")
            converted_lhs = ToProtoConverter.convert_feature_to_filter_node(raw_lhs)
        if isinstance(raw_rhs, Feature):
            if not raw_rhs.is_scalar and not raw_rhs.is_feature_time:
                raise ValueError("rhs of filter is a feature that is not scalar or feature-time")
            converted_rhs = ToProtoConverter.convert_feature_to_filter_node(raw_rhs)

        if isinstance(raw_lhs, Feature) and isinstance(raw_rhs, TimeDelta):
            # This means that the filter was a before() or after()
            duration_converter = FeatureConverter(name="helper", is_nullable=False, pyarrow_dtype=pa.duration("us"))
            converted_rhs = expr_pb.LogicalExprNode(
                literal=duration_converter.from_primitive_to_protobuf_single(raw_rhs.to_std())
            )
            return expr_pb.LogicalExprNode(
                binary_expr=expr_pb.BinaryExprNode(
                    operands=[converted_lhs, converted_rhs],
                    op=f.operation,
                ),
            )

        if not isinstance(raw_lhs, Feature):
            if not isinstance(raw_rhs, Feature):
                raise ValueError("One side must be a feature")
            converted_lhs = expr_pb.LogicalExprNode(
                literal=raw_rhs.converter.from_primitive_to_protobuf_single(converted_lhs),
            )

        if not isinstance(raw_rhs, Feature):
            if not isinstance(raw_lhs, Feature):
                raise ValueError("One side must be a feature")
            if f.operation in ("in", "not in"):
                if not isinstance(raw_rhs, collections.abc.Iterable):
                    raise ValueError("rhs must be an iterable when operation is 'in'/'not in'")
                prim_values = tuple(raw_lhs.converter.from_rich_to_primitive(x) for x in raw_rhs)
                list_dtype = pa.large_list(raw_lhs.converter.pyarrow_dtype)
                list_converter = FeatureConverter(name="helper", is_nullable=False, pyarrow_dtype=list_dtype)
                converted_rhs = expr_pb.LogicalExprNode(
                    literal=list_converter.from_primitive_to_protobuf_single(prim_values),
                )
            else:
                converted_rhs = expr_pb.LogicalExprNode(literal=raw_lhs.converter.from_rich_to_protobuf(raw_rhs))

        return expr_pb.LogicalExprNode(
            binary_expr=expr_pb.BinaryExprNode(
                operands=[converted_lhs, converted_rhs],
                op=f.operation,
            )
        )

    @staticmethod
    def _resolve_source_name(source: Union[BaseSQLSource, StreamSource]) -> str:
        if isinstance(source, BaseSQLSource):
            return source.name or f"__chalk_anon_sql_source_{id(source)}"
        elif isinstance(source, StreamSource):
            return source.name or f"__chalk_anon_stream_source_{id(source)}"
        else:
            raise ValueError(f"Unknown source type: {type(source).__name__}")

    @staticmethod
    def create_database_source_reference(source: BaseSQLSource) -> sources_pb.DatabaseSourceReference:
        if isinstance(source, BigQuerySourceImpl):
            source_type = sources_pb.DATABASE_SOURCE_TYPE_BIGQUERY
        elif isinstance(source, CloudSQLSourceImpl):
            source_type = sources_pb.DATABASE_SOURCE_TYPE_CLOUDSQL
        elif isinstance(source, DatabricksSourceImpl):
            source_type = sources_pb.DATABASE_SOURCE_TYPE_DATABRICKS
        elif isinstance(source, MySQLSourceImpl):
            source_type = sources_pb.DATABASE_SOURCE_TYPE_MYSQL
        elif isinstance(source, RedshiftSourceImpl):
            source_type = sources_pb.DATABASE_SOURCE_TYPE_REDSHIFT
        elif isinstance(source, SnowflakeSourceImpl):
            source_type = sources_pb.DATABASE_SOURCE_TYPE_SNOWFLAKE
        elif isinstance(source, SQLiteSourceImpl):
            source_type = sources_pb.DATABASE_SOURCE_TYPE_SQLITE
        elif isinstance(source, PostgreSQLSourceImpl):
            source_type = sources_pb.DATABASE_SOURCE_TYPE_POSTGRES
        else:
            raise ValueError(f"Unknown database source type: {type(source).__name__}")

        return sources_pb.DatabaseSourceReference(
            name=ToProtoConverter._resolve_source_name(source),
            type=source_type,
        )

    @staticmethod
    def convert_rich_type_to_protobuf(rich_type: Type[TRich]) -> arrow_pb.ArrowType:
        converter = FeatureConverter(name="helper", is_nullable=False, rich_type=rich_type)
        return converter.convert_pa_dtype_to_proto_dtype(converter.pyarrow_dtype)

    @staticmethod
    def create_stream_source_reference(source: StreamSource) -> sources_pb.StreamSourceReference:
        if isinstance(source, KafkaSource):
            source_type = sources_pb.STREAM_SOURCE_TYPE_KAFKA
        elif isinstance(source, KinesisSource):
            source_type = sources_pb.STREAM_SOURCE_TYPE_KINESIS
        elif isinstance(source, StreamSource):
            # MockStreamSource
            source_type = sources_pb.STREAM_SOURCE_TYPE_UNSPECIFIED
        else:
            raise TypeError(f"Unknown stream source type: {type(source).__name__}")

        return sources_pb.StreamSourceReference(
            name=ToProtoConverter._resolve_source_name(source),
            type=source_type,
        )

    @staticmethod
    def create_function_reference(fn: Callable) -> pb.FunctionReference:
        module = inspect.getmodule(fn)
        return pb.FunctionReference(
            name=fn.__name__,
            module=module.__name__ if module else "",
            file_name=inspect.getfile(fn),
            function_definition=inspect.getsource(fn),
        )

    @staticmethod
    def create_feature_reference(feature: Feature) -> pb.FeatureReference:
        df = None
        if feature.is_has_many:
            df = feature.typ.parsed_annotation
            if not isinstance(df, type) or not issubclass(df, DataFrame):
                raise ValueError("has-many feature missing `DataFrame` annotation")

        return pb.FeatureReference(
            name=feature.name,
            namespace=feature.namespace,
            path=[ToProtoConverter.create_feature_reference(path_elem.parent) for path_elem in feature.path],
            df=ToProtoConverter.convert_dataframe(df) if df else None,
        )

    @staticmethod
    def convert_resolver_inputs(
        resolver_inputs: Sequence[Union[Feature, FeatureWrapper, Type[DataFrame]]],
        state: Optional[StateDescriptor],
        default_args: List,
    ) -> List[pb.ResolverInput]:
        inputs = []
        raw_inputs: List[Optional[Union[Feature, FeatureWrapper, Type[DataFrame]]]] = [i for i in resolver_inputs]
        if state is not None:
            raw_inputs.insert(state.pos, None)

        is_sole_dataframe_input = (
            len(resolver_inputs) == 1
            and isinstance(resolver_inputs[0], type)
            and issubclass(resolver_inputs[0], DataFrame)
        )
        if is_sole_dataframe_input:
            # TODO: Enforce check when there is uniformity in how many
            #       default args there are if there is a sole DF input
            # if len(resolver_inputs[0].columns) != len(default_args):
            #     raise ValueError(
            #         f"Length mismatch: found {len(resolver_inputs[0].columns)} DF "
            #         + f"columns and {len(default_args)} default arg"
            #     )
            pass
        else:
            if len(raw_inputs) != len(default_args):
                if (
                    resolver_inputs
                    and isinstance(resolver_inputs[0], type)
                    and issubclass(resolver_inputs[0], DataFrame)
                ):
                    # TODO: Remove this exception once we fix the incorrect default args count.
                    #       Currently we take the num columns of the first DF as the num default args,
                    #       regardless of whether or not it is the sole input.
                    pass
                else:
                    raise ValueError(
                        f"Length mismatch: found {len(raw_inputs)} `inputs` and {len(default_args)} `default_args`"
                    )

        for i in range(len(raw_inputs)):
            if state and i == state.pos:
                converter = FeatureConverter(
                    name="state", is_nullable=False, rich_type=state.typ, rich_default=state.initial
                )
                inputs.append(
                    pb.ResolverInput(
                        state=pb.ResolverState(
                            initial=converter.from_rich_to_protobuf(state.initial),
                            arrow_type=converter.convert_pa_dtype_to_proto_dtype(converter.pyarrow_dtype),
                        )
                    )
                )
            elif isinstance(raw_inputs[i], type) and issubclass(raw_inputs[i], DataFrame):
                inputs.append(pb.ResolverInput(df=ToProtoConverter.convert_dataframe(raw_inputs[i])))
            else:
                inp = ensure_feature(raw_inputs[i])
                default_arg = default_args[i]
                if default_arg is not None and not isinstance(default_arg, ResolverArgErrorHandler):
                    raise ValueError(f"Invalid default arg: {default_arg}")

                inputs.append(
                    pb.ResolverInput(
                        feature=pb.FeatureInput(
                            feature=ToProtoConverter.create_feature_reference(inp),
                            default_value=inp.converter.from_primitive_to_protobuf_single(default_arg.default_value)
                            if default_arg is not None
                            else None,
                        )
                    )
                )

        return inputs

    @staticmethod
    def convert_resolver_outputs(raw_outputs: List[Union[Feature, Type[DataFrame]]]) -> List[pb.ResolverOutput]:
        outputs = []
        for o in raw_outputs:
            if isinstance(o, type) and issubclass(o, DataFrame):
                outputs.append(pb.ResolverOutput(df=ToProtoConverter.convert_dataframe(o)))
            elif isinstance(o, Feature):
                outputs.append(pb.ResolverOutput(feature=ToProtoConverter.create_feature_reference(o)))
            else:
                raise TypeError(f"Unknown output type: {type(o).__name__}")
        return outputs

    @staticmethod
    def convert_validations(validations: Optional[List[FeatureValidation]]) -> Optional[List[pb.FeatureValidation]]:
        if validations is None:
            return None

        res = []
        for val in validations:
            if val.min is not None:
                res.append(pb.FeatureValidation(min=val.min, strict=val.strict))
            if val.max is not None:
                res.append(pb.FeatureValidation(max=val.max, strict=val.strict))
            if val.min_length is not None:
                res.append(pb.FeatureValidation(min_length=val.min_length, strict=val.strict))
            if val.max_length is not None:
                res.append(pb.FeatureValidation(max_length=val.max_length, strict=val.strict))

        return res

    @staticmethod
    def convert_has_many(f: Feature) -> pb.FeatureType:
        if not f.is_has_many:
            raise ValueError("Should only be called on has_many features")
        if f.path:
            raise ValueError("Should not be called on features with `path`")
        if f.join is None:
            raise ValueError(f"Feature missing join")

        max_staleness_duration = None
        if f.max_staleness is not None:
            max_staleness_duration = timedelta_to_proto_duration(convert_raw_duration(f.max_staleness))
        res = pb.FeatureType(
            has_many=pb.HasManyFeatureType(
                name=f.name,
                namespace=f.namespace,
                is_autogenerated=f.is_autogenerated,
                join=ToProtoConverter.convert_filter(f.join),
                foreign_namespace=f.joined_class.namespace,
                max_staleness_duration=max_staleness_duration,
            )
        )

        return res

    @staticmethod
    def convert_has_one(f: Feature) -> pb.FeatureType:
        if f.path:
            raise ValueError("Should not be called on features with `path`")
        if f.join is None:
            raise ValueError(f"Feature missing join {f.namespace}.{f.name}")
        if f.joined_class is None:
            raise ValueError("has-one relationships must reference a Features cls")
        if not isinstance(f.join.lhs, Feature):
            raise ValueError("lhs of join must be a Feature")
        if not isinstance(f.join.rhs, Feature):
            raise ValueError("rhs of join must be a Feature")

        res = pb.FeatureType(
            has_one=pb.HasOneFeatureType(
                name=f.name,
                namespace=f.namespace,
                is_nullable=f.typ.is_nullable,
                is_autogenerated=f.is_autogenerated,
                join=ToProtoConverter.convert_filter(f.join),
                foreign_namespace=f.joined_class.namespace,
            )
        )
        return res

    @staticmethod
    def convert_feature_time_feature(f: Feature) -> pb.FeatureType:
        if not f.is_feature_time:
            raise ValueError("Should only be called on feature time features")

        return pb.FeatureType(
            feature_time=pb.FeatureTimeFeatureType(
                name=f.name,
                namespace=f.namespace,
                is_autogenerated=f.is_autogenerated,
            )
        )

    @staticmethod
    def convert_windowed(f: Feature) -> pb.FeatureType:
        if not f.is_windowed:
            raise ValueError("Should only be called on windowed features")
        if f.path:
            raise ValueError("Should not be called on features with `path`")

        return pb.FeatureType(
            windowed=pb.WindowedFeatureType(
                name=f.name,
                namespace=f.namespace,
                is_autogenerated=f.is_autogenerated,
                window_durations=[seconds_to_proto_duration(d) for d in f.window_durations],
            )
        )

    @staticmethod
    def convert_scalar(f: Feature) -> pb.FeatureType:
        if not f.is_scalar:
            raise ValueError("Should only be called on scalar features")
        if f.path:
            raise ValueError("Should not be called on features with `path`")

        res = pb.FeatureType(
            scalar=pb.ScalarFeatureType(
                name=f.name,
                namespace=f.namespace,
                arrow_type=f.converter.convert_pa_dtype_to_proto_dtype(f.converter.pyarrow_dtype),
                is_distance_pseudofeature=f.is_distance_pseudofeature,
                is_nullable=f.typ.is_nullable,
                is_primary=f.primary,
                description=f.description,
                owner=f.owner,
                is_autogenerated=f.is_autogenerated,
                max_staleness_duration=timedelta_to_proto_duration(convert_raw_duration(f._raw_max_staleness))
                if f._raw_max_staleness is not ... and f._raw_max_staleness is not None
                else None,
                offline_ttl_duration=timedelta_to_proto_duration(convert_raw_duration(f._offline_ttl))
                if f._offline_ttl is not ... and f._offline_ttl is not None
                else None,
                window_info=pb.WindowInfo(
                    duration=seconds_to_proto_duration(f.window_duration),
                )
                if f.is_windowed_pseudofeature
                else None,
                etl_offline_to_online=f._raw_etl_offline_to_online,
                tags=f.tags,
                version=pb.VersionInfo(
                    default=f.version.default,
                    maximum=f.version.maximum,
                )
                if f.version
                else None,
                last_for=ToProtoConverter.create_feature_reference(f.last_for) if f.last_for else None,
                default_value=f.converter.from_primitive_to_protobuf_single(f.converter.primitive_default)
                if f.converter._primitive_default is not ...
                else None,
                validations=ToProtoConverter.convert_validations(f._all_validations),
                expression=ToProtoConverter.convert_underscore(f.underscore_expression)
                if f.underscore_expression
                else None,
                no_display=f.no_display,
            )
        )
        return res

    @staticmethod
    def _convert_feature(o: Feature) -> pb.FeatureType:
        if not isinstance(o, Feature):
            raise ValueError("Should only be called on `Feature` objects")
        if o.path:
            raise ValueError("Features with `path` not supported yet")

        if o.is_scalar:
            if o.is_windowed:  # nesting in o.is_scalar to prevent bugs
                return ToProtoConverter.convert_windowed(o)
            return ToProtoConverter.convert_scalar(o)
        if o.is_feature_time:
            return ToProtoConverter.convert_feature_time_feature(o)
        if o.is_has_one:
            return ToProtoConverter.convert_has_one(o)
        if o.is_has_many:
            return ToProtoConverter.convert_has_many(o)

        raise ValueError(f"Unknown Feature object: {o}")

    @staticmethod
    def convert_feature(o: Feature) -> pb.FeatureType:
        try:
            return ToProtoConverter._convert_feature(o)
        except Exception as e:
            raise ValueError(f"Error converting feature '{o.namespace}.{o.name}': {e}")

    @staticmethod
    def convert_dataframe(df: Type[DataFrame]) -> pb.DataFrameType:
        return pb.DataFrameType(
            root_namespace=get_unique_item(x.root_namespace for x in df.columns if x.root_namespace != PSEUDONAMESPACE),
            optional_columns=[ToProtoConverter.create_feature_reference(ensure_feature(c)) for c in df.columns],
            required_columns=(),
            filter=expr_pb.LogicalExprNode(
                binary_expr=expr_pb.BinaryExprNode(
                    operands=[ToProtoConverter.convert_filter(f) for f in df.filters],
                    op="and",
                )
            ),
            limit=df.__limit__ if df.__limit__ is not None else None,
        )

    @staticmethod
    def convert_online_or_offline_resolver(r: Union[OnlineResolver, OfflineResolver]) -> pb.Resolver:
        if r.output is None:
            raise ValueError("Resolver missing `output` attribute")

        outputs = ToProtoConverter.convert_resolver_outputs(r.output.features or [])
        schedule = None
        cron_filter = None
        if r.cron is not None:
            if isinstance(r.cron, Cron):
                duration = None
                crontab = None
                if isinstance(r.cron.schedule, str):
                    try:
                        duration_td = parse_chalk_duration(r.cron.schedule)
                    except ValueError:
                        crontab = r.cron.schedule
                    else:
                        duration = timedelta_to_proto_duration(duration_td)
                elif isinstance(r.cron.schedule, timedelta):
                    duration = timedelta_to_proto_duration(r.cron.schedule)
                else:
                    raise TypeError(f"Unknown cron schedule type: {type(r.cron.schedule).__name__}")

                cron_filter = ToProtoConverter.convert_cron_filter(r.cron) if r.cron.filter else None

                schedule = pb.Schedule(
                    filter=ToProtoConverter.create_function_reference(r.cron.filter)
                    if r.cron.filter is not None
                    else None,
                    sample=ToProtoConverter.create_function_reference(r.cron.sample) if r.cron.sample else None,
                    duration=duration,
                    crontab=crontab,
                )
            elif isinstance(r.cron, str):
                try:
                    duration_td = parse_chalk_duration(r.cron)
                except:
                    schedule = pb.Schedule(crontab=r.cron)
                else:
                    schedule = pb.Schedule(duration=timedelta_to_proto_duration(duration_td))
            elif isinstance(r.cron, timedelta):
                schedule = pb.Schedule(duration=timedelta_to_proto_duration(r.cron))
            else:
                raise TypeError(f"Unknown cron type: {type(r.cron).__name__}")

        return pb.Resolver(
            fqn=r.fqn,
            kind=pb.ResolverKind.RESOLVER_KIND_ONLINE
            if isinstance(r, OnlineResolver)
            else pb.ResolverKind.RESOLVER_KIND_OFFLINE,
            inputs=ToProtoConverter.convert_resolver_inputs(r.inputs, r.state, r.default_args),
            outputs=outputs,
            is_generator=inspect.isgeneratorfunction(r.fn),
            data_sources=[ToProtoConverter.create_database_source_reference(s) for s in (r.data_sources or [])],
            machine_type=r.machine_type,
            tags=r.tags or [],
            owner=r.owner,
            doc=r.doc,
            environments=r.environment or [],
            timeout_duration=timedelta_to_proto_duration(r.timeout) if r.timeout is not None else None,
            schedule=schedule,
            when=ToProtoConverter.convert_filter(r.when) if r.when else None,
            cron_filter=cron_filter,
            function=ToProtoConverter.create_function_reference(r.fn),
        )

    @staticmethod
    def convert_stream_resolver_param(p: StreamResolverParam) -> pb.StreamResolverParam:
        if isinstance(p, StreamResolverParamMessage):
            return pb.StreamResolverParam(
                message=pb.StreamResolverParamMessage(
                    name=p.name,
                    arrow_type=ToProtoConverter.convert_rich_type_to_protobuf(p.typ),
                )
            )
        elif isinstance(p, StreamResolverParamMessageWindow):
            return pb.StreamResolverParam(
                message_window=pb.StreamResolverParamMessageWindow(
                    name=p.name,
                    arrow_type=ToProtoConverter.convert_rich_type_to_protobuf(p.typ),
                )
            )
        elif isinstance(p, StreamResolverParamKeyedState):
            converter = FeatureConverter(
                name="helper", is_nullable=False, rich_type=p.typ, rich_default=p.default_value
            )
            return pb.StreamResolverParam(
                state=pb.ResolverState(
                    arrow_type=converter.convert_pa_dtype_to_proto_dtype(converter.pyarrow_dtype)
                    if converter
                    else None,
                    initial=converter.from_rich_to_protobuf(p.default_value) if converter else None,
                )
            )
        else:
            raise TypeError(f"Unknown param type: {type(p).__name__}")

    @classmethod
    def convert_stream_resolver(cls, r: StreamResolver) -> pb.StreamResolver:
        mode = None
        if r.mode:
            mode = cls._mode_to_enum.get(r.mode)
            if mode is None:
                raise ValueError(f"Unknown window mode: {r.mode}")

        return pb.StreamResolver(
            fqn=r.fqn,
            params=[ToProtoConverter.convert_stream_resolver_param(p) for p in r.signature.params],
            outputs=ToProtoConverter.convert_resolver_outputs(r.output.features or []),
            explicit_schema=ToProtoConverter.convert_rich_type_to_protobuf(cast(Optional[Type[BaseModel]], r.message))
            if r.message
            else None,
            keys=[
                pb.StreamKey(key=k, feature=ToProtoConverter.create_feature_reference(ensure_feature(v)))
                for k, v in r.keys.items()
            ]
            if r.keys is not None
            else None,
            source=ToProtoConverter.create_stream_source_reference(r.source),
            parse_info=pb.ParseInfo(
                parse_function_input_type=ToProtoConverter.convert_rich_type_to_protobuf(r.parse.input_type),
                parse_function_output_type=ToProtoConverter.convert_rich_type_to_protobuf(r.parse.output_type),
                parse_function=ToProtoConverter.create_function_reference(r.parse.fn),
                is_parse_function_output_optional=r.parse.output_is_optional,
            )
            if r.parse
            else None,
            mode=mode,
            environments=r.environment or [],
            timeout_duration=timedelta_to_proto_duration(r.timeout) if r.timeout is not None else None,
            timestamp_attribute_name=r.timestamp,
            owner=r.owner,
            doc=r.doc,
            machine_type=r.machine_type,
            function=ToProtoConverter.create_function_reference(r.fn),
        )

    @staticmethod
    def convert_sink_resolver(r: SinkResolver) -> pb.SinkResolver:
        stream_source = None
        database_source = None

        if r.integration:
            if isinstance(r.integration, BaseSQLSource):
                database_source = ToProtoConverter.create_database_source_reference(r.integration)
            elif isinstance(r.integration, StreamSource):
                stream_source = ToProtoConverter.create_stream_source_reference(r.integration)
            else:
                raise TypeError(f"Unsupported integration type: {type(r.integration).__name__}")

        return pb.SinkResolver(
            fqn=r.fqn,
            inputs=ToProtoConverter.convert_resolver_inputs(r.inputs, r.state, r.default_args),
            buffer_size=r.buffer_size if r.buffer_size is not None else None,
            debounce_duration=timedelta_to_proto_duration(r.debounce) if r.debounce is not None else None,
            max_delay_duration=timedelta_to_proto_duration(r.max_delay) if r.max_delay is not None else None,
            upsert=r.upsert,
            stream_source=stream_source,
            database_source=database_source,
            machine_type=r.machine_type,
            doc=r.doc,
            owner=r.owner,
            environments=r.environment or [],
            timeout_duration=timedelta_to_proto_duration(r.timeout) if r.timeout is not None else None,
            function=ToProtoConverter.create_function_reference(r.fn),
        )

    @staticmethod
    def _convert_resolver(r: Resolver) -> Union[pb.Resolver, pb.StreamResolver, pb.SinkResolver]:
        if isinstance(r, (OnlineResolver, OfflineResolver)):
            return ToProtoConverter.convert_online_or_offline_resolver(r)
        elif isinstance(r, StreamResolver):
            return ToProtoConverter.convert_stream_resolver(r)
        elif isinstance(r, SinkResolver):
            return ToProtoConverter.convert_sink_resolver(r)
        else:
            raise TypeError(f"Unknown resolver type: {type(r).__name__}")

    @staticmethod
    def convert_resolver(r: Resolver) -> Union[pb.Resolver, pb.StreamResolver, pb.SinkResolver]:
        try:
            return ToProtoConverter._convert_resolver(r)
        except Exception as e:
            raise ValueError(f"Error converting resolver '{r.fqn}': {e}")

    @staticmethod
    def convert_graph(
        features_registry: Dict[str, Type[Features]],
        resolver_registry: ResolverRegistry,
        sql_source_registry: List[BaseSQLSource],
        stream_source_registry: List[StreamSource],
    ) -> pb.Graph:
        feature_sets = []

        for namespace, feature_set in features_registry.items():
            feature_sets.append(
                pb.FeatureSet(
                    name=feature_set.namespace,
                    features=[ToProtoConverter.convert_feature(f) for f in feature_set.features],
                    is_singleton=feature_set.__chalk_is_singleton__,
                    max_staleness_duration=timedelta_to_proto_duration(feature_set.__chalk_max_staleness__),
                    tags=feature_set.__chalk_tags__,
                    owner=feature_set.__chalk_owner__,
                    doc=feature_set.__doc__,
                    etl_offline_to_online=feature_set.__chalk_etl_offline_to_online__,
                )
            )

        resolvers = []
        stream_resolvers = []
        sink_resolvers = []
        for resolver in resolver_registry.get_all_resolvers():
            converted = ToProtoConverter.convert_resolver(resolver)
            if isinstance(converted, pb.Resolver):
                resolvers.append(converted)
            elif isinstance(converted, pb.StreamResolver):
                stream_resolvers.append(converted)
            elif isinstance(converted, pb.SinkResolver):
                sink_resolvers.append(converted)
            else:
                raise TypeError(f"Unknown resolver type: {type(converted).__name__}")

        return pb.Graph(
            feature_sets=feature_sets,
            resolvers=resolvers,
            stream_resolvers=stream_resolvers,
            sink_resolvers=sink_resolvers,
            database_sources=[
                ToProtoConverter.convert_sql_source(s)
                for s in sql_source_registry
                if isinstance(s, ToProtoConverter._supported_db_source_types)
            ],
            stream_sources=[
                ToProtoConverter.convert_stream_source(s)
                for s in stream_source_registry
                if isinstance(s, ToProtoConverter._supported_stream_source_types)
            ],
        )

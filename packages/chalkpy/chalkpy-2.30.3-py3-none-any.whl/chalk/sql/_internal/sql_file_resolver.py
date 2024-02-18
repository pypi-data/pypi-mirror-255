from __future__ import annotations

import dataclasses
import inspect
import json
import os
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Literal, Mapping, Optional, Sequence, Type, Union, cast

import yaml
from yaml.scanner import ScannerError

from chalk import OfflineResolver, OnlineResolver
from chalk._lsp.error_builder import SQLFileResolverErrorBuilder
from chalk.features import DataFrame, Feature, Features, FeatureSetBase
from chalk.features.resolver import ResolverArgErrorHandler, StreamResolver
from chalk.sql._internal.integrations.bigquery import BigQuerySourceImpl
from chalk.sql._internal.integrations.cloudsql import CloudSQLSourceImpl
from chalk.sql._internal.integrations.mysql import MySQLSourceImpl
from chalk.sql._internal.integrations.postgres import PostgreSQLSourceImpl
from chalk.sql._internal.integrations.redshift import RedshiftSourceImpl
from chalk.sql._internal.integrations.snowflake import SnowflakeSourceImpl
from chalk.sql._internal.integrations.sqlite import SQLiteSourceImpl
from chalk.sql._internal.sql_source import BaseSQLSource
from chalk.streams import KafkaSource, get_resolver_error_builder
from chalk.streams.base import StreamSource
from chalk.streams.types import StreamResolverSignature
from chalk.utils.collections import get_unique_item, get_unique_item_if_exists
from chalk.utils.duration import parse_chalk_duration
from chalk.utils.missing_dependency import missing_dependency_exception
from chalk.utils.string import to_snake_case

if TYPE_CHECKING:
    from pydantic import BaseModel, ValidationError, validator
    from sqlglot.expressions import Select
else:
    try:
        from pydantic.v1 import BaseModel, ValidationError, validator
    except ImportError:
        from pydantic import BaseModel, ValidationError, validator

_SOURCES: Mapping[str, Union[Type[BaseSQLSource], Type[StreamSource]]] = {
    "snowflake": SnowflakeSourceImpl,
    "postgres": PostgreSQLSourceImpl,
    "postgresql": PostgreSQLSourceImpl,
    "mysql": MySQLSourceImpl,
    "bigquery": BigQuerySourceImpl,
    "cloudsql": CloudSQLSourceImpl,
    "redshift": RedshiftSourceImpl,
    "sqlite": SQLiteSourceImpl,
    "kafka": KafkaSource,
}

_SQLGLOT_DIALECTS = frozenset(
    (
        "snowflake",
        "postgres",
        "mysql",
        "bigquery",
        "redshift",
        "sqlite",
        "databricks",
    )
)
"""These dialects are used if a "kind" of source is listed, rather than a specific source."""

_RESOLVER_TYPES = {
    "offline": OfflineResolver,
    "batch": OfflineResolver,
    "online": OnlineResolver,
    "realtime": OnlineResolver,
    "stream": StreamResolver,
    "streaming": StreamResolver,
}


class IncrementalSettings(BaseModel):
    incremental_column: Optional[str]
    lookback_period: Optional[str]
    mode: Literal["row", "group", "parameter"]
    incremental_timestamp: Optional[Literal["feature_time", "resolver_execution_time"]] = "feature_time"

    @validator("lookback_period")
    @classmethod
    def validate_lookback_period(cls, value: Optional[str]):
        if value is None:
            return None
        try:
            parse_chalk_duration(value)
        except Exception as e:
            raise ValueError(f"Could not parse value '{value}' as timedelta, {e}")
        return value

    @validator("mode")
    @classmethod
    def validate_mode(cls, mode: Literal["row", "group", "parameter"], values: Dict[str, Any]):
        if mode in ["row", "group"] and not values["incremental_column"]:
            raise ValueError(f"'incremental_column' must be set if mode is 'row' or 'group'.")
        return mode


class CommentDict(BaseModel):
    source: str
    resolves: str
    incremental: Optional[IncrementalSettings]
    tags: Optional[List[str]]
    environment: Optional[List[str]]
    count: Optional[Literal[1, "one", "one_or_none"]]
    cron: Optional[str]
    machine_type: Optional[str]
    max_staleness: Optional[str]
    message: Optional[str]
    owner: Optional[str]
    type: Optional[str]
    timeout: Optional[str]
    fields: Optional[Dict[str, str]]

    @validator("tags", "environment", pre=True)
    @classmethod
    def validate_list_inputs(cls, value: Union[str, List[str], None]):
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [value]
        raise ValueError(f"Value {value} must be a string or a list of strings.")

    @validator("max_staleness", "timeout")
    @classmethod
    def validate_timedelta(cls, string: Optional[str]):
        if string is None:
            return None
        try:
            parse_chalk_duration(string)
        except Exception as e:
            raise ValueError(f"Could not parse value '{string}' as timedelta, {e}")
        return string

    @validator("type")
    @classmethod
    def validate_type(cls, resolver_type: str):
        if resolver_type not in _RESOLVER_TYPES:
            raise ValueError(
                (
                    f"Resolver type '{resolver_type}' not supported. "
                    f"'online', 'offline' and 'streaming' are supported options"
                )
            )
        return resolver_type


@dataclasses.dataclass(frozen=True)
class ResolverError:
    """Generic class for returning errors at any point during resolution process"""

    display: str
    path: str
    parameter: Optional[str]


@dataclasses.dataclass(frozen=True)
class ResolverResult:
    """Chief return class with resolver we actually use"""

    resolver: Optional[Union[OnlineResolver, OfflineResolver, StreamResolver]]
    errors: List[ResolverError]
    db: Optional[Union[BaseSQLSource, StreamSource]]
    fields: Optional[Dict[str, str]]
    args: Optional[Dict[str, str]]


@dataclasses.dataclass(frozen=True)
class SQLStringResult:
    """Class for getting the sql string from the file"""

    path: str
    sql_string: Optional[str]
    error: Optional[ResolverError]

    @classmethod
    def fail(cls, display_error: str, path: str) -> "SQLStringResult":
        return cls(path=path, sql_string=None, error=ResolverError(display=display_error, path=path, parameter=None))


@dataclasses.dataclass(frozen=True)
class GlotResult:
    """Class for editing the sql string, and using sqlglot on sql string"""

    sql_string: str
    glot: Optional[Select]
    args: Dict[str, str]
    default_args: List[Union[Optional[str], ellipsis]]
    comment_dict: Optional[CommentDict]
    docstring: Optional[str]
    errors: List[ResolverError]


@dataclasses.dataclass(frozen=True)
class ParseResult:
    """Class for important info gathered from glot"""

    sql_string: str
    comment_dict: CommentDict
    fields: Dict[str, str]
    namespace: str
    source: Union[BaseSQLSource, StreamSource, None]
    docstring: Optional[str]
    errors: List[ResolverError]


_filepath_to_sql_string: dict[str, str] = {}
"""Mapping from filepath to sql string. Used to skip reimporting the same sql file if the content is identical to what was already imported
If the content is different, then we'll import it again, but we may error later when attempting to add the resolver to the registry if we don't
allow overrides and we're not in a notebook.
"""


def get_sql_file_resolvers(
    sql_file_resolve_location: Path,
    sources: Sequence[BaseSQLSource],
    has_import_errors: bool,
) -> Iterable[ResolverResult]:
    """Iterate through all `.chalk.sql` filepaths, gather the sql strings, and get a resolver hopefully for each."""
    for dp, dn, fn in os.walk(os.path.expanduser(sql_file_resolve_location)):
        del dn  # unused
        for f in fn:
            filepath = os.path.join(dp, f)
            if not filepath.endswith(".chalk.sql"):
                continue
                # Already imported this file. Skipping it, assuming it did not change since the last time we imported it
            sql_string_result = _get_sql_string(filepath)
            existing_sql_string = _filepath_to_sql_string.get(filepath)
            if sql_string_result.sql_string is not None:
                if existing_sql_string is not None and existing_sql_string == sql_string_result.sql_string:
                    # The sql file is identical to what was already imported. skip it
                    continue
                _filepath_to_sql_string[filepath] = sql_string_result.sql_string
            yield get_sql_file_resolver(sources, sql_string_result, has_import_errors)


def get_sql_file_resolvers_from_paths(
    sources: Sequence[BaseSQLSource], paths: List[str], has_import_errors: bool
) -> Iterable[ResolverResult]:
    for p in paths:
        sql_string_result = _get_sql_string(p)
        existing_sql_string = _filepath_to_sql_string.get(p)
        if sql_string_result.sql_string is not None:
            if existing_sql_string is not None and existing_sql_string == sql_string_result.sql_string:
                # The sql file is identical to what was already imported. skip it
                continue
            _filepath_to_sql_string[p] = sql_string_result.sql_string
        yield get_sql_file_resolver(
            sources=sources, sql_string_result=sql_string_result, has_import_errors=has_import_errors
        )


def get_sql_file_resolver(
    sources: Iterable[BaseSQLSource], sql_string_result: SQLStringResult, has_import_errors: bool = False
) -> ResolverResult:
    assert sql_string_result.sql_string is not None, f"SQL string from path {sql_string_result.path} should not be None"
    error_builder = SQLFileResolverErrorBuilder(uri=sql_string_result.path, sql_string=sql_string_result.sql_string)

    """Parse the sql strings and get a ResolverResult from each"""
    if sql_string_result.error:
        return ResolverResult(
            resolver=None,
            errors=[sql_string_result.error],
            db=None,
            fields=None,
            args=None,
        )
    assert sql_string_result.sql_string is not None
    path = sql_string_result.path

    errors: List[ResolverError] = []
    glot_result = _get_sql_glot(
        sql_string=sql_string_result.sql_string, path=path, sources=sources, error_builder=error_builder
    )
    if glot_result.errors:
        return ResolverResult(
            resolver=None,
            errors=glot_result.errors,
            db=None,
            fields=None,
            args=None,
        )

    parsed = _parse_glot(
        glot_result=glot_result,
        path=path,
        sources=sources,
        error_builder=error_builder,
        has_import_errors=has_import_errors,
    )
    if parsed.errors:
        return ResolverResult(
            resolver=None,
            errors=parsed.errors,
            db=parsed.source,
            fields=None,
            args=None,
        )

    # validate inputs and outputs as real features in graph
    inputs: List[Feature] = []
    for arg in glot_result.args.values():
        try:
            inputs.append(Feature.from_root_fqn(arg))
        except Exception:
            message = f"SQL file resolver references an input feature '{arg}' which does not exist."
            if arg in FeatureSetBase.registry:
                message += f" It appears '{arg}' is a feature class, not a feature."

            if not has_import_errors:
                error_builder.add_diagnostic(
                    message=message,
                    code="152",
                    label="input feature not recognized",
                    range=error_builder.variable_range_by_name(arg),
                )
                errors.append(
                    ResolverError(
                        display=message,
                        path=path,
                        parameter=arg,
                    )
                )
    outputs: List[Feature] = []
    query_fields: Dict[str, str] = {}
    for variable, output in parsed.fields.items():
        if output.endswith("*"):
            features = FeatureSetBase.registry[parsed.namespace].features
            for feature in features:
                if feature.is_scalar:
                    outputs.append(feature)
            continue

        unrecognized_output = False
        try:
            feature = Feature.from_root_fqn(output)
            outputs.append(feature)
            query_fields[variable] = output
        except Exception:
            if parsed.comment_dict.fields is not None:
                split = output.split(".", 1)
                namespace = split[0]
                output_name = split[1]
                if output_name in parsed.comment_dict.fields:
                    field = parsed.comment_dict.fields.get(output_name)
                    output = f"{namespace}.{field}"
                    try:
                        feature = Feature.from_root_fqn(output)
                        outputs.append(feature)
                        query_fields[output_name] = output
                    except:
                        unrecognized_output = True
                else:
                    unrecognized_output = True
            else:
                unrecognized_output = True
        if unrecognized_output:
            message = f"SQL file resolver references an output feature '{output}' which does not exist. "
            if not has_import_errors:
                value = output.split(".", 1)[1]
                error_builder.add_diagnostic(
                    message=message,
                    code="153",
                    label="output feature not recognized",
                    range=error_builder.value_range_by_name(glot_result.glot, value),
                )
                errors.append(
                    ResolverError(
                        display=message,
                        path=path,
                        parameter=output,
                    )
                )
    if len(outputs) == 0:
        message = (
            "SQL file resolver has no detected outputs. Make sure that all select outputs are aliased to features "
            "defined within the feature set referenced by the `resolves` parameter."
        )
        if has_import_errors:
            return ResolverResult(
                resolver=None,
                errors=[],
                db=parsed.source,
                fields=None,
                args=None,
            )
        error_builder.add_diagnostic(
            message=message,
            code="154",
            label="no outputs detected",
            range=error_builder.sql_range(),
        )
        errors.append(ResolverError(display=message, path=path, parameter=None))

    resolver_type_str = parsed.comment_dict.type if parsed.comment_dict.type else "online"
    resolver_type = _RESOLVER_TYPES[resolver_type_str]

    if resolver_type == StreamResolver:
        return _get_stream_resolver(path, glot_result, parsed, outputs, error_builder)

    incremental_dict = parsed.comment_dict.incremental.dict() if parsed.comment_dict.incremental else None
    return_one = parsed.comment_dict.count
    source = parsed.source
    assert isinstance(source, BaseSQLSource)

    # function for online resolver to process
    def fn(
        *input_values: Any,
        database: BaseSQLSource = source,
        sql_query: str = parsed.sql_string,
        field_dict: Dict[str, str] = query_fields,
        args_dict: Dict[str, str] = glot_result.args,
        incremental: Optional[Dict[str, Any]] = incremental_dict,
    ):
        arg_dict = {arg: input_value for input_value, arg in zip(input_values, args_dict.keys())}
        func = database.query_string(
            query=sql_query,
            fields=field_dict,
            args=arg_dict,
        )
        if incremental:
            func = func.incremental(**incremental)
        elif return_one in [1, "one"]:
            func = func.one()
        elif return_one == "one_or_none":
            func = func.one_or_none()
        return func

    if errors:
        return ResolverResult(
            resolver=None, errors=errors, db=parsed.source, fields=parsed.fields, args=glot_result.args
        )
    if return_one is None:
        # If the root ns of the inputs is the same as what is being resolved, then it is always return one
        input_root_namespace = get_unique_item_if_exists(x.root_namespace for x in inputs)
        output_root_namespace = get_unique_item(x.root_namespace for x in outputs)
        if input_root_namespace is not None and input_root_namespace == output_root_namespace:
            return_one = "one"

    if return_one:
        output = Features[tuple(outputs)]
    else:
        output = Features[DataFrame[tuple(outputs)]]

    default_args: List[Optional[ResolverArgErrorHandler]] = [
        None if default_value is ... else ResolverArgErrorHandler(default_value)
        for default_value in glot_result.default_args
    ]

    filename = os.path.basename(path)
    # attempt to instantiate the resolver
    try:
        assert resolver_type in (OnlineResolver, OfflineResolver)
        assert isinstance(parsed.source, BaseSQLSource)
        resolver = resolver_type(
            filename=path,
            function_definition=sql_string_result.sql_string,
            fqn=filename.replace(".chalk.sql", ""),
            doc=parsed.docstring,
            inputs=inputs,
            output=output,
            fn=fn,
            environment=parsed.comment_dict.environment,
            tags=parsed.comment_dict.tags,
            cron=parsed.comment_dict.cron,
            machine_type=parsed.comment_dict.machine_type,
            when=None,
            state=None,
            default_args=default_args,
            owner=parsed.comment_dict.owner,
            timeout=parsed.comment_dict.timeout,
            is_sql_file_resolver=True,
            data_sources=[parsed.source],
            name=None,
            source_line=None,
            lsp_builder=get_resolver_error_builder(fn),
        )
    except Exception as e:
        message = f"SQL file resolver '{resolver_type_str.capitalize()}'  could not be instantiated, {e}"
        error_builder.add_diagnostic(
            message=message,
            code="155",
            label="resolver instantiation failed",
            range=error_builder.full_range(),
        )
        errors.append(
            ResolverError(
                display=message,
                path=path,
                parameter=None,
            )
        )
        return ResolverResult(
            resolver=None, errors=errors, db=parsed.source, fields=parsed.fields, args=glot_result.args
        )

    return ResolverResult(
        resolver=resolver, errors=errors, db=parsed.source, fields=parsed.fields, args=glot_result.args
    )


def _get_sql_string(path: str) -> SQLStringResult:
    """Attempt to get a sql string from a filepath and gracefully exit if unable to"""

    if not path.endswith(".chalk.sql"):
        return SQLStringResult.fail(display_error=f"sql resolver file '{path}' must end in '.chalk.sql'", path=path)
    sql_string = None
    if os.path.isfile(path):
        with open(path) as f:
            sql_string = f.read()
    else:
        frame = inspect.currentframe()
        assert frame is not None
        caller_frame = frame.f_back
        assert caller_frame is not None
        caller_filename = inspect.getsourcefile(caller_frame)
        assert caller_filename is not None
        dir_path = os.path.dirname(os.path.realpath(caller_filename))
        if isinstance(path, bytes):
            path = path.decode("utf-8")
        relative_path = os.path.join(dir_path, path)
        if os.path.isfile(relative_path):
            with open(relative_path) as f:
                sql_string = f.read()
    if sql_string is None:
        return SQLStringResult.fail(display_error=f"Cannot find file '{path}'", path=path)
    return SQLStringResult(path=path, sql_string=sql_string, error=None)


def _get_sql_glot(
    sql_string: str, path: str, sources: Iterable[BaseSQLSource], error_builder: SQLFileResolverErrorBuilder
) -> GlotResult:
    """Get sqlglot from sql string and gracefully exit if unable to"""
    try:
        import sqlglot
        import sqlglot.errors
        import sqlglot.expressions
    except ImportError:
        raise missing_dependency_exception("chalkpy[runtime]")
    args = {}  # sql string -> input feature string
    variables = set(re.findall("\\${.*?\\}", sql_string))
    errors: List[ResolverError] = []
    default_args: List[Union[Optional[str], ellipsis]] = []
    # replace ?{variable_name} with :variable_name for sqlalchemy, and keep track of input args necessary
    for variable_pattern in variables:
        has_default_arg = False
        variable = variable_pattern[2:-1]  # cut off ${ and }
        for split_var in ["|", " or "]:  # default argument
            # TODO cannot parse something like {Transaction.category or "Waffles or Pancakes"} yet
            if split_var in variable:
                split = variable.split(split_var)
                if len(split) != 2:
                    message = (
                        f"If character '|' is used, both variable name and default value must be "
                        f"specified in '({variable})' like '?{{variable_name | \"default_value\"}}"
                    )
                    error_builder.add_diagnostic(
                        message=message,
                        code="140",
                        label="invalid variable",
                        range=error_builder.variable_range_by_name(variable),
                    )
                    errors.append(
                        ResolverError(
                            display=message,
                            path=path,
                            parameter=None,
                        )
                    )
                else:  # has default argument
                    variable = split[0].strip()
                    default_arg = split[1].strip()
                    default_arg = json.loads(default_arg)
                    f = Feature.from_root_fqn(variable)
                    default_arg = f.converter.from_json_to_rich(default_arg)
                    default_args.append(default_arg)
                    has_default_arg = True
        if not has_default_arg:
            default_args.append(...)
        period_replaced = variable.replace(".", "_")
        sql_safe_str = f"__chalk_{period_replaced}__"
        sql_string = sql_string.replace(variable_pattern, f":{sql_safe_str}")
        args[sql_safe_str] = variable
    comments = ""
    docstring = ""
    comment_row_to_file_row: Dict[int, int] = {}
    comment_row_offset: Dict[int, int] = {}
    comment_line_counter = 0
    """
    Comments and docstrings are required to be at the beginning of the file resolver.
    Thus, we need to make sure that for ranges, comments are mapped to the right line number
    as docstrings are not included in the comments variable above.

    We also need to keep track of the offset of the comment in order to properly detect the range.
    """
    for line_no, comment in enumerate(sql_string.splitlines()):
        if comment.strip().startswith("--"):
            stripped_comment = comment.strip().replace("--", "")
            comment_offset = len(comment) - len(stripped_comment)
            if stripped_comment.strip().startswith("-"):
                comments += f"{stripped_comment}\n"
            else:
                split = stripped_comment.split(":")
                if len(split) != 2:
                    docstring += f"{stripped_comment.strip()}\n"
                else:
                    comments += f"{stripped_comment}\n"
                    comment_row_to_file_row[comment_line_counter] = line_no
                    comment_row_offset[comment_line_counter] = comment_offset
                    comment_line_counter += 1
        else:
            break

    if len(comments) == 0:
        message = "SQL file resolvers require comments that describe key-value pairs in YAML form."
        error_builder.add_diagnostic(
            message=message,
            code="141",
            label="missing comments",
            range=error_builder.full_range(),
            code_href="https://docs.chalk.ai/docs/sql#sql-file-resolvers",
        )
        errors.append(
            ResolverError(
                display=message,
                path=path,
                parameter=None,
            )
        )
        return GlotResult(
            sql_string=sql_string,
            glot=None,
            args=args,
            default_args=default_args,
            comment_dict=None,
            docstring=docstring,
            errors=errors,
        )
    try:
        comment_dict: Dict[str, Any] = yaml.safe_load(comments)
    except Exception as e:
        message = f"SQL File resolver comments must have key-values in YAML form: {e}"
        if isinstance(e, ScannerError) and e.problem_mark is not None:
            comment_line_no = e.problem_mark.line
            comment_col_no = e.problem_mark.column
            file_line_no = comment_row_to_file_row[comment_line_no]
            file_comment_no = comment_row_offset[comment_line_no] + comment_col_no
            error_builder.add_diagnostic(
                message=message,
                code="142",
                label="Could not parse comments as YAML",
                range=error_builder.custom_range(line_no=file_line_no + 1, col=file_comment_no + 1),
            )

        errors.append(
            ResolverError(
                display=message,
                path=path,
                parameter=comments,
            )
        )
        return GlotResult(
            sql_string=sql_string,
            glot=None,
            args=args,
            default_args=default_args,
            comment_dict=None,
            docstring=docstring,
            errors=errors,
        )
    if "source" not in comment_dict:
        """This would be caught by the following BaseModel.parse_obj() but the error message is bad"""
        message = (
            f"The datasource is a required field for SQL file resolvers. "
            f"Please add a comment ' -- source: my_name'  where 'my_name' refers to a named integration. "
        )
        error_builder.add_diagnostic(
            message=message,
            code="143",
            label="missing source",
            range=error_builder.full_comment_range(),
            code_href="https://docs.chalk.ai/docs/integrations",
        )
        errors.append(
            ResolverError(
                display=message,
                path=path,
                parameter=json.dumps(comment_dict),
            )
        )
        return GlotResult(
            sql_string=sql_string,
            glot=None,
            args=args,
            default_args=default_args,
            comment_dict=None,
            docstring=docstring,
            errors=errors,
        )
    if "resolves" not in comment_dict:
        """This would be caught by the following BaseModel.parse_obj() but the error message is bad"""
        message = (
            f"A feature class must be specified for SQL file resolvers. "
            f"Please add a comment ' -- resolves: my_name'  where 'my_name' refers to a feature class."
        )
        error_builder.add_diagnostic(
            message=message,
            code="144",
            label="missing feature class",
            range=error_builder.full_comment_range(),
            code_href="https://docs.chalk.ai/docs/integrations",
        )
        errors.append(
            ResolverError(
                display=message,
                path=path,
                parameter=json.dumps(comment_dict),
            )
        )
        return GlotResult(
            sql_string=sql_string,
            glot=None,
            args=args,
            default_args=default_args,
            comment_dict=None,
            docstring=docstring,
            errors=errors,
        )

    try:
        comment_dict_object = CommentDict.parse_obj(comment_dict)
    except ValidationError as e:
        for error in e.errors():
            location = error["loc"][-1]  # the innermost error
            message = f"SQL file resolver could not validate comment '{location}': {error['msg']}"
            range = error_builder.comment_range_by_key(str(location))
            if range is None and location in IncrementalSettings.__fields__:
                range = error_builder.comment_range_by_key("incremental")
            error_builder.add_diagnostic(
                message=message,
                code="145",
                label="Could not validate comment",
                range=range,
            )
            errors.append(
                ResolverError(
                    display=message,
                    path=path,
                    parameter=json.dumps(comment_dict),
                )
            )
        return GlotResult(
            sql_string=sql_string,
            glot=None,
            args=args,
            default_args=default_args,
            comment_dict=None,
            docstring=docstring,
            errors=errors,
        )
    docstring = docstring.strip()

    source_comment = comment_dict_object.source
    source_type = None
    if source_comment not in _SOURCES:  # actual name of source
        for possible_source in sources:
            if possible_source.name == source_comment and isinstance(possible_source, BaseSQLSource):
                # Note: it is apparently possible for non-BaseSQLSources to be passed here, including
                # e.g. `KafkaSource`.
                source_type = (
                    possible_source.get_sqlglot_dialect()
                )  # dialect may be unsupported, in which case this returns `None`
    else:
        if source_comment in _SQLGLOT_DIALECTS:  # source type, if supported
            source_type = source_comment
    try:
        glots = sqlglot.parse(sql=sql_string, read=source_type)
    except Exception as e:
        message = f"SQL file resolver could not SQL parse string: {e}"
        if isinstance(e, sqlglot.errors.ParseError):
            for error in e.errors:
                error_builder.add_diagnostic(
                    message=message,
                    code="146",
                    label="could not parse SQL",
                    range=error_builder.custom_range(
                        line_no=error["line"], col=error["col"] - 2, length=len(error["highlight"])  # ????
                    ),
                )
        errors.append(ResolverError(display=message, path=path, parameter=None))
        return GlotResult(
            sql_string=sql_string,
            glot=None,
            args=args,
            default_args=default_args,
            comment_dict=comment_dict_object,
            docstring=docstring,
            errors=errors,
        )
    if len(glots) > 1:
        message = f"SQL file resolver query {sql_string} has more than one 'SELECT' statements. Only one is permitted."
        error_builder.add_diagnostic(
            message=message,
            code="147",
            label="SQL query must be a single SELECT statement",
            range=error_builder.sql_range(),
        )
        errors.append(ResolverError(display=message, path=path, parameter=None))
        return GlotResult(
            sql_string=sql_string,
            glot=None,
            args=args,
            default_args=default_args,
            comment_dict=comment_dict_object,
            docstring=docstring,
            errors=errors,
        )
    glot = glots[0]
    if not isinstance(glot, sqlglot.expressions.Select):
        message = f"SQL file resolver query {sql_string} should be of 'SELECT' type"
        error_builder.add_diagnostic(
            message=message,
            code="147",
            label="SQL query must be a SELECT statement",
            range=error_builder.sql_range(),
        )
        errors.append(ResolverError(display=message, path=path, parameter=None))
        return GlotResult(
            sql_string=sql_string,
            glot=None,
            args=args,
            default_args=default_args,
            comment_dict=comment_dict_object,
            docstring=docstring,
            errors=errors,
        )
    if len(glot.selects) > len(glot.named_selects):
        for select in glot.selects:
            matched = False
            for named_select in glot.named_selects:
                if select.alias_or_name == named_select:
                    matched = True
            if not matched:
                message = (
                    f"SQL file resolver query with unnamed select '{str(select)}'. "
                    f"All selects must either match a feature name, e.g. 'id', or must be aliased, e.g. "
                    f"'SELECT COUNT (DISTINCT merchant_id) AS num_unique_merchant_ids. "
                    f"All names/aliases must match to features on the feature set defined "
                    f"by the 'resolves' comment parameter. "
                )
                error_builder.add_diagnostic(
                    message=message,
                    code="148",
                    label="all selects must map to features",
                    range=error_builder.value_range_by_name(glot=glot, name=str(select).lower()),
                )
                errors.append(
                    ResolverError(
                        display=message,
                        path=path,
                        parameter=None,
                    )
                )
    return GlotResult(
        sql_string=sql_string,
        glot=glot,
        args=args,
        default_args=default_args,
        comment_dict=comment_dict_object,
        docstring=docstring,
        errors=errors,
    )


def _parse_glot(
    glot_result: GlotResult,
    path: str,
    sources: Iterable[BaseSQLSource],
    error_builder: SQLFileResolverErrorBuilder,
    has_import_errors: bool,
) -> ParseResult:
    """Parse useful info from sqlglot and gracefully exit if unable to"""
    try:
        import sqlglot
        import sqlglot.expressions
    except ImportError:
        raise missing_dependency_exception("chalkpy[runtime]")
    # define a source SQL database. Can either specify name or kind if only one of the kind is present.
    comment_dict = glot_result.comment_dict
    assert comment_dict is not None
    docstring = glot_result.docstring
    source_name = comment_dict.source
    source = None
    errors: List[ResolverError] = []
    if source_name not in _SOURCES:  # actual name of source
        for possible_source in sources:
            if possible_source.name == source_name:
                source = possible_source
    else:
        for possible_source in sources:
            source_type = _SOURCES.get(source_name)
            if source_type is not None and isinstance(possible_source, source_type):
                if source:
                    message = (
                        f"SQL file resolver refers to '{source_name}' when more than one {source_name}-type source "
                        f"exists. Instead, refer to the integration by name among "
                        f"({[source.name for source in sources]})."
                    )
                    error_builder.add_diagnostic(
                        message=message,
                        code="149",
                        label="Refer to source via name instead",
                        range=error_builder.comment_range_by_key("source"),
                    )
                    errors.append(
                        ResolverError(
                            display=message,
                            path=path,
                            parameter=source_name,
                        )
                    )
                source = possible_source
    if not source:
        message = (
            f"SQL file resolver refers to unrecognized source '{source_name}'. "
            f"Please refer to your source via its name on your Chalk dashboard."
        )
        if not has_import_errors:
            error_builder.add_diagnostic(
                message=message,
                code="150",
                label="Source not found",
                range=error_builder.comment_range_by_key("source"),
            )
            errors.append(
                ResolverError(
                    display=message,
                    path=path,
                    parameter=source_name,
                )
            )
    # get resolver fields: which columns selected will match to which chalk feature?
    namespace = comment_dict.resolves
    if namespace not in FeatureSetBase.registry:
        snaked_namespace = to_snake_case(namespace)
        if snaked_namespace in FeatureSetBase.registry:
            namespace = snaked_namespace
        else:
            message = f"No @features class with the name '{namespace}'"
            error_builder.add_diagnostic(
                message=message,
                code="151",
                label="Unrecognized namespace ",
                range=error_builder.comment_range_by_key("resolves"),
            )
            errors.append(ResolverError(display=message, path=path, parameter=source_name))

    if len(errors) > 0:
        return ParseResult(
            sql_string=glot_result.sql_string,
            comment_dict=comment_dict,
            fields={},
            namespace=namespace,
            source=source,
            docstring=docstring,
            errors=errors,
        )

    assert isinstance(glot_result.glot, sqlglot.expressions.Select)
    # sql target -> output feature string
    fields: Dict[str, str] = {
        column_name: f"{namespace}.{column_name}" for column_name in glot_result.glot.named_selects
    }

    return ParseResult(
        sql_string=glot_result.sql_string,
        comment_dict=comment_dict,
        fields=fields,
        namespace=namespace,
        source=source,
        docstring=docstring,
        errors=errors,
    )


def _get_stream_resolver(
    path: str,
    glot_result: GlotResult,
    parsed: ParseResult,
    outputs: List[Feature],
    error_builder: SQLFileResolverErrorBuilder,
) -> ResolverResult:
    errors = []
    output_features = Features[DataFrame[tuple(outputs)]]

    if isinstance(output_features.features[0], type) and issubclass(output_features.features[0], DataFrame):
        output_feature_fqns = set(f.fqn for f in cast(Type[DataFrame], output_features.features[0]).columns)
    else:
        output_feature_fqns = set(f.fqn for f in output_features.features)

    signature = StreamResolverSignature(
        params=[],
        output_feature_fqns=output_feature_fqns,
    )

    sql_query: str = _remove_comments(parsed.sql_string)
    filename = os.path.basename(path)
    assert isinstance(parsed.source, StreamSource)

    try:

        def fn():
            return sql_query

        # attempt to instantiate the resolver
        resolver = StreamResolver(
            function_definition=sql_query,
            fqn=filename.replace(".chalk.sql", ""),
            filename=path,
            source=parsed.source,
            fn=fn,
            environment=parsed.comment_dict.environment,
            doc=parsed.docstring,
            mode=None,
            machine_type=parsed.comment_dict.machine_type,
            message=None,
            output=output_features,
            signature=signature,
            state=None,
            sql_query=sql_query,
            owner=parsed.comment_dict.owner,
            parse=None,
            keys=None,  # TODO implement parse and keys for sql file resolvers?
            timestamp=None,
            source_line=None,
            name=None,
            tags=None,
            lsp_builder=get_resolver_error_builder(fn),
        )
    except Exception as e:
        message = f"Streaming SQL file resolver could not be instantiated, {e}"
        error_builder.add_diagnostic(
            message=message,
            code="141",
            label="resolver instantiation failed",
            range=error_builder.full_range(),
        )
        errors.append(
            ResolverError(
                display=message,
                path=path,
                parameter=None,
            )
        )
        return ResolverResult(resolver=None, errors=errors, db=parsed.source, fields=None, args=None)

    return ResolverResult(
        resolver=resolver,
        errors=errors,
        db=parsed.source,
        fields=parsed.fields,
        args=glot_result.args,
    )


def _remove_comments(sql_string: str) -> str:
    sql_string = re.sub(
        re.compile("/\\*.*?\\*/", re.DOTALL), "", sql_string
    )  # remove all occurrences streamed comments (/*COMMENT */) from string
    sql_string = re.sub(
        re.compile("//.*?\n"), "", sql_string
    )  # remove all occurrence single-line comments (//COMMENT\n ) from string
    sql_string = re.sub(
        re.compile("--.*?\n"), "", sql_string
    )  # remove all occurrence single-line comments (//COMMENT\n ) from string
    return sql_string.strip()

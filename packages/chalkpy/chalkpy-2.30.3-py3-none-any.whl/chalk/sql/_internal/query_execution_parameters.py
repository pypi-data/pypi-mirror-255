from dataclasses import dataclass

from chalk.utils.environment_parsing import env_var_bool


@dataclass(frozen=True)
class PostgresQueryExecutionParameters:
    attempt_efficient_postgres_execution: bool
    """
    Overrides QueryExecutionParameters.attempt_efficient_parameters if True
    """

    polars_read_csv: bool
    """
    When `attempt_postgres_efficient_execution` is True, this flag decides whether to use polars'
    read_csv or pyarrow's read_csv.
    """

    csv_read_then_cast: bool
    """
    When `attempt_postgres_efficient_execution` is True, another flag that may help
    to accommodate unzoned timestamps in postgres. This happens AFTER the sql query.
    """

    skip_datetime_timezone_cast: bool
    """
    skip datetime timezone casting, only under efficient execution. This happens BEFORE the sql query.
    """


@dataclass(frozen=True)
class QueryExecutionParameters:
    attempt_efficient_execution: bool
    """
    This will be overriden at query time if the source is a postgres source and
    PostgresQueryExecutionParameters.attempt_efficient_postgres_execution is True in the invoker
    """

    postgres: PostgresQueryExecutionParameters


def query_execution_parameters_from_env_vars():
    """
    For when called in user resolver code.
    If you do not want to do efficient execution, set CHALK_FORCE_SQLALCHEMY_QUERY_EXECUTION_WITHOUT_EXCEPTION to True
    """
    return QueryExecutionParameters(
        attempt_efficient_execution=True,
        postgres=PostgresQueryExecutionParameters(
            attempt_efficient_postgres_execution=True,
            polars_read_csv=env_var_bool("CHALK_FORCE_POLARS_READ_CSV"),
            csv_read_then_cast=env_var_bool("CSV_READ_THEN_CAST"),
            skip_datetime_timezone_cast=env_var_bool("CHALK_SKIP_PG_DATETIME_ZONE_CAST"),
        ),
    )

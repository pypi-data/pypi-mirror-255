import ascend.protos.component.component_pb2 as component
import ascend.protos.function.function_pb2 as function
import ascend.protos.io.io_pb2 as io
import ascend.protos.operator.operator_pb2 as operator

from ascend.sdk import definitions

import re
import click

def create_transform(
    id,
    sql,
    inputs,
    description,
    custom_dq_test_sql=None,
    reduction="no-reduction",
    language="snowflake-sql",
):
    """
    Create Ascend transform component from dbt model.
    """
    input_ids = [x.split(".")[-1] for x in inputs]

    # In sql, find all the occurrences of the input nodes with DB name and schema name using regex as per the following example
    # Example input: select * from XXX.YYY.customer_revenue_by_month
    # Example output: select * from {{ customer_revenue_by_month }}
    prev_sql = sql
    sql = translate_sql(language=language, sql=sql, input_ids=input_ids)

    # If no substitutions were made, display the error and exit
    # Ascend does not allow a transform to have no inputs
    if sql == prev_sql:
        print(
            f"No inputs replaced in the file {id}.sql. Please check the file and try again."
        )
        exit(1)

    # Create transform component
    # TODO: Add support for other SQL flavours
    # TODO: Add support for other partition reduction options
    return definitions.Transform(
        id=id,
        name=id,
        description=description,
        input_ids=input_ids,
        operator=operator.Operator(
            spark_function=operator.Spark.Function(
                executable=io.Executable(
                    code=io.Code(
                        language=get_language(language),
                        source=io.Code.Source(
                            inline=sql,
                        ),
                    ),
                ),
                reduction=get_reduction(reduction_method=reduction),
                tests=define_quality_tests(custom_dq_test_sql),
            ),
        ),
        assigned_priority=component.Priority(),
    )


def get_language(type):
    """
    Get the language for the transform component.
    """

    if type == "snowflake-sql":
        return function.Code.Language(
            snowflake_sql=function.Code.Language.SnowflakeSql()
        )
    
    if type == "bigquery-sql":
        return function.Code.Language(
            bigquery_sql=function.Code.Language.BigQuerySql()
        )

    if type == "databricks-sql":
        return function.Code.Language(
            databricks_sql=function.Code.Language.DatabricksSql()
        )

    raise Exception(f"Language type {type} not supported.")


def get_reduction(reduction_method):
    """
    Get the reduction method for the transform component.
    """

    if reduction_method == "no-reduction":
        return operator.Reduction(
            no_reduction=operator.Reduction.NoReduction(),
        )
    elif reduction_method == "full-reduction":
        return operator.Reduction(full=operator.Reduction.Full())
    else:
        raise Exception(f"Reduction method {reduction_method} not supported.")

def translate_sql(language, sql, input_ids):
    """
    Translate the SQL to replace the input nodes with Ascend placeholders.
    """
    for input in input_ids:

        # Fix to remove all "`" characters from 3 part names
        sql = re.sub(r"`([\w\-]+)`\.`([\w\-]+)`\.`({})`".format(input), r"\1.\2.\3", sql, flags=re.IGNORECASE)

        sql = re.sub(r"[\w\-]+\.[\w\-]+\.({})".format(input), lambda m: "{{{{{}}}}}".format(m.group(1).lower()), sql, flags=re.IGNORECASE)
        
    return sql.strip()


# TODO: Add support for standard checks
def define_quality_tests(custom_dq_test_sql):
    """
    Define quality tests for a transform component. Only supports no checks and custom checks.
    """

    if custom_dq_test_sql is None:
        return function.QualityTests()

    return function.QualityTests(
        custom=[
            function.QualityTests.CustomCheck(
                sql=custom_dq_test_sql.strip(),
            )
        ]
    )

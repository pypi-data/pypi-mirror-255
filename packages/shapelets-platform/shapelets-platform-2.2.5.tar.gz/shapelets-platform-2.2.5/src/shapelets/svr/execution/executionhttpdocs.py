from blacksheep.server.openapi.common import EndpointDocs, ParameterInfo

__tags = ["Execution"]

run_execution = EndpointDocs(
    summary="Run Bind Execution",
    description=
    """ 
    Invoke the serialization function and return its output. This method is called by the UI to retrieve the
    generated widget resulting from a bound execution.
    """,
    tags=__tags,
    parameters={"fn": ParameterInfo("json FunctionProfile")}
)

table_data = EndpointDocs(
    summary="Retrieve table data",
    description=
    """
    Retrieve the specified data from a table. This method is invoked by the UI to obtain the next page of the table.
    """,
    tags=__tags,
    parameters={
        "table": ParameterInfo("table id", str),
        "fromRow": ParameterInfo("starting row", int),
        "n": ParameterInfo("amount of rows to retrieve", int)
    }
)

create_data = EndpointDocs(
    summary="Create table",
    description=
    """ 
    Given a serialized Arrow Table and an identifier (ID), store the table in a file using the ID as the filename.
    """,
    tags=__tags,
    parameters={
        "table_id": ParameterInfo("table id", str),
        "data": ParameterInfo("serialized arrow table", str)
    }
)

__all__ = ['run_execution', 'table_data', 'create_data']

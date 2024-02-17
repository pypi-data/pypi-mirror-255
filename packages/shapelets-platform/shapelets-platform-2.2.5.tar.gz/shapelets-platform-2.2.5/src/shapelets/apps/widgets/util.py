import base64
import numpy as np
import pandas as pd
import pyarrow as pa
import os

from typing import Union

from ... import DataSet

SH_DIR = os.path.expanduser('~/.shapelets')
DATA_DIR = os.path.join(SH_DIR, 'data')


def write_arrow_file(arrow_table: pa.Table, uid: str):
    _write_arrow_file(arrow_table, uid)


def serialize_table(table: pa.Table) -> str:
    return _serialize_table(table)


def create_arrow_table(data: Union[pd.DataFrame, DataSet], preserve_index: bool = False) -> pa.Table:
    return _create_arrow_table(data, preserve_index)


def read_from_arrow_file(file_name: str, from_row: int = 0, n: int = 10) -> pa.Table:
    return _read_from_arrow_file(file_name, from_row, n)


def to_utf64_arrow_buffer(data: Union[pd.DataFrame, DataSet, pa.Table], preserve_index: bool = True) -> str:
    if isinstance(data, (DataSet, pd.DataFrame, pa.Table)):
        return _to_utf64_arrow_buffer(data, preserve_index)
    raise TypeError("Invalid type.")


def _to_utf64_arrow_buffer(data: Union[pd.DataFrame, DataSet, pa.Table], preserve_index: bool = True) -> str:
    """
    Transform pandas dataframe or Shapelets dataset to an arrow buffer
    """
    if isinstance(data, pd.DataFrame):
        # df = dataframe.astype(float)
        table = pa.Table.from_pandas(data, preserve_index=preserve_index)
    elif isinstance(data, DataSet):
        table = data.to_arrow_table(1024)
    elif isinstance(data, pa.Table):
        table = data

    sink = pa.BufferOutputStream()
    with pa.ipc.RecordBatchFileWriter(sink, table.schema) as writer:
        writer.write(table)
    buffer = sink.getvalue()
    return base64.b64encode(buffer).decode("utf-8")


def _to_utf64_arrow_buffer_numpy(array: np.ndarray) -> str:
    parray = pa.array(array.flatten())
    batch = pa.record_batch([parray], names=["values"])
    sink = pa.BufferOutputStream()
    with pa.ipc.RecordBatchFileWriter(sink, batch.schema) as writer:
        writer.write(batch)
    buffer = sink.getvalue()
    return base64.b64encode(buffer).decode("utf-8")


def _to_utf64_arrow_buffer_series(series: pd.Series) -> str:
    parray = pa.Array.from_pandas(series)
    batch = pa.record_batch([parray], names=["values"])
    sink = pa.BufferOutputStream()
    with pa.ipc.RecordBatchFileWriter(sink, batch.schema) as writer:
        writer.write(batch)
    buffer = sink.getvalue()
    return base64.b64encode(buffer).decode("utf-8")


def _create_arrow_table(data: Union[pd.DataFrame, DataSet], preserve_index: bool = False) -> pa.Table:
    """
    Convert a Pandas DataFrame or a Shapelets Dataset into an Arrow Table.
    """
    if isinstance(data, pd.DataFrame):
        try:
            table = pa.Table.from_pandas(data, preserve_index=preserve_index)
        except (pa.ArrowTypeError, pa.ArrowInvalid):
            # When a pandas dataframe has multiple types in a col like int, str, etc. is defined as dtype object in pandas.
            # However, arrow does not have cols with multiple types, therefore if we catch the exception ArrowTypeError,
            # or ArrowInvalid, we try to identify the col name and convert it to string.
            table = None
            for col_name in data.columns:
                if data[col_name].dtype == "object":
                    data[col_name] = data[col_name].astype(str)
                try:
                    # Check if only that col failed. Avoid converting to string those columns that don't fail.
                    table = pa.Table.from_pandas(data, preserve_index=preserve_index)
                    break
                except (pa.ArrowTypeError, pa.ArrowInvalid):
                    continue
            if table is None:
                # Desperate solution. If by any chance we could not convert the table properlty, convert all the types
                # to string. (We should never get to this point)
                data = data.astype(str)
                table = pa.Table.from_pandas(data, preserve_index=preserve_index)

    elif isinstance(data, DataSet):
        table = data.to_arrow_table(1024)
    elif isinstance(data, pd.Series):
        arrow_array = pa.array(data)
        table = pa.Table.from_arrays([arrow_array], names=[data.name])
    return table


def _write_arrow_file(table: pa.Table, uid: str):
    """
    Persist the data from an Arrow Table by storing it in within a file.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, uid)

    sink = pa.BufferOutputStream()
    with pa.ipc.RecordBatchFileWriter(sink, table.schema) as writer:
        writer.write(table)
    buffer = sink.getvalue()
    with open(path, 'wb') as sink:
        sink.write(buffer)


def _read_from_arrow_file(file_name: str, from_row: int = 0, n: int = 10) -> pa.Table:
    path = os.path.join(DATA_DIR, file_name)
    with open(path, "rb") as file:
        reader = pa.ipc.open_file(file)
        table = reader.read_all()
    return table


def _serialize_table(table: pa.Table):
    sink = pa.BufferOutputStream()
    with pa.ipc.RecordBatchFileWriter(sink, table.schema) as writer:
        writer.write(table)
    buffer = sink.getvalue()
    return base64.b64encode(buffer).decode("utf-8")

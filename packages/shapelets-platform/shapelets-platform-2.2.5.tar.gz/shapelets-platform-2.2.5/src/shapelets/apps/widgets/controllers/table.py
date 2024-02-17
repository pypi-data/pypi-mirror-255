from __future__ import annotations

import numpy as np
import pandas as pd
import random
import shapelets as sh
import string
import uuid

from typing import List, Union, Optional, Tuple
from typing_extensions import Literal
from dataclasses import dataclass

from ..state_control import StateControl
from ..widget import AttributeNames, Widget

from ..util import create_arrow_table, read_from_arrow_file, serialize_table, to_utf64_arrow_buffer, write_arrow_file
from ....svr import get_service, IExecutionService, server_or_client


@dataclass
class Condition:
    column: int
    type: Literal["case", "range"]
    conditions: List[dict]

    def to_dict(self):
        return {
            AttributeNames.COLUMN.value: self.column,
            AttributeNames.TYPE.value: self.type,
            AttributeNames.CONDITION.value: self.conditions,
        }


@dataclass
class Table(StateControl):
    data: Optional[Union[pd.DataFrame, sh.DataSet]] = None
    title: Optional[str] = None
    rows_per_page: Optional[int] = None
    tools_visible: Optional[bool] = True
    conditional_formats: Optional[List[Union[Condition, dict]]] = None
    date_format: Optional[str] = None

    def __post_init__(self):
        if not hasattr(self, "widget_id"):
            self.widget_id = str(uuid.uuid1())
        # if self.data is not None and isinstance(self.data, (pd.DataFrame, sh.DataSet)):
        #     self._save_data_and_return()

    def _save_data_and_return(self, host: str = None) -> str:
        # Save table information and returns the initial data for the UI
        server = server_or_client()
        # self.table_file_id = str(uuid.uuid1())
        # Convert data to pa.Table
        arrow_table = create_arrow_table(data=self.data, preserve_index=False)
        if not server:
            # client execution, get server
            serialize_data = to_utf64_arrow_buffer(arrow_table)
            exec_svc = get_service(IExecutionService, host)
            exec_svc.save_table(self.widget_id, serialize_data)
            initial_data = exec_svc.table_data(self.widget_id, 0, 10).decode('utf-8')
        else:
            # Server running, call the actual function
            write_arrow_file(arrow_table, self.widget_id)
            initial_data = self.read_from_arrow_file_and_ser(self.widget_id)

        # Relate arrow file with the dataApp
        if hasattr(self, "parent_data_app") and self.parent_data_app is not None:
            self.parent_data_app._data.append(self.widget_id)

        # return first 10 rows to include them in the spec
        return initial_data

    def replace_widget(self, new_widget: Table):
        """
        Replace the current values of the widget for the values of a similar widget type.
        """
        self.data = new_widget.data
        self.title = new_widget.title
        self.rows_per_page = new_widget.rows_per_page
        self.tools_visible = new_widget.tools_visible
        self.conditional_formats = new_widget.conditional_formats
        self.date_format = new_widget.date_format

    def get_current_value(self):
        """
        Return the current value of the widget. Return None is the widget value is not set.
        """
        if self.data is not None:
            return self.data
        return None

    def from_dataframe(self, data: pd.DataFrame) -> Table:
        self.data = data
        return self

    def to_dataframe(self) -> pd.DataFrame:
        dataframe = self.data
        return dataframe

    def from_dataset(self, data: sh.DataSet) -> Table:
        self.data = data
        return self

    def to_dataset(self) -> sh.DataSet:
        dataset = self.data
        return dataset

    def from_list(self, lista: list) -> Table:
        self.data = lista
        return self

    def to_list(self) -> list:
        lista = self.data.values.tolist() if self.data is not None else []
        return lista

    def to_utf64_arrow_buffer(self) -> str:
        """
        Mainly for testing.
        """
        return to_utf64_arrow_buffer(data=self.data, preserve_index=False)

    @staticmethod
    def read_from_arrow_file_and_ser(table_file_id: str) -> str:
        table = read_from_arrow_file(table_file_id)
        return serialize_table(table)

    @staticmethod
    def generate_short_uuid(length=8):
        characters = string.ascii_letters + string.digits
        short_uuid = ''.join(random.choice(characters) for _ in range(length))
        return short_uuid

    def to_dict_widget(self, table_dict: dict = None, host: str = None):
        if table_dict is None:
            table_dict = {
                AttributeNames.ID.value: self.widget_id,
                AttributeNames.TYPE.value: Table.__name__,
                AttributeNames.DRAGGABLE.value: self.draggable,
                AttributeNames.RESIZABLE.value: self.resizable,
                AttributeNames.DISABLED.value: self.disabled,
                AttributeNames.PROPERTIES.value: {}
            }
        if self.data is not None:
            if isinstance(self.data, (pd.DataFrame, sh.DataSet)):
                # Add size of the dataset
                table_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.TOTAL_ROWS.value: len(self.data)
                })
                # Add file ID to recover its file
                table_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.ID.value: self.widget_id
                })
                # Set column names
                if isinstance(self.data.columns, pd.MultiIndex):
                    summary_col_names = []
                    parent_title = {}
                    # Ensure that each column is uniquely identified by keeping track of its index.
                    index = 0
                    # Accumulate cols name to check for duplicates
                    cols_so_far = set()
                    for item in self.data.columns:
                        parent_name, item_title = item
                        # If the parent is not already in the dictionary, add it.
                        # Avoid sending unnamed cols name
                        if parent_name not in parent_title:
                            new_parent_name = parent_name if parent_name and "Unnamed:" not in parent_name else None
                            parent_title[parent_name] = {
                                "key": index,
                                "title": new_parent_name,
                                "children": []
                            }
                            index += 1

                        child_title = item_title
                        # Add Conditional formats
                        con_type = None
                        conditions = None
                        if self.conditional_formats is not None:
                            for condition in self.conditional_formats:
                                if isinstance(condition, Condition):
                                    if condition.column == child_title:
                                        con_type = condition.type
                                        conditions = condition.conditions
                                elif condition["column"] == child_title:
                                    con_type = condition["type"]
                                    conditions = condition["conditions"]

                        while child_title in cols_so_far:
                            child_title = f"{child_title}_{self.generate_short_uuid()}"
                            self.data.columns = pd.MultiIndex.from_tuples(
                                [(level[0], child_title) if level == item else level for level in
                                 self.data.columns]
                            )
                        else:
                            cols_so_far.add(child_title)

                        child_dict = {
                            "key": index,
                            "title": item_title,
                            "dataIndex": child_title
                        }
                        index += 1
                        summary_col_names.append(child_title)

                        if con_type is not None:
                            child_dict.update({
                                "conditionalType": con_type
                            })
                        if conditions is not None:
                            child_dict.update({
                                "conditions": conditions
                            })
                        parent_title[parent_name]["children"].append(child_dict)
                    # Convert the dictionary values to a list
                    cols = list(parent_title.values())

                    table_dict[AttributeNames.PROPERTIES.value].update({
                        AttributeNames.COLS.value: cols
                    })
                    table_dict[AttributeNames.PROPERTIES.value].update({
                        "multiIndexCol": True
                    })
                    table_dict[AttributeNames.PROPERTIES.value].update({
                        "allColNames": summary_col_names
                    })
                else:
                    column_names = list(self.data.columns)
                    if self.conditional_formats is None:
                        cols = []
                        for index, col in enumerate(column_names):
                            cols.append({
                                "title": col,
                                "dataIndex": col,
                                "key": index
                            })
                        table_dict[AttributeNames.PROPERTIES.value].update({
                            AttributeNames.COLS.value: cols
                        })
                    else:
                        # Set column names for conditionals
                        cols = []
                        for index, col in enumerate(column_names):
                            col_dict = {
                                "title": col,
                                "dataIndex": col,
                                "key": index
                            }

                            for condition in self.conditional_formats:
                                if isinstance(condition, dict):
                                    if condition["column"] not in column_names:
                                        raise "Condition column not in table data"
                                    if condition["column"] == col:
                                        col_dict["conditionalType"] = condition["type"]
                                        col_dict["conditions"] = condition["conditions"]
                                elif isinstance(condition, Condition):
                                    if condition.column not in column_names:
                                        raise "Condition column not in table data"
                                    if condition.column == col:
                                        col_dict["conditionalType"] = condition.type
                                        col_dict["conditions"] = condition.conditions
                            cols.append(col_dict)

                        table_dict[AttributeNames.PROPERTIES.value].update({
                            AttributeNames.COLS.value: cols
                        })

                # Save data and load 10 first rows
                arrow_data = self._save_data_and_return(host)
                table_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.DATA.value: arrow_data
                })

                if isinstance(self.data, pd.DataFrame):
                    table_dict[AttributeNames.PROPERTIES.value].update({
                        AttributeNames.COL_TYPES.value: [str(x) for x in self.data.dtypes]
                    })
                elif isinstance(self.data, sh.DataSet):
                    table_dict[AttributeNames.PROPERTIES.value].update({
                        AttributeNames.COL_TYPES.value: [str(x) for x in self.data.describe().column_type]
                    })

            else:
                raise ValueError("Data type not supported")

        if self.title is not None:
            if isinstance(self.title, str):
                table_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.TITLE.value: self.title
                })

        if self.rows_per_page is not None:
            if isinstance(self.rows_per_page, int):
                table_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.ROWS_PER_PAGE.value: self.rows_per_page
                })

        if self.tools_visible is not None:
            if isinstance(self.tools_visible, bool):
                table_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.TOOLS_VISIBLE.value: self.tools_visible
                })

        if self.date_format is not None:
            if isinstance(self.date_format, str):
                table_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.FORMAT.value: self.date_format
                })

        return table_dict


class TableWidget(Table, Widget):

    def __init__(self,
                 data: Optional[Union[pd.DataFrame, sh.DataSet]] = None,
                 title: Optional[str] = None,
                 rows_per_page: Optional[int] = None,
                 tools_visible: Optional[bool] = True,
                 conditional_formats: Optional[List[Union[Condition, dict]]] = None,
                 date_format: Optional[str] = None,
                 **additional):
        Widget.__init__(self, Table.__name__,
                        compatibility=tuple(
                            [pd.DataFrame.__name__, np.ndarray.__name__, list.__name__, Table.__name__]),
                        **additional)
        Table.__init__(self,
                       data=data,
                       title=title,
                       rows_per_page=rows_per_page,
                       tools_visible=tools_visible,
                       conditional_formats=conditional_formats,
                       date_format=date_format)
        self._parent_class = Table.__name__
        self._compatibility: Tuple = (pd.DataFrame.__name__,
                                      np.ndarray.__name__,
                                      list.__name__,
                                      Table.__name__,
                                      sh.DataSet.__name__)

    def to_dict_widget(self, host: str = None):
        table_dict = Widget.to_dict_widget(self)
        table_dict = Table.to_dict_widget(self, table_dict, host)
        return table_dict

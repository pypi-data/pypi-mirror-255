from __future__ import annotations

import numpy as np

from dataclasses import dataclass
from typing import  List, Union

from ..layouts import HorizontalLayoutWidget, VerticalLayoutWidget

@dataclass
class Column:

    n_columns: Union[int, List[float]] = 2 
    layout: HorizontalLayoutWidget = None # Se inicia a None y no a HL para poder bindearlo despues
    cols: List[VerticalLayoutWidget] = None
    max_cols: int = 24

    # Accessor para poder acceder a los VLayouts y poder hacer place dentro.
    # x = Column()
    # x[0].place() <- x[0] es un VLayout
    def __getitem__(self,index):
        return self.cols[index]

    def __post_init__(self):
        self._check_data()

    def _check_data(self):
        if self.n_columns is None:
            raise ValueError("No parameters provided")

        self.layout = HorizontalLayoutWidget()
        self.widget_id = self.layout.widget_id
        self.cols = []

        if isinstance(self.n_columns, int):
            for i in range(self.n_columns):
                v = VerticalLayoutWidget(span=round(self.max_cols/self.n_columns))
                self.layout.place(v)
                self.cols.append(v)

        elif isinstance(self.n_columns, List):
            n_columns = self._ratios_to_columns(self.n_columns, self.max_cols)
            for i in range(len(self.n_columns)):
                v = VerticalLayoutWidget(span=n_columns[i])
                self.layout.place(v)
                self.cols.append(v)
        else:
            raise TypeError("No available for that type.")


    def _ratios_to_columns(self,aspect_ratio, max_cols=24):
        if sum(aspect_ratio) != 1.0:
            raise ValueError("Percentages must add up to 1.0")

        result_floats = [fraction * max_cols for fraction in aspect_ratio]
        columns = [np.ceil(num) for num in result_floats]
        adjustment = max_cols - sum(columns)
        columns[np.argmax(columns)] += adjustment

        return columns

    def to_dict_widget(self):
        return self.layout.to_dict_widget()
        


class ColumnWidget(Column):
    """
    Creates a layout where widgets are arranged side by side horizontally.
    """

    def __init__(self,
                 n_columns: Union[int, list] = 2,
                **additional):
        Column.__init__(self,n_columns=n_columns)

    def to_dict_widget(self ):
        column_dict = Column.to_dict_widget(self)
        return column_dict    

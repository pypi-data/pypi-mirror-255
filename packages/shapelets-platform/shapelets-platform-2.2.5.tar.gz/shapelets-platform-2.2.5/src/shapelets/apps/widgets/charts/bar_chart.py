from __future__ import annotations

import uuid
import numpy as np
import pandas as pd

from dataclasses import dataclass
from typing import Any, List, Literal, Optional, Union

from ..state_control import StateControl
from ..widget import Widget, AttributeNames

from .... import DataSet


@dataclass
class BarChart(StateControl):
    data: Optional[Union[pd.DataFrame, DataSet]] = None
    x: Optional[Union[List[Any], List[np.array]]] = None
    y: Optional[Union[List[Any], List[np.array]]] = None
    y_axis_orientation: Literal["right", "left"] = "left"
    x_name: Optional[str] = None
    y_name: Optional[str] = None
    title: Optional[str] = None
    legend: Optional[Union[str, List[Any]]] = None

    def __post_init__(self):
        self.bar_orientation = "vertical"
        self._check_data()
        if not hasattr(self, "widget_id"):
            self.widget_id = str(uuid.uuid1())

    def _check_data(self):
        if self.data is not None:
            if isinstance(self.data, DataSet):
                self.data = self.data.to_pandas()
            if isinstance(self.data, pd.DataFrame):
                melted_df = pd.melt(self.data.reset_index(), id_vars='index', var_name='category', value_name='y')
                self.data = melted_df.to_dict(orient='records')
        if self.x is not None and self.y is not None:
            if isinstance(self.y, list) and all(isinstance(sublist, list) for sublist in self.y):
                data = []
                for i, category in enumerate(self.x):
                    for j, value in enumerate(self.y[i]):
                        data.append({"category": category, "y": value, "index": j})
                self.data = data
                self.bar_orientation = "vertical"

            elif isinstance(self.x, list) and all(isinstance(sublist, list) for sublist in self.x):
                # Horizontal
                data = []
                for i, category in enumerate(self.y):
                    for j, value in enumerate(self.x[i]):
                        data.append({"category": category, "y": value, "index": j})
                self.data = data
                self.bar_orientation = "horizontal"

            elif isinstance(self.y, list) and all(isinstance(sublist, (int, float, str)) for sublist in self.y):
                self.data = [{'category': category, 'y': value, 'index': 0} for category, value in zip(self.x, self.y)]
                self.bar_orientation = "vertical"

            elif isinstance(self.x, np.ndarray) and isinstance(self.y, np.ndarray):
                result_list = []
                for i, category in enumerate(self.x):
                    for j, value in enumerate(self.y[i]):
                        result_list.append({"category": category, "y": str(value), "index": j})

                self.data = result_list

    def from_dataframe(self, dataframe: pd.DataFrame) -> BarChart:
        self.data = dataframe
        self._check_data()
        return self

    def replace_widget(self, new_widget: BarChart):
        """
        Replace the current values of the widget for the values of a similar widget type.
        """
        self.data = new_widget.data
        self.x = new_widget.x
        self.y = new_widget.y
        self.y_axis_orientation = new_widget.y_axis_orientation
        self.x_name = new_widget.x_name
        self.y_name = new_widget.y_name
        self.title = new_widget.title
        self.bar_orientation = new_widget.bar_orientation

    def get_current_value(self):
        """
        Return the current value of the widget. Return None is the widget value is not set.
        """
        if self.data is not None:
            return self.data
        if self.x is not None and self.y is not None:
            return [self.x, self.y]
        return None

    def to_dict_widget(self, bar_dict: dict = None):
        if bar_dict is None:
            bar_dict = {
                AttributeNames.ID.value: self.widget_id,
                AttributeNames.TYPE.value: BarChart.__name__,
                AttributeNames.DRAGGABLE.value: self.draggable,
                AttributeNames.RESIZABLE.value: self.resizable,
                AttributeNames.DISABLED.value: self.disabled,
                AttributeNames.PROPERTIES.value: {}
            }
        # Widget providers are used when the value of a different widget must be set inside an attribute.
        _widget_providers = []
        if self.data is not None:
            bar_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.DATA.value: self.data
            })

        if self.title is not None:
            if isinstance(self.title, str):
                bar_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.TITLE.value: self.title
                })
            elif isinstance(self.title, Widget):
                target = {"id": self.title.widget_id, "target": "title"}
                _widget_providers.append(target)
            else:
                raise ValueError(f"Error Widget {self.widget_type}: Title value should be a string or another widget")

        if self.y_axis_orientation is not None:
            if isinstance(self.y_axis_orientation, str):
                bar_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.Y_AXIS_ORIENTATION.value: self.y_axis_orientation.lower()
                })
            elif isinstance(self.y_axis_orientation, Widget):
                target = {"id": self.y_axis_orientation.widget_id, "target": "yAxisOrientation"}
                _widget_providers.append(target)
            else:
                raise ValueError(
                    f"Error Widget {self.widget_type}: y_axis_orientation value should be a string or another widget")

        if self.x_name is not None:
            if isinstance(self.x_name, str):
                bar_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.X_TITLE.value: self.x_name
                })
            elif isinstance(self.x_name, Widget):
                target = {"id": self.x_name.widget_id, "target": "xTitle"}
                _widget_providers.append(target)
            else:
                raise ValueError(f"Error Widget {self.widget_type}: x_name value should be a string or another widget")

        if self.y_name is not None:
            if isinstance(self.y_name, str):
                bar_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.Y_TITLE.value: self.y_name
                })
            elif isinstance(self.y_name, Widget):
                target = {"id": self.y_name.widget_id, "target": "yTitle"}
                _widget_providers.append(target)
            else:
                raise ValueError(f"Error Widget {self.widget_type}: y_name value should be a string or another widget")

        if self.bar_orientation is not None:
            if isinstance(self.bar_orientation, str):
                bar_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.BAR_ORIENTATION.value: self.bar_orientation
                })
        if self.legend is not None:
            bar_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.LEGEND.value: self.legend
            })

        if _widget_providers:
            self.add_widget_providers(bar_dict, _widget_providers)

        return bar_dict


axis_type = Union[List[int], List[float], List[str], List[np.array]]


class BarChartWidget(Widget, BarChart):
    def __init__(self,
                 data: Optional[Union[pd.DataFrame, DataSet]] = None,
                 x: Optional[Union[List[Any], List[np.array]]] = None,
                 y: Optional[Union[List[Any], List[np.array]]] = None,
                 y_axis_orientation: Literal["right", "left"] = "left",
                 x_name: Optional[str] = None,
                 y_name: Optional[str] = None,
                 title: Optional[str] = None,
                 legend: Optional[Union[Any, List[Any]]] = None,
                 **additional):
        if data is not None and (x is not None or y is not None):
            raise ValueError("Parameter data is incompatible with x_axis and y_axis.")

        Widget.__init__(self, BarChart.__name__,
                        compatibility=tuple([BarChart.__name__, pd.DataFrame.__name__]),
                        **additional)
        BarChart.__init__(self, data=data, x=x, y=y, y_axis_orientation=y_axis_orientation,
                          x_name=x_name, y_name=y_name, title=title, legend=legend)
        self._parent_class = BarChart.__name__

    def to_dict_widget(self):
        bar_dict = Widget.to_dict_widget(self)
        bar_dict = BarChart.to_dict_widget(self, bar_dict)
        return bar_dict

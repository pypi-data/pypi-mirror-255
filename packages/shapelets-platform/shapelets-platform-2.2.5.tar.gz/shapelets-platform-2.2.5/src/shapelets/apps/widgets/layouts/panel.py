from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from ..charts import LineChart
from ..controllers import Table
from ..state_control import StateControl
from ..widget import Widget, AttributeNames


@dataclass
class Panel(StateControl):
    panel_title: Optional[str] = None
    panel_id: Optional[str] = None
    widgets: Optional[List[Widget]] = field(default_factory=lambda: [])


class PanelWidget(Widget, Panel):
    """
    Container + Layout: a Panel is a plain layout where widgets can be placed.
    """

    def __init__(self,
                 panel_title: Optional[str] = None,
                 panel_id: Optional[str] = None,
                 compatibility: tuple = None,
                 **additional
                 ):
        Widget.__init__(self, widget_type=self._parent_class,
                        widget_id=panel_id, compatibility=compatibility, **additional)
        Panel.__init__(self, panel_title=panel_title)

    def _place(self, *widget: Tuple[Widget, ...]):
        self.widgets.extend(widget)

    def to_dict_widget(self, host: str = None):
        panel_dict = super().to_dict_widget()
        if self.widgets is not None:
            widgets = []
            for widget in self.widgets:
                if isinstance(widget, (LineChart, Table)):
                    widgets.append(widget.to_dict_widget(host))
                else:
                    widgets.append(widget.to_dict_widget())
            # widgets = [widget.to_dict_widget() for widget in self.widgets]
            panel_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.WIDGETS.value: widgets
            })
        if self.panel_title:
            panel_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.TITLE.value: self.panel_title
            })
        return panel_dict

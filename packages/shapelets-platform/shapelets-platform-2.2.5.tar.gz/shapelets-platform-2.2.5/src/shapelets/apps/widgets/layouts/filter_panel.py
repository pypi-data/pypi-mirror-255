from dataclasses import dataclass
from typing import List, Optional

import uuid

from ..charts import LineChart
from ..controllers import Table
from ..widget import Widget, AttributeNames
from .panel import PanelWidget, Panel


@dataclass
class FilterPanel(Panel):
    """
    Creates a fixed panel collapsible on left side
    
    Parameters
    ----------
    title : str, optional
        Text associated to the Ring.

    width : int, float, optional
        Param to indicate the width on left panel

    Returns
    -------
    filterPanel.

    Examples
    
    title: Optional[str] = None
    width: Optional[int] = 300,
    widgets: Optional[List[Widget]] = field(default_factory=lambda: [])
  

    """
    def place(self, widget: Widget, width: Optional[float] = None, offset: Optional[int] = None):
        """
        Place widget inside layout
        param widget: widget to place.
        param width: understood as a percentage.
        param offset: distance with the next widget.
        """
        if width is not None and width < 100:
            raise Exception("Width can be over a 100")
        self.widgets.append(widget)
        self.width = width
        self.placements[widget.widget_id] = (width, offset)

    def to_dict_widget(self, host: str = None):
        panel_dict = {
            AttributeNames.ID.value: self.panel_id if self.panel_title else str(uuid.uuid1()),
            AttributeNames.DRAGGABLE.value: self.draggable,
            AttributeNames.RESIZABLE.value: self.resizable,
            AttributeNames.DISABLED.value: self.disabled,
            AttributeNames.PROPERTIES.value: {}
        }
        if self.panel_title is not None:
            panel_dict[AttributeNames.PROPERTIES.value].update({
                "panel_title": self.panel_title
            })

        if self.placements is not None:
            panel_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.PLACEMENTS.value: [{
                    AttributeNames.WIDGET_REF.value: key,
                    AttributeNames.WIDTH.value: width,
                    AttributeNames.OFFSET.value: offset
                } for key, (width, offset) in self.placements.items()]
            })

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

        if self.width is not None:
            panel_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.WIDTH.value: self.width
            })
            

        return panel_dict        
        
class FilterPanelWidget(PanelWidget):
    """
    Container + Layout: a Panel fixed collapsible  that holds widget inside it vertically (stacked on-top of one another).
    """

    def __init__(self,
                 panel_title: Optional[str] = None,
                 panel_width: Optional[int] = None,
                 panel_id: Optional[str] = None,
                 **additional):
        self._parent_class = FilterPanel.__name__
        super().__init__(panel_title, panel_id,
                         compatibility=tuple([list.__name__, List._name, FilterPanel.__name__]),
                         **additional)
        self.panel_width = panel_width
        self.placements = dict()

    def place(self, widget: Widget, width: Optional[int] = None, offset: Optional[int] = None):
        """
        Place widget inside layout
        param widget: widget to place.
        param width: understood as a percentage.
        param offset: distance with the next widget.
        """
        if width is not None and width > 100:
            raise Exception("Width cant be over a 100")
        super()._place(widget)
        self.width = width
        self.placements[widget.widget_id] = (width, offset)

    def to_dict_widget(self, host: str = None):
        panel_dict = super().to_dict_widget(host)
        panel_dict[AttributeNames.PROPERTIES.value].update({
            AttributeNames.PLACEMENTS.value: [{
                AttributeNames.WIDGET_REF.value: key,
                AttributeNames.WIDTH.value: width,
            } for key, (width, offset) in self.placements.items()]
        })
        if self.panel_width is not None:
            panel_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.WIDTH.value: self.panel_width
            })
                                
        
        return panel_dict

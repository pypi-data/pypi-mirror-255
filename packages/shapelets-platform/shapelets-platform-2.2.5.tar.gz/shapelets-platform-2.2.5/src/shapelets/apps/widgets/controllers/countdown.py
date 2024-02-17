from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Union
from typing_extensions import Literal

from ..state_control import StateControl
from ..widget import Widget, AttributeNames


@dataclass
class CountDown(StateControl):
    """

    Creates a CountDown for your dataApp.

    Parameters
    ----------

    duration : int , optional
        Defines how often the Timer is executed in seconds | milliseconds.

    start_delay : int, optional
        Defines a start delay for the Timer.

    unit : str 's' or 'ms', optional
        Defines the unit of timer secods or millisencods

    Returns
    -------
    countdown

    Examples
    --------
    >>> countdown = app.countdown(duration=5, start_delay=20)


    """
    duration: Optional[int] = None
    start_delay: Optional[int] = None
    unit: Optional[Literal["s","ms"]] = "s"

    def from_string(self, string: str) -> CountDown:
        self.title = string
        return self

    def to_string(self) -> str:
        return str(self.duration)

    def from_int(self, number: int) -> CountDown:
        self.duration = number
        return self

    def to_int(self) -> int:
        return int(self.duration)


class CountDownWidget(Widget, CountDown):
    def __init__(self,
                 duration: Union[int, float] = None,
                 start_delay: Optional[int] = None,
                 unit: Optional[Literal["s","ms"]] = "s",
                 **additional):
        Widget.__init__(self, CountDown.__name__,
                        compatibility=tuple([str.__name__, int.__name__, float.__name__, CountDown.__name__]),
                        **additional)
        CountDown.__init__(self,  duration=duration, start_delay=start_delay, unit=unit)
        self._parent_class = CountDown.__name__

    def to_dict_widget(self):
        timer_dict = super().to_dict_widget()
        # Widget providers are used when the value of a different widget must be set inside an attribute.
        _widget_providers = []

        if self.duration is not None:
            if isinstance(self.duration, (int, float)):
                timer_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.DURATION.value: self.duration
                })
            elif isinstance(self.duration, Widget):
                target = {"id": self.every.widget_id, "target": AttributeNames.DURATION.duration}
                _widget_providers.append(target)
            else:
                raise ValueError(f"Error Widget {self.widget_type}: duration value should be a int")

        if self.start_delay is not None:
            if isinstance(self.start_delay, int):
                timer_dict[AttributeNames.PROPERTIES.value].update({
                    AttributeNames.START_DELAY.value: self.start_delay
                })
            elif isinstance(self.start_delay, Widget):
                target = {"id": self.start_delay.widget_id, "target": AttributeNames.START_DELAY.value}
                _widget_providers.append(target)
            else:
                raise ValueError(
                    f"Error Widget {self.widget_type}: Start Delay value should be a int or another widget")

        if self.unit is not None:
            if not isinstance(self.unit, str):
                raise ValueError(f"Error Widget {self.widget_type}: unit value should be a str 's' or 'ms'")
            
            # Ahora que sabemos que es una cadena, comprobamos el valor
            if self.unit not in ("s", "ms"):
                raise ValueError(f"Error Widget {self.widget_type}: unit value should be 's' or 'ms'")
            
            # Si llegamos aquí, la unidad es una cadena y tiene un valor válido
            timer_dict[AttributeNames.PROPERTIES.value].update({
                AttributeNames.UNIT.value: self.unit
            })
            

        if _widget_providers:
            self.add_widget_providers(timer_dict, _widget_providers)

        return timer_dict

    @staticmethod
    def bind():
        raise AttributeError("Button widget does not allow bind")

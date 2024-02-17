from dataclasses import dataclass

"""
Class to control share attributes between widgets. Every widget import this class.
"""


@dataclass
class StateControl:
    disabled: bool = False
    draggable: bool = False
    resizable: bool = False
    placeholder: str = None

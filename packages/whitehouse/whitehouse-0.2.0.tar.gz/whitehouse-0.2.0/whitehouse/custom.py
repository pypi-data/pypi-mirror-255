from .base import Component
from typing import List, Dict, Union



class Template(Component):
    def __init__(self, component: Component) -> None:
        super().__init__(component)

    def __str__(self) -> str:
        return self.children

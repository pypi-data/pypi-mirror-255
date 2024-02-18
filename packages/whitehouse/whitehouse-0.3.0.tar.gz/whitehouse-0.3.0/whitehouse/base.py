from typing import List, Dict, Union


class Component:
    def __init__(self, children: Union[str, 'Component', List['Component']], attributes: Dict[str, str] = {}) -> None:
        if isinstance(children, str):
            self.children = children
        elif isinstance(children, Component):
            self.children = str(children)
        elif isinstance(children, list):
            self.children = ''.join([str(child) for child in children])
        else:
            raise ValueError(f"Invalid type {type(children)} for children")

        if len(attributes) > 0:
            self.attributes = f''' {" ".join([f'{key}="{value}"' for key, value in attributes.items()])}'''
        else:
            self.attributes = ""
    
    def __str__(self) -> str:
        return f"""
        <{type(self).__name__}{self.attributes}>
            {self.children}
        </{type(self).__name__}>
        """

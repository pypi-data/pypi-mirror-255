from .base import Component
from typing import List, Dict, Union



class a(Component):
    def __init__(self, children: Union[str, 'Component', List['Component']], attributes: Dict[str, str] = {}) -> None:
        super().__init__(children, attributes)

class body(Component):
    def __init__(self, children: Union[str, 'Component', List['Component']], attributes: Dict[str, str] = {}) -> None:
        super().__init__(children, attributes)
    
class br(Component):
    def __init__(self, attributes: Dict[str, str] = {}) -> None:
        super().__init__("", attributes)

    def __str__(self) -> str:
        return f"""
        <br{self.attributes}/>
        """
    
class button(Component):
    def __init__(self, text: str, attributes: Dict[str, str] = {}) -> None:
        super().__init__(text, attributes)

class div(Component):
    def __init__(self, children: Union[str, 'Component', List['Component']], attributes: Dict[str, str] = {}) -> None:
        super().__init__(children, attributes)

class p(Component):
    def __init__(self, text: str, attributes: Dict[str, str] = {}) -> None:
        super().__init__(text, attributes)
    
class footer(Component):
    def __init__(self, children: Union[str, 'Component', List['Component']], attributes: Dict[str, str] = {}) -> None:
        super().__init__(children, attributes)
        
class form(Component):
    def __init__(self, children: Union[str, 'Component', List['Component']], attributes: Dict[str, str] = {}) -> None:
        super().__init__(children, attributes)

class img(Component):
    def __init__(self, attributes: Dict[str, str]) -> None:
        super().__init__("", attributes)
    
    def __str__(self) -> str:
        return f"""
        <img{self.attributes}/>
        """

class h1(Component):
    def __init__(self, text: str, attributes: Dict[str, str] = {}) -> None:
        super().__init__(text, attributes)

class h2(Component):
    def __init__(self, text: str, attributes: Dict[str, str] = {}) -> None:
        super().__init__(text, attributes)

class h3(Component):
    def __init__(self, text: str, attributes: Dict[str, str] = {}) -> None:
        super().__init__(text, attributes)

class h4(Component):
    def __init__(self, text: str, attributes: Dict[str, str] = {}) -> None:
        super().__init__(text, attributes)

class h5(Component):
    def __init__(self, text: str, attributes: Dict[str, str] = {}) -> None:
        super().__init__(text, attributes)

class h6(Component):
    def __init__(self, text: str, attributes: Dict[str, str] = {}) -> None:
        super().__init__(text, attributes)

class head(Component):
    def __init__(self, children: Union[str, 'Component', List['Component']]) -> None:
        super().__init__(children)
    
class header(Component):
    def __init__(self, children: Union[str, 'Component', List['Component']], attributes: Dict[str, str] = {}) -> None:
        super().__init__(children, attributes)

class hgroup(Component):
    def __init__(self, children: Union[str, 'Component', List['Component']], attributes: Dict[str, str] = {}) -> None:
        super().__init__(children, attributes)

class hr(Component):
    def __init__(self, attributes: Dict[str, str] = {}) -> None:
        super().__init__("", attributes)
    
    def __str__(self) -> str:
        return f"""
        <hr{self.attributes}/>
        """

class html(Component):
    def __init__(self, children: Union[str, 'Component', List['Component']]) -> None:
        super().__init__(children)
    
    def __str__(self) -> str:
        return f"""
        <!DOCTYPE html>
        <html>
            {self.children}
        </html>
        """
    
class li(Component):
    def __init__(self, text: str, attributes: Dict[str, str] = {}) -> None:
        super().__init__(text, attributes)

class link(Component):
    def __init__(self, attributes: Dict[str, str]) -> None:
        super().__init__("", attributes)
    
    def __str__(self) -> str:
        return f"""
        <link{self.attributes}/>
        """

class meta(Component):
    def __init__(self, attributes: Dict[str, str]) -> None:
        super().__init__("", attributes)
    
    def __str__(self) -> str:
        return f"""
        <meta{self.attributes}/>
        """

class nav(Component):
    def __init__(self, children: Union[str, 'Component', List['Component']], attributes: Dict[str, str] = {}) -> None:
        super().__init__(children, attributes)

class script(Component):
    def __init__(self, text: str, attributes: Dict[str, str] = {}) -> None:
        super().__init__(text, attributes)
    
class svg(Component):
    def __init__(self, children: Union[str, 'Component', List['Component']], attributes: Dict[str, str] = {}) -> None:
        super().__init__(children, attributes)

class section(Component):
    def __init__(self, children: Union[str, 'Component', List['Component']], attributes: Dict[str, str] = {}) -> None:
        super().__init__(children, attributes)

class table(Component):
    def __init__(self, children: Union[str, 'Component', List['Component']], attributes: Dict[str, str] = {}) -> None:
        super().__init__(children, attributes)

class tbody(Component):
    def __init__(self, children: Union[str, 'Component', List['Component']], attributes: Dict[str, str] = {}) -> None:
        super().__init__(children, attributes)

class td(Component):
    def __init__(self, text: str, attributes: Dict[str, str] = {}) -> None:
        super().__init__(text, attributes)

class template(Component):
    def __init__(self, children: Union[str, 'Component', List['Component']], attributes: Dict[str, str] = {}) -> None:
        super().__init__(children, attributes)

class textarea(Component):
    def __init__(self, text: str, attributes: Dict[str, str] = {}) -> None:
        super().__init__(text, attributes)

class tfoot(Component):
    def __init__(self, children: Union[str, 'Component', List['Component']], attributes: Dict[str, str] = {}) -> None:
        super().__init__(children, attributes)

class th(Component):
    def __init__(self, text: str, attributes: Dict[str, str] = {}) -> None:
        super().__init__(text, attributes)

class thead(Component):
    def __init__(self, children: Union[str, 'Component', List['Component']], attributes: Dict[str, str] = {}) -> None:
        super().__init__(children, attributes)

class time(Component):
    def __init__(self, text: str, attributes: Dict[str, str] = {}) -> None:
        super().__init__(text, attributes)

class title(Component):
    def __init__(self, text: str) -> None:
        super().__init__(text)
    
class tr(Component):
    def __init__(self, children: Union[str, 'Component', List['Component']], attributes: Dict[str, str] = {}) -> None:
        super().__init__(children, attributes)

class track(Component):
    def __init__(self, attributes: Dict[str, str]) -> None:
        super().__init__("", attributes)
    
    def __str__(self) -> str:
        return f"""
        <track{self.attributes}/>
        """

class u(Component):
    def __init__(self, text: str, attributes: Dict[str, str] = {}) -> None:
        super().__init__(text, attributes)

class ul(Component):
    def __init__(self, children: Union[str, 'Component', List['Component']], attributes: Dict[str, str] = {}) -> None:
        super().__init__(children, attributes)

class var(Component):
    def __init__(self, text: str, attributes: Dict[str, str] = {}) -> None:
        super().__init__(text, attributes)

class video(Component):
    def __init__(self, children: Union[str, 'Component', List['Component']], attributes: Dict[str, str]) -> None:
        super().__init__(children, attributes)

class wbr(Component):
    def __init__(self, attributes: Dict[str, str] = {}) -> None:
        super().__init__("", attributes)

    def __str__(self) -> str:
        return f"""
        <wbr{self.attributes}/>
        """
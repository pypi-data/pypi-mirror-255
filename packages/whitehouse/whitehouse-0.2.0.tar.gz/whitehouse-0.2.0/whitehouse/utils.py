from bs4 import BeautifulSoup
from typing import List, Union
from .base import Component


def format_html(components: Union[Component, List[Component]]) -> str:
    # Convert the component to a string
    if isinstance(components, list):
        html_str = ''.join([str(component) for component in components])
    else:
        html_str = str(components)

    # Parse the HTML string with BeautifulSoup
    soup = BeautifulSoup(html_str, 'html.parser')

    # Use the prettify() method to add indentation
    formatted_html = soup.prettify()

    return formatted_html

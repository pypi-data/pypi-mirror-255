# Whitehouse
Welcome to the Whitehouse HTML Components library. 8-) 😏

### Installation:
```
pip install whitehouse
```

### The whitehouse library:
There are only four important files (i.e., modules) in this library (seriously... that's it... that's all there is to it...):
##### base.py
There is not much to this library. The ```Component``` class in ```base.py``` is the base class that is responsible for constructing the tag for the element. The ```Component``` class simply takes two arguments ```children``` (a list of child components) and ```attributes``` (a dictionary of HTML attributes to put on the element). The ```Component``` simply recursively calls the ```str()``` function to render all of its child components and then places the attributes into the element.

##### default.py
A library of all of the basic HTML5 elements codified as components.

##### utils.py
A library that provides functionalities such as formatting the rendered HTML into a more aethetically pleasing format. 

##### template.py
Defines a ```Template``` class that you can use to create component templates. Use the ```Template``` class when you need to create a template that includes the ```html``` component.

### Example Usage:
This is how you can use whitehouse to create your own HTML components:
```python
from whitehouse.default import *
from whitehouse.custom import CustomComponent
from whitehouse.utils import format_html

class MyComponent(CustomComponent):
    def __init__(
        self, 
        child1: Union[str, 'Component', List['Component']], 
        child2: Union[str, 'Component', List['Component']], 
        properties: Dict[str, str] = {}
    ) -> None:
        super().__init__([
            div([
                p("Hello, World 1!"),
                child1
            ], {"class": "container"}),
            div([
                p("Hello, World 2!"),
                child2
            ], {"class": "container"})
        ], properties=properties)


if __name__ == "__main__":
    component = html([
        head([
            title("Hello, World!"),
            meta({"charset": "UTF-8", "name": "viewport", "content": "width=device-width, initial-scale=1.0"}),
            link({"rel": "stylesheet", "href": "style.css"}),
            script("", {"src": "script.js"})
        ]),
        body([
            MyComponent(
                p("Hello, World 3!"), 
                p("Hello, World 4!"), 
                {"id": "custom-component1"}
            ),
            MyComponent(
                p("Hello, World 5!"), 
                p("Hello, World 6!"), 
                {"id": "custom-component2"}
            ),
            script("console.log('Hello, World!');")
        ])
    ])

    print(format_html(component))
```
Output HTML:
```html
<!DOCTYPE html>
<html>
 <head>
  <title>
   Hello, World!
  </title>
  <meta charset="utf-8" content="width=device-width, initial-scale=1.0" name="viewport"/>
  <link href="style.css" rel="stylesheet"/>
  <script src="script.js">
  </script>
 </head>
 <body>
  <mycomponent id="custom-component1">
   <div class="container">
    <p>
     Hello, World 1!
    </p>
    <p>
     Hello, World 3!
    </p>
   </div>
   <div class="container">
    <p>
     Hello, World 2!
    </p>
    <p>
     Hello, World 4!
    </p>
   </div>
  </mycomponent>
  <mycomponent id="custom-component2">
   <div class="container">
    <p>
     Hello, World 1!
    </p>
    <p>
     Hello, World 5!
    </p>
   </div>
   <div class="container">
    <p>
     Hello, World 2!
    </p>
    <p>
     Hello, World 6!
    </p>
   </div>
  </mycomponent>
  <script>
   console.log('Hello, World!');
  </script>
 </body>
</html>
```
Example usage #2:
```python
fragments = format_html([
    MyComponent(
        p("Hello, World 3!"), 
        p("Hello, World 4!"), 
        {"id": "custom-component1"}
    ),
    MyComponent(
        p("Hello, World 5!"), 
        p("Hello, World 6!"), 
        {"id": "custom-component2"}
    )
])
print(fragments)
```
Output:
```html
<mycomponent id="custom-component1">
 <div class="container">
  <p>
   Hello, World 1!
  </p>
  <p>
   Hello, World 3!
  </p>
 </div>
 <div class="container">
  <p>
   Hello, World 2!
  </p>
  <p>
   Hello, World 4!
  </p>
 </div>
</mycomponent>
<mycomponent id="custom-component2">
 <div class="container">
  <p>
   Hello, World 1!
  </p>
  <p>
   Hello, World 5!
  </p>
 </div>
 <div class="container">
  <p>
   Hello, World 2!
  </p>
  <p>
   Hello, World 6!
  </p>
 </div>
</mycomponent>
```
As you can see, no need for Jinja2 or any templating library necessary. 

#### Advantages of using whitehouse:
1. Extremely lightweight: ```whitehouse``` has only 1 dependency, BeautifulSoup4, that is it.
2. Easy to understand: it is fairly easy to see what HTML code will be generated from whitehouse Components. Obviously it is not as easy to see the HTML code that will be created by custom components so as a best practice, keep your custom components simple. In short, create and use custom components at your own peril.
3. No need to create template files: all rendering is done in python.
4. Create documentation: you can write PEP8 style documentation and type hints to describe the parameters and tell users how to use your custom components/templates.
5. More compatible with code editors: by creating documentation for your components, your users will be able to see the documentation for you custom components/templates through their code editors.
6. Ease of distribution: package your components/templates and its corresponding js and css files into your python package and then share it with other developers.
7. Encapsulation: in the case of using Jinja2 and a web framework (e.g., FastAPI), if your template is inheriting another template, you may have to provide not just the data for the current template, but also its parent template. With ```whitehouse``` components, you can create a custom component that provides the parent component with the data it needs once and then you can reuse the custom component and provide only the necessary data for the custom component. 

#### Disadvantages of using whitehouse:
1. Whitehouse currently doesn't support all HTML elements (see ```default.py``` for a list of all available HTML elements). This is mostly just because I'm too lazy to add support for every single HTML element out there. With that said, creating an element is super easy (again, see how to do it in ```default.py```) so feel free to create a branch and add your own elements in there, I promise I won't be too lazy to merge it into the main branch.

#### Jinja2 vs whitehouse Comparison:
##### For loops:
```html
{% for record in records %}
<div id="record.id">{{ record.content }}</div>
{% endfor }
```
```python
format_html(
    [div(record.content, {"id": record.id}) for record in records]
)
```
##### Conditionals:
```html
{% if is_open == True %}
    <button class=".open_btn">open</button>
{% else %}
    <button class=".close_btn">close</button>
{% endif %}
```
```python
format_html(
    button("open", {"class": ".open_btn"}) if is_open is True else button("close", {"class": ".close_btn"})
)
```
##### Template inheritance:
Parent template:
```html
<!DOCTYPE html>
<html>
    <head>
        <title>Hello, World!</title>
        <meta charset="utf-8" content="width=device-width, initial-scale=1.0" name="viewport"/>
    </head>
    <body>
    {% block body %}{% endblock %}
    </body>
</html>
```
Child template:
```html
{% extends "base.html" %}

{% block body %}
<mycomponent id="custom-component1">
    <div class="container">
        <p>Hello, World 1!</p>
        <p>Hello, World 3!</p>
    </div>
    <div class="container">
        <p>Hello, World 2!</p>
        <p>Hello, World 4!</p>
    </div>
</mycomponent>
{% endblock %}
```
Output:
```html
<!DOCTYPE html>
<html>
    <head>
        <title>Hello, World!</title>
        <meta charset="utf-8" content="width=device-width, initial-scale=1.0" name="viewport"/>
    </head>
    <body>
        <mycomponent id="custom-component1">
            <div class="container">
                <p>Hello, World 1!</p>
                <p>Hello, World 3!</p>
            </div>
            <div class="container">
                <p>Hello, World 2!</p>
                <p>Hello, World 4!</p>
            </div>
        </mycomponent>
    </body>
</html>
```
template class:
```python
from whitehouse.custom import Template

class IndexTemplate(Template):
    def __init__(self, body_content: Component) -> None:
        super().__init__(
            html([
                head([
                    title("Hello, World!"),
                    meta({"charset": "UTF-8", "name": "viewport", "content": "width=device-width, initial-scale=1.0"}),
                ]),
                body([
                    body_content
                ])
            ])
        )

index_template = IndexTemplate(
    MyComponent(p("Hello, World 3!"), p("Hello, World 4!"), {"id": "custom-component1"})
)
print(format_html(index_template))
```
Output:
```html
<!DOCTYPE html>
<html>
 <head>
  <title>
   Hello, World!
  </title>
  <meta charset="utf-8" content="width=device-width, initial-scale=1.0" name="viewport"/>
 </head>
 <body>
  <mycomponent id="custom-component1">
   <div class="container">
    <p>
     Hello, World 1!
    </p>
    <p>
     Hello, World 3!
    </p>
   </div>
   <div class="container">
    <p>
     Hello, World 2!
    </p>
    <p>
     Hello, World 4!
    </p>
   </div>
  </mycomponent>
 </body>
</html>
```

### Why I built this library:
I created this library because I needed a way of distributing HTML templates across a number of users of the Anacostia Pipeline. 

What I used to do was I packaged the Jinja2 templates into the Anacostia Pipeline package as ```package_data``` and then publish the package onto PyPI. From there, users of Anacostia would have to use the ```pkg_resources``` library to extract the templates from the package and then create their own child templates. The architecture and development philosophy of Anactostia emphasized enabling developers to build their own Anacostia nodes *and* the custom frontends to provide visualization for their nodes (i.e., I wanted developers to be able to create custom dashboards for their nodes). Enabling this development philosophy would require a server-side rendering approach where developers would create a FastAPI sub-application that would interact with their node(s), render the information of the nodes in an html fragment, and then the html fragment would be inserted into the DOM via [htmx](https://htmx.org/). This approach was promising but since I was using [FastAPI](https://fastapi.tiangolo.com), this approach presented a problem: only one directory can be defined for the main application, thus, users simply could not just create their own templates directory and then mount their templates directory into their sub-application which would then be recognized by the main application. Therefore, a more user-friendly approach was needed. 

The solution I decided upon was to create a library to render HTML fragments using only python which would not require the use of Jinja2 nor any templating directories that needed to be mounted into the FastAPI sub-application. Distribution of the fragments could be done by packaging the code for the fragments inside the Anacostia Pipeline package where the user could simply import the fragments into their python development environment. From there, the FastAPI sub-applications could simply render the templates during runtime and return the html snippets as the response to htmx requests.
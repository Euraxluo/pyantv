# coding:utf8

import warnings
import json
import os
from jinja2 import Template, FileSystemLoader, Environment
from typing import Any, Optional, Sequence, Tuple, Union, AnyStr

Numeric = Union[int, float]
from base.base import MacroElement, Figure, Element, JavascriptLink, CssLink
from base.options import BasicOpts, BackgroundOptions, GridOptions, SnaplineOptions
from base.helper import parse_size, parse_options, validate_location

ENV = Environment(
    loader=FileSystemLoader(
        os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "templates"
        )
    ),
)

_default_js = [
    ('x6', 'https://cdn.jsdelivr.net/npm/@antv/x6/dist/x6.js'),
]

_default_css = []


class Graph(MacroElement, BasicOpts):
    _template = Template(u"""
    {% macro header(this, kwargs) %}
        <meta name="viewport" content="width=device-width,
            initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
        <style>
            #{{ this.get_name() }} {
                width: {{this.width[0]}}{{this.width[1]}};
                height: {{this.height[0]}}{{this.height[1]}};
            }
        </style>
    {% endmacro %}
    
    {% macro html(this, kwargs) %}
        <div class="{{ this.get_name() }}" id={{ this.get_name()|tojson }} ></div>
    {% endmacro %}
        
    {% macro script(this, kwargs) %}
        const {{ this.get_name() }} = new X6.Graph({
                container: document.getElementById({{ this.get_name()|tojson }}),
                {%- for key, value in this.options.items() %}
                {{ key }}: {{ value|tojson }},
                {%- endfor %}
                }
        );
        {{this.get_name()}}.fromJSON({{ this.data() }});
    {% endmacro %}
    """)

    """Background 相关"""

    def drawBackground(self, background: Union[BackgroundOptions, dict, None] = BackgroundOptions()):
        if isinstance(background, dict):
            self.background.setOpt(**BackgroundOptions(**background).getOpt())
        elif isinstance(background, BackgroundOptions):
            self.background.setOpt(**background.getOpt())
        self.updateBackground()

    def updateBackground(self):
        self.options['background'] = self.background.getOpt()

    def clearBackground(self):
        self.options['background'] = False

    """Grid相关"""

    def drawGrid(self, grid: Union[GridOptions, dict, bool] = GridOptions()):
        if isinstance(grid, dict):
            self.grid.setOpt(**GridOptions(**grid).getOpt())
        elif isinstance(grid, GridOptions):
            self.grid.setOpt(**grid.getOpt())
        self.updateGrid()

    def updateGrid(self):
        self.options['grid'] = self.grid.getOpt()

    def getGridSize(self) -> Optional[Numeric]:
        return self.grid.getOpt('size')

    def setGridSize(self, gridSize: Optional[Numeric] = 10):
        self.grid.setOpt(size=gridSize)

    def showGrid(self):
        self.grid.setOpt(visible=True)

    def hideGrid(self):
        self.grid.setOpt(visible=False)

    """Snapline"""

    def isSnaplineEnabled(self):
        return self.snapline.getOpt('enable')

    def enableSnapline(self):
        self.options['snapline'] = True

    def disableSnapline(self):
        self.snapline.setOpt(enable=False)
        self.updateSnapline()

    def toggleSnapline(self, enable: Optional[bool] = None):
        if enable == None:
            self.snapline.setOpt(enable=not self.snapline.getOpt('enable'))
        else:
            self.snapline.setOpt(enable=enable)
        self.updateSnapline()

    def updateSnapline(self, snapline: Union[SnaplineOptions, dict, bool, None] = None):
        if isinstance(snapline, dict):
            self.snapline.setOpt(**SnaplineOptions(**snapline).getOpt())
        if isinstance(snapline, bool):
            self.options['snapline'] = snapline
            return
        elif isinstance(snapline, SnaplineOptions):
            self.snapline.setOpt(**snapline.getOpt())

        self.options['snapline'] = self.snapline.getOpt()

    def __init__(
            self,
            width: Union[Numeric, str] = 800,
            height: Union[Numeric, str] = 800,
            autoResize: bool = True,
            grid: Union[GridOptions, dict, bool] = GridOptions(),
            background: Union[BackgroundOptions, dict, bool] = BackgroundOptions(),
            snapline: Union[SnaplineOptions, dict, bool] = SnaplineOptions(),
            # scroller: Union[BackgroundOptions, dict, bool] = True,
            # # minimap: Union[BackgroundOptions, dict, bool] = False,
            # history: Union[BackgroundOptions, dict, bool] = True,
            # clipboard: Union[BackgroundOptions, dict, bool] = True,
            # keyboard: Union[BackgroundOptions, dict, bool] = True,
            # mousewheel: Union[BackgroundOptions, dict, bool] = True,
            # selecting: Union[BackgroundOptions, dict, bool] = True,
            # rotating: Union[BackgroundOptions, dict, bool] = True,
            # resizing: Union[BackgroundOptions, dict, bool] = True,
            # # translating: Union[BackgroundOptions, dict, None] = None,
            # # transforming: Union[BackgroundOptions, dict, None] = None,
            # embedding: Union[BackgroundOptions, dict, bool] = False,
            # # connecting: Union[BackgroundOptions, dict, None] = None,
            # # highlighting: Union[BackgroundOptions, dict, None] = None,
            # interacting: Union[BackgroundOptions, dict] = {'edgeLabelMovable': False},
            # sorting: Union['none', 'approx', 'exact'] = 'exact',
            # _async: Options[bool] = False,
            # frozen: Options[bool] = False,
            # magnetThreshold: Union[Numeric, 'onleave'] = 0,
            # moveThreshold: Numeric = 0,
            # clickThreshold: Numeric = 0,
            # preventDefaultContextMenu: Options[bool] = True,
            # preventDefaultBlankAction: Options[bool] = True,
            **kwargs
    ):
        self.grid = grid
        self.background = background
        self.snapline = snapline
        self.setOpt(locals())
        self.width = parse_size(width)
        self.height = parse_size(height)
        super(Graph, self).__init__()
        self._name = self.__class__.__name__
        self._env = ENV
        Figure().add_child(self)

    # def _repr_html_(self, **kwargs):
    #     """Displays the HTML Map in a Jupyter notebook."""
    #     if self._parent is None:
    #         self.add_to(Figure())
    #         out = self._parent._repr_html_(**kwargs)
    #         self._parent = None
    #     else:
    #         out = self._parent._repr_html_(**kwargs)
    #     return out

    #
    # def _to_png(self, delay=3):
    #     if self._png_image is None:
    #         # from selenium import webdriver
    #         #
    #         # options = webdriver.firefox.options.Options()
    #         # options.add_argument('--headless')
    #         # driver = webdriver.Firefox(options=options)
    #         #
    #         # html = self.get_root().render()
    #         # with _tmp_html(html) as fname:
    #         #     We need the tempfile to avoid JS security issues.
    #         # driver.get('file:///{path}'.format(path=fname))
    #         # driver.maximize_window()
    #         # time.sleep(delay)
    #         # png = driver.get_screenshot_as_png()
    #         # driver.quit()
    #         # self._png_image = png
    #         pass
    #     return self._png_image
    #
    # def _repr_png_(self):
    #     """Displays the PNG Map in a Jupyter notebook."""
    #     # The notebook calls all _repr_*_ by default.
    #     # We don't want that here b/c this one is quite slow.
    #     if not self.png_enabled:
    #         return None
    #     return self._to_png()
    #
    def render(self, **kwargs):
        """Renders the HTML representation of the element."""
        figure = self.get_root()
        assert isinstance(figure, Figure), ('You cannot render this Element '
                                            'if it is not in a Figure.')
        # Import Javascripts
        for name, url in _default_js:
            figure.header.add_child(JavascriptLink(url), name=name)
        # Import Css
        for name, url in _default_css:
            figure.header.add_child(CssLink(url), name=name)

        figure.header.add_child(Element(
            '<style>html, body {'
            'width: 100%;'
            'height: 100%;'
            'margin: 0;'
            'padding: 0;'
            '}'
            '</style>'), name='css_style')

        figure.header.add_child(Element(
            '<style>#graph {'
            'position:absolute;'
            'top:0;'
            'bottom:0;'
            'right:0;'
            'left:0;'
            '}'
            '</style>'), name='graph_style')

        super(Graph, self).render(**kwargs)

    def data(self):
        data = """
        {
            "nodes": [
                {
                    "id": "node1",
                    "x": 40,
                    "y": 40,
                    "width": 100,
                    "height": 40,
                    "attrs": {
                        "body": {
                            "fill": "#2ECC71",
                            "stroke": "#000",
                            "strokeDasharray": "10,2"
                        },
                        "label": {
                            "text": "Hello",
                            "fill": "#333",
                            "fontSize": 13
                        }
                    }
                },
                {
                    "id": "node2",
                    "x": 180,
                    "y": 240,
                    "width": 100,
                    "height": 40,
                    "attrs": {
                        "body": {
                            "fill": "#F39C12",
                            "stroke": "#000",
                            "rx": 16,
                            "ry": 16
                        },
                        "label": {
                            "text": "World",
                            "fill": "#333",
                            "fontSize": 18,
                            "fontWeight": "bold",
                            "fontVariant": "small-caps"
                        }
                    }
                }
            ],
            "edges": [
                {
                    "source": "node1",
                    "target": "node2",
                    "shape": "edge",
                    "attrs": {
                        "line": {
                            "stroke": "orange"
                        }
                    }
                }
            ]
        }
        """
        return data


if __name__ == '__main__':
    # g = Graph()
    # print(g.getOpt())
    # g.drawBackground(background=BackgroundOptions(color='yellow'))
    # print(g.getOpt())
    #
    # g.drawGrid(grid=GridOptions(color='yellow',visible=False))
    # print(g.getOpt())
    #
    # g.drawGrid({'color':'red','visible':True})
    # print(g.getOpt())
    #
    # g.hideGrid()
    # print(g.getOpt())
    #
    # g.showGrid()
    # print(g.getOpt())
    #
    # g.setGridSize(gridSize=11)
    # print(g.getOpt())
    # print(g.getGridSize())

    g = Graph()
    g.enableSnapline()
    print(g.getOpt())

    g.save("../test/g.html")

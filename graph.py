# coding:utf8

import warnings

from base.base import MacroElement, Figure, Element, JavascriptLink, CssLink
from base.base_object import *

from base.utils import parse_options, validate_location
from base.helper import _parse_size
from jinja2 import Template, PackageLoader, Environment

ENV = Environment(loader=PackageLoader('x6', 'templates'))
_default_js = [
    ('leaflet',
     'https://cdn.jsdelivr.net/npm/leaflet@1.5.1/dist/leaflet.js'),
    ('jquery',
     'https://code.jquery.com/jquery-1.12.4.min.js'),
    ('bootstrap',
     'https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/js/bootstrap.min.js'),
    ('awesome_markers',
     'https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.js'),  # noqa
]

_default_css = [
    ('leaflet_css',
     'https://cdn.jsdelivr.net/npm/leaflet@1.5.1/dist/leaflet.css'),
    ('bootstrap_css',
     'https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap.min.css'),
    ('bootstrap_theme_css',
     'https://maxcdn.bootstrapcdn.com/bootstrap/3.2.0/css/bootstrap-theme.min.css'),  # noqa
    ('awesome_markers_font_css',
     'https://maxcdn.bootstrapcdn.com/font-awesome/4.6.3/css/font-awesome.min.css'),  # noqa
    ('awesome_markers_css',
     'https://cdnjs.cloudflare.com/ajax/libs/Leaflet.awesome-markers/2.0.2/leaflet.awesome-markers.css'),  # noqa
    ('awesome_rotate_css',
     'https://rawcdn.githack.com/python-visualization/folium/master/folium/templates/leaflet.awesome.rotate.css'),
    # noqa
]


class GlobalSwitches(Element):
    _template = Template("""
        <script>
            L_NO_TOUCH = {{ this.no_touch |tojson}};
            L_DISABLE_3D = {{ this.disable_3d|tojson }};
        </script>
    """)

    def __init__(self, no_touch=False, disable_3d=False):
        super(GlobalSwitches, self).__init__()
        self._name = 'GlobalSwitches'
        self.no_touch = no_touch
        self.disable_3d = disable_3d


class Graph(MacroElement, BasicOpts):
    _template = Template(u"""
        {% macro header(this, kwargs) %}
            <meta name="viewport" content="width=device-width,
                initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
            <style>
                #{{ this.get_name() }} {
                    position: {{this.position}};
                    width: {{this.width[0]}}{{this.width[1]}};
                    height: {{this.height[0]}}{{this.height[1]}};
                    left: {{this.left[0]}}{{this.left[1]}};
                    top: {{this.top[0]}}{{this.top[1]}};
                }
            </style>
        {% endmacro %}

        {% macro html(this, kwargs) %}
            <div class="folium-map" id={{ this.get_name()|tojson }} ></div>
        {% endmacro %}

        {% macro script(this, kwargs) %}
            var {{ this.get_name() }} = L.map(
                {{ this.get_name()|tojson }},
                {
                    center: {{ this.location|tojson }},
                    crs: L.CRS.{{ this.crs }},
                    {%- for key, value in this.options.items() %}
                    {{ key }}: {{ value|tojson }},
                    {%- endfor %}
                }
            );

            {%- if this.control_scale %}
            L.control.scale().addTo({{ this.get_name() }});
            {%- endif %}

            {% if this.objects_to_stay_in_front %}
            function objects_in_front() {
                {%- for obj in this.objects_to_stay_in_front %}
                    {{ obj.get_name() }}.bringToFront();
                {%- endfor %}
            };
            {{ this.get_name() }}.on("overlayadd", objects_in_front);
            $(document).ready(objects_in_front);
            {%- endif %}

        {% endmacro %}
        """)
    def drawBackground(
            self,background: Union[BackgroundOptions, dict, None] = BackgroundOptions()
           ):
        if isinstance(background,dict):
            self._background.update(**BackgroundOptions(**background).get())
        elif isinstance(background,BackgroundOptions):
            self._background.update(**background.get())
        self.updateBackground()

    def updateBackground(self):
        self.options['background'] = self._background.get()

    def clearBackground(self):
        self._background = None

    def drawGrid(
            self, grid: Union[GridOptions, dict, None] = GridOptions()
    ):
        if isinstance(grid, dict):
            self._grid.update(**GridOptions(**grid).get())
        elif isinstance(grid, GridOptions):
            self._grid.update(**grid.get())
        self.updateGrid()

    def updateGrid(self):
        self.options['grid'] = self._grid.get()

    def getGridSize(self)->Optional[Numeric]:
        return self._grid.get('size')

    def setGridSize(self,gridSize: Optional[Numeric] = 10):
        self._grid.update(size=gridSize)

    def showGrid(self):
        self._grid.update(visible=True)

    def hideGrid(self):
        self._grid.update(visible=False)

    def clearBackground(self):
        self._grid = None

    def __init__(
            self,
            container: Optional[str] = "container",
            width: Union[int, float, str] = '100%',
            height: Union[int, float, str] = '100%',
            background: Union[BackgroundOptions, dict, None] = BackgroundOptions(),
            grid: Union[GridOptions, dict, None] = GridOptions(),
            **kwargs
    ):
        super(Graph, self).__init__()
        self._background = background
        self._grid = grid
        self.width = _parse_size(width)
        self.height = _parse_size(height)

        self.options = parse_options(
            container=container,
            width=self.width,
            height=self.height,
            background=self._background.get(),
            grid=self._grid.get(),
            **kwargs
        )
        print(self.options)


        self.options: dict = {
            "container": container,
            "width": self.width,
            "height": self.height,
            "background": self._background.get(),
            "grid": self._grid.get(),
        }


        self._name = 'Graph'
        self._env = ENV
        Figure().add_child(self)



        # max_bounds_array = [[min_lat, min_lon], [max_lat, max_lon]] \
        #     if max_bounds else None
        #
        # self.crs = crs
        # self.control_scale = control_scale
        #

        #
        # self.global_switches = GlobalSwitches(
        #     no_touch,
        #     disable_3d
        # )
        #
        # self.objects_to_stay_in_front = []
        #
        # if tiles:
        #     pass
        # tile_layer = TileLayer(tiles=tiles, attr=attr,
        #                        min_zoom=min_zoom, max_zoom=max_zoom)
        # self.add_child(tile_layer, name=tile_layer.tile_name)

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
    #     """Export the HTML to byte representation of a PNG image.
    #
    #     Uses selenium to render the HTML and record a PNG. You may need to
    #     adjust the `delay` time keyword argument if maps render without data or tiles.
    #
    #     Examples
    #     --------
    #     >>> m._to_png()
    #     >>> m._to_png(time=10)  # Wait 10 seconds between render and snapshot.
    #
    #     """
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
    # def render(self, **kwargs):
    #     """Renders the HTML representation of the element."""
    #     figure = self.get_root()
    #     assert isinstance(figure, Figure), ('You cannot render this Element '
    #                                         'if it is not in a Figure.')
    #
    #     # Set global switches
    #     figure.header.add_child(self.global_switches, name='global_switches')
    #
    #     # Import Javascripts
    #     for name, url in _default_js:
    #         figure.header.add_child(JavascriptLink(url), name=name)
    #
    #     # Import Css
    #     for name, url in _default_css:
    #         figure.header.add_child(CssLink(url), name=name)
    #
    #     figure.header.add_child(Element(
    #         '<style>html, body {'
    #         'width: 100%;'
    #         'height: 100%;'
    #         'margin: 0;'
    #         'padding: 0;'
    #         '}'
    #         '</style>'), name='css_style')
    #
    #     figure.header.add_child(Element(
    #         '<style>#map {'
    #         'position:absolute;'
    #         'top:0;'
    #         'bottom:0;'
    #         'right:0;'
    #         'left:0;'
    #         '}'
    #         '</style>'), name='map_style')
    #
    #     super(Graph, self).render(**kwargs)
    #
    # def fit_bounds(self, bounds, padding_top_left=None,
    #                padding_bottom_right=None, padding=None, max_zoom=None):
    #     """Fit the map to contain a bounding box with the
    #     maximum zoom level possible.
    #
    #     Parameters
    #     ----------
    #     bounds: list of (latitude, longitude) points
    #         Bounding box specified as two points [southwest, northeast]
    #     padding_top_left: (x, y) point, default None
    #         Padding in the top left corner. Useful if some elements in
    #         the corner, such as controls, might obscure objects you're zooming
    #         to.
    #     padding_bottom_right: (x, y) point, default None
    #         Padding in the bottom right corner.
    #     padding: (x, y) point, default None
    #         Equivalent to setting both top left and bottom right padding to
    #         the same value.
    #     max_zoom: int, default None
    #         Maximum zoom to be used.
    #
    #     Examples
    #     --------
    #     >>> m.fit_bounds([[52.193636, -2.221575], [52.636878, -1.139759]])
    #
    #     """
    #     pass
    #     # self.add_child(FitBounds(bounds,
    #     #                          padding_top_left=padding_top_left,
    #     #                          padding_bottom_right=padding_bottom_right,
    #     #                          padding=padding,
    #     #                          max_zoom=max_zoom,
    #     #                          )
    #     #                )
    #
    # def choropleth(self, *args, **kwargs):
    #     """Call the Choropleth class with the same arguments.
    #
    #     This method may be deleted after a year from now (Nov 2018).
    #     """
    #     warnings.warn(
    #         'The choropleth  method has been deprecated. Instead use the new '
    #         'Choropleth class, which has the same arguments. See the example '
    #         'notebook \'GeoJSON_and_choropleth\' for how to do this.',
    #         FutureWarning
    #     )
    #     from folium.features import Choropleth
    #     self.add_child(Choropleth(*args, **kwargs))
    #
    # def keep_in_front(self, *args):
    #     """Pass one or multiples object that must stay in front.
    #
    #     The ordering matters, the last one is put on top.
    #
    #     Parameters
    #     ----------
    #     *args :
    #         Variable length argument list. Any folium object that counts as an
    #         overlay. For example FeatureGroup or a vector object such as Marker.
    #     """
    #     for obj in args:
    #         self.objects_to_stay_in_front.append(obj)


if __name__ == '__main__':
    g = Graph()
    print(g.get())
    g.drawBackground(background=BackgroundOptions(color='yellow'))
    print(g.get())

    g.drawGrid(grid=GridOptions(color='yellow',visible=False))
    print(g.get())

    g.drawGrid({'color':'red','visible':True})
    print(g.get())

    g.hideGrid()
    print(g.get())

    g.showGrid()
    print(g.get())

    g.setGridSize(gridSize=11)
    print(g.get())
    print(g.getGridSize())
    # g.save("../test/g.html")

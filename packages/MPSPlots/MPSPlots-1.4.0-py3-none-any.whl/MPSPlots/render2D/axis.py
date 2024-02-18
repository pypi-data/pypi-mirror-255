#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Matplotlib imports
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.pyplot import axis as MPLAxis
from matplotlib import ticker

# Other imports
import numpy
from dataclasses import dataclass, field
from functools import wraps

from MPSPlots.render2D.artist import (
    Line,
    FillLine,
    STDLine,
    Mesh,
    Scatter,
    Contour,
    VerticalLine,
    HorizontalLine,
    Text,
    PatchPolygon,
    Colorbar,
    AxAnnotation,
    Table,
    WaterMark,
    PatchCircle
)


@dataclass(slots=True)
class Axis:
    row: int
    """ Row value of the ax """
    col: int
    """ Column value of the ax """
    x_label: str = None
    """ Set x label """
    y_label: str = None
    """ Set y label """
    title: str = ''
    """ Title of the ax """
    show_grid: bool = True
    """ Show the ax grid or not """
    show_legend: bool = False
    """ Show the legend or not """
    legend_position: str = 'best'
    """ Position of the legend """
    x_scale: str = 'linear'
    """ Set scale of x axis """
    y_scale: str = 'linear'
    """ Set scale of y axis """
    x_limits: list = None
    """ Set limits of x axis """
    y_limits: list = None
    """ Set limits of y axis """
    equal_limits: bool = False
    """ Set equal limits to x and y axis, override x_limits and y_limits """
    projection: str = None
    """ Projection of the plot [Polar, normal] """
    font_size: int = 16
    """ Text font size """
    tick_size: int = 14
    """ Ticks font size """
    y_tick_position: str = 'left'
    """ Ticks position for the y axis, must be in ['left', 'right'] """
    x_tick_position: str = 'bottom'
    """ Ticks position for the x axis, must be in ['top', 'bottom'] """
    show_ticks: bool = True
    """ Show x and y ticks or not """
    show_colorbar: bool = None
    """ Show colorbar or not """
    legend_font_size: bool = 14
    """  Font size of the legend text """
    line_width: float = None
    """ Line width of the contained artists. """
    line_style: float = None
    """ Line style of the contained artists. """
    x_scale_factor: float = None
    """ Scaling factor for the x axis """
    y_scale_factor: float = None
    """ Scaling factor for the y axis """
    aspect_ratio: str = 'auto'
    """ Aspect ratio of the axis """

    _artist_list: list = field(default_factory=lambda: [], init=False)
    mpl_ax: MPLAxis = field(default=None, init=False)
    colorbar: Colorbar = field(default_factory=lambda: Colorbar(), init=False)

    def __getitem__(self, idx):
        return self._artist_list[idx]

    def __add__(self, other):
        self._artist_list += other._artist_list
        return self

    def add_artist_to_ax(function):
        @wraps(function)
        def wrapper(self, *args, **kwargs):
            artist = function(self, *args, **kwargs)
            self._artist_list.append(artist)

            return artist

        return wrapper

    @property
    def style(self):
        return {
            'x_label': self.x_label,
            'y_label': self.y_label,
            'title': self.title,
            'show_grid': self.show_grid,
            'show_legend': self.show_legend,
            'x_scale': self.x_scale,
            'y_scale': self.y_scale,
            'x_limits': self.x_limits,
            'y_limits': self.y_limits,
            'equal_limits': self.equal_limits,
            'aspect_ratio': self.aspect_ratio,
            'projection': self.projection,
            'font_size': self.font_size,
            'legend_font_size': self.legend_font_size,
            'tick_size': self.tick_size
        }

    def get_y_max(self) -> float:
        """
        Gets the maximum y value of all artist in that current axis

        :returns:   The maximum y value.
        :rtype:     float
        """
        y_max = -numpy.inf
        for artist in self._artist_list:
            if not hasattr(artist, 'y'):
                continue
            artist_y_max = numpy.max(artist.y)
            y_max = max(y_max, artist_y_max)

        return y_max

    def get_y_min(self) -> float:
        """
        Gets the minimum y value of all artist in that current axis

        :returns:   The minimum y value.
        :rtype:     float
        """
        y_min = numpy.inf
        for artist in self._artist_list:
            if not hasattr(artist, 'y'):
                continue
            artist_y_min = numpy.min(artist.y)
            y_min = min(y_min, artist_y_min)

        return y_min

    def get_x_max(self) -> float:
        """
        Gets the maximum x value of all artist in that current axis

        :returns:   The maximum x value.
        :rtype:     float
        """
        y_max = -numpy.inf
        for artist in self._artist_list:
            artist_y_max = numpy.max(artist.y)
            y_max = max(y_max, artist_y_max)

        return y_max

    def get_x_min(self) -> float:
        """
        Gets the minimum y value of all artist in that current axis

        :returns:   The minimum y value.
        :rtype:     float
        """
        x_min = numpy.inf
        for artist in self._artist_list:
            artist_x_min = numpy.min(artist.y)
            x_min = min(x_min, artist_x_min)

        return x_min

    def copy_style(self, other) -> None:
        assert isinstance(other, self), f"Cannot copy style from other class {other.__class__}"
        for element, value in other.style.items():
            setattr(self, element, value)

    def add_artist(self, *artists) -> None:
        for artist in artists:
            self._artist_list.append(artist)

    def set_style(self, **style_dict):
        for element, value in style_dict.items():
            setattr(self, element, value)

        return self

    def set_ax_limits(self) -> None:
        """
        Sets the ax x and y limits.

        :returns:   No returns
        :rtype:     None
        """
        self.mpl_ax.set_xlim(self.x_limits)

        self.mpl_ax.set_ylim(self.y_limits)

        if self.equal_limits:
            xy_limits = [*self.mpl_ax.get_xlim(), *self.mpl_ax.get_ylim()]
            min_xy_limit = numpy.min(xy_limits)
            max_xy_limit = numpy.max(xy_limits)

            self.mpl_ax.set_xlim([min_xy_limit, max_xy_limit])
            self.mpl_ax.set_ylim([min_xy_limit, max_xy_limit])

        ticker.ScalarFormatter(
            useOffset=False,
            # useMathText=None,
            # useLocale=None
        )

    def set_artist_parameter_value(self, parameter_str: str, value) -> None:
        if value is None:
            return

        for artist in self._artist_list:
            if not hasattr(artist, parameter_str):
                continue

            setattr(artist, parameter_str, value)

    def scale_artist_x_axis(self, scale_factor: float) -> None:
        """
        Scales all the artist x axis by the provided factor

        :param      scale_factor:  The scale factor
        :type       scale_factor:  float

        :returns:   No returns
        :rtype:     None
        """
        self.set_artist_parameter_value(
            parameter_str='x_scale_factor',
            value=scale_factor
        )

    def scale_artist_y_axis(self, scale_factor: float) -> None:
        """
        Scales all the artist x axis by the provided factor

        :param      scale_factor:  The scale factor
        :type       scale_factor:  float

        :returns:   No returns
        :rtype:     None
        """
        self.set_artist_parameter_value(
            parameter_str='y_scale_factor',
            value=scale_factor
        )

    def set_artist_line_width(self, line_width: float) -> None:
        """
        Sets the artists line width.

        :param      line_width:  The line width
        :type       line_width:  float

        :returns:   No returns
        :rtype:     None
        """
        self.set_artist_parameter_value(
            parameter_str='line_width',
            value=line_width
        )

    def set_artist_line_style(self, line_style: 'str') -> None:
        """
        Sets the artists line style.

        :param      line_width:  The line style
        :type       line_width:  float

        :returns:   No returns
        :rtype:     None
        """
        self.set_artist_parameter_value(
            parameter_str='line_style',
            value=line_style
        )

    def render_artists(self) -> None:
        """
        Render artists

        :returns:   No returns
        :rtype:     None
        """
        for artist in self._artist_list:
            artist._render_(self)

    def _render_(self) -> None:
        """
        Renders the ax with each of its related artist.

        :returns:   No returns
        :rtype:     None
        """
        self.scale_artist_x_axis(self.x_scale_factor)

        self.scale_artist_y_axis(self.y_scale_factor)

        self.set_artist_line_width(line_width=self.line_width)

        self.set_artist_line_style(line_style=self.line_style)

        self.render_artists()

        self.decorate_axis()

        if self.show_colorbar:
            self.colorbar._render_(ax=self)

        self.set_ax_limits()

    def generate_legend(self) -> None:
        """
        Generate legend of ax

        :returns:   No returns
        :rtype:     None
        """
        if self.show_legend:
            self.mpl_ax.legend()
            handles, labels = self.mpl_ax.get_legend_handles_labels()

            by_label = dict(zip(labels, handles))

            self.mpl_ax.legend(
                by_label.values(),
                by_label.keys(),
                edgecolor='k',
                facecolor='white',
                fancybox=True,
                fontsize=self.legend_font_size - 4,
                loc=self.legend_position,
            )

    def set_x_ticks_position(self, position: str) -> None:
        """
        Sets the axis x ticks position.

        :param      position:  The position
        :type       position:  str

        :returns:   No returns
        :rtype:     None
        """
        position = position.lower()

        mpl_ticks = self.mpl_ax.xaxis
        mpl_ticks.set_label_position(position)
        tick_position_function = getattr(mpl_ticks, f"tick_{position}")

        tick_position_function()

        mpl_ticks.set_visible(self.show_ticks)

        self.x_tick_position = position

    def set_y_ticks_position(self, position: str) -> None:
        """
        Sets the axis y ticks position.

        :param      position:  The position
        :type       position:  str

        :returns:   No returns
        :rtype:     None
        """
        position = position.lower()

        mpl_ticks = self.mpl_ax.yaxis
        mpl_ticks.set_label_position(position)
        tick_position_function = getattr(mpl_ticks, f"tick_{position}")

        tick_position_function()

        mpl_ticks.set_visible(self.show_ticks)

        self.y_tick_position = position

    def set_title(self, title: str, font_size: int = None) -> None:
        """
        Sets the title of axis.

        :param      title:      The title
        :type       title:      str
        :param      font_size:  The font size
        :type       font_size:  int

        :returns:   No returns
        :rtype:     None
        """
        font_size = self.font_size if font_size is None else font_size

        self.title = title

        self.mpl_ax.set_title(self.title, fontsize=font_size)

    def set_tick_size(self, tick_size: int = None) -> None:
        """
        Sets the tick size.

        :param      tick_size:  The tick size
        :type       tick_size:  int

        :returns:   No returns
        :rtype:     None
        """
        tick_size = self.tick_size if tick_size is None else tick_size

        self.tick_size = tick_size

        self.mpl_ax.tick_params(labelsize=tick_size)

    def set_aspect(self, aspect: str = None) -> None:
        """
        Sets the aspect ratio for plot.

        :param      aspect:  The aspect
        :type       aspect:  str

        :returns:   No returns
        :rtype:     None
        """
        aspect_ratio = self.aspect_ratio if aspect is None else aspect

        self.mpl_ax.set_aspect(aspect_ratio)

    def set_show_grid(self, show_grid: bool = None) -> None:
        """
        Sets the show grid.

        :param      show_grid:  The show grid
        :type       show_grid:  bool

        :returns:   No returns
        :rtype:     None
        """
        show_grid = self.show_grid if show_grid is None else show_grid

        self.mpl_ax.grid(show_grid)

        self.show_grid = show_grid

    def set_x_label(self, label: str, font_size: int = None) -> None:
        """
        Sets the x label.

        :param      label:      The label
        :type       label:      str
        :param      font_size:  The font size
        :type       font_size:  int

        :returns:   No returns
        :rtype:     None
        """
        font_size = self.font_size if font_size is None else font_size

        self.mpl_ax.set_xlabel(label, fontsize=font_size)

    def set_y_label(self, label: str, font_size: int = None) -> None:
        """
        Sets the y label.

        :param      label:      The label
        :type       label:      str
        :param      font_size:  The font size
        :type       font_size:  int

        :returns:   No returns
        :rtype:     None
        """
        font_size = self.font_size if font_size is None else font_size

        self.mpl_ax.set_ylabel(label, fontsize=font_size)

    def set_y_scale(self, scale: str = None) -> None:
        """
        Sets the y scale.

        :param      label:      The scale
        :type       label:      str

        :returns:   No returns
        :rtype:     None
        """
        scale = self.y_scale if scale is None else scale

        self.mpl_ax.set_yscale(scale)

    def set_x_scale(self, scale: str = None) -> None:
        """
        Sets the x scale.

        :param      label:      The scale
        :type       label:      str

        :returns:   No returns
        :rtype:     None
        """
        scale = self.x_scale if scale is None else scale

        self.mpl_ax.set_xscale(scale)

    def decorate_axis(self) -> None:
        """
        Add all the decoration to axis

        :returns:   No returns
        :rtype:     None
        """
        self.generate_legend()

        self.set_x_label(self.x_label)

        self.set_y_label(self.y_label)

        self.set_x_ticks_position(position=self.x_tick_position)

        self.set_y_ticks_position(position=self.y_tick_position)

        self.set_title(title=self.title)

        self.set_x_scale()

        self.set_y_scale()

        self.set_tick_size()

        self.set_aspect()

        self.set_show_grid()

    @add_artist_to_ax
    def add_fill_line(self, **kwargs: dict) -> FillLine:
        """
        Adds a FillLine artist to ax.

        :param      kwargs:  The keywords arguments to be sent to FillLine class
        :type       kwargs:  dict

        :returns:   The artist object
        :rtype:     FillLine
        """
        return FillLine(**kwargs)

    @add_artist_to_ax
    def add_std_line(self, **kwargs: dict) -> STDLine:
        """
        Adds a STDLine artist to ax.

        :param      kwargs:  The keywords arguments to be sent to STDLine class
        :type       kwargs:  dict

        :returns:   The artist object
        :rtype:     STDLine
        """
        return STDLine(**kwargs)

    @add_artist_to_ax
    def add_scatter(self, **kwargs: dict) -> Scatter:
        """
        Adds a Scatter artist to ax.

        :param      kwargs:  The keywords arguments to be sent to Scatter class
        :type       kwargs:  dict

        :returns:   The artist object
        :rtype:     Scatter
        """
        return Scatter(**kwargs)

    def add_table(self, **kwargs: dict) -> Table:
        """
        Adds a Table artist to ax.

        :param      kwargs:  The keywords arguments to be sent to Table class
        :type       kwargs:  dict

        :returns:   The artist object
        :rtype:     Table
        """
        return Table(**kwargs)

    @add_artist_to_ax
    def add_mesh(self, **kwargs: dict) -> Mesh:
        """
        Adds a Mesh artist to ax.

        :param      kwargs:  The keywords arguments to be sent to Mesh class
        :type       kwargs:  dict

        :returns:   The artist object
        :rtype:     Mesh
        """
        artist = Mesh(**kwargs)
        self.add_artist(artist)

        return artist

    @add_artist_to_ax
    def add_contour(self, **kwargs: dict) -> Contour:
        """
        Adds a Contour artist to ax.

        :param      kwargs:  The keywords arguments to be sent to Contour class
        :type       kwargs:  dict

        :returns:   The artist object
        :rtype:     Contour
        """
        return Contour(**kwargs)

    @add_artist_to_ax
    def add_line(self, **kwargs: dict) -> Line:
        """
        Adds a Line artist to ax.

        :param      kwargs:  The keywords arguments to be sent to Line class
        :type       kwargs:  dict

        :returns:   The artist object
        :rtype:     Line
        """
        return Line(**kwargs)

    @add_artist_to_ax
    def add_vertical_line(self, **kwargs: dict) -> VerticalLine:
        """
        Adds a VerticalLine artist to ax.

        :param      kwargs:  The keywords arguments to be sent to VerticalLine class
        :type       kwargs:  dict

        :returns:   The artist object
        :rtype:     VerticalLine
        """
        return VerticalLine(**kwargs)

    @add_artist_to_ax
    def add_horizontal_line(self, **kwargs: dict) -> HorizontalLine:
        """
        Adds a HorizontalLine artist to ax.

        :param      kwargs:  The keywords arguments to be sent to HorizontalLine class
        :type       kwargs:  dict

        :returns:   The artist object
        :rtype:     VerticalLine
        """
        return HorizontalLine(**kwargs)

    @add_artist_to_ax
    def add_text(self, **kwargs: dict) -> Text:
        """
        Adds a Text artist to ax.

        :param      kwargs:  The keywords arguments to be sent to Text class
        :type       kwargs:  dict

        :returns:   The artist object
        :rtype:     Text
        """
        return Text(**kwargs)

    @add_artist_to_ax
    def add_watermark(self, **kwargs: dict) -> WaterMark:
        """
        Adds a WaterMark artist to ax.

        :param      kwargs:  The keywords arguments to be sent to WaterMark class
        :type       kwargs:  dict

        :returns:   The artist object
        :rtype:     Text
        """
        return WaterMark(**kwargs)

    @add_artist_to_ax
    def add_polygon(self, **kwargs: dict) -> PatchPolygon:
        """
        Adds a PatchPolygon artist to ax.

        :param      kwargs:  The keywords arguments to be sent to Text class
        :type       kwargs:  dict

        :returns:   The artist object
        :rtype:     PatchPolygon
        """
        return PatchPolygon(**kwargs)

    @add_artist_to_ax
    def add_circle(self, **kwargs: dict) -> PatchCircle:
        """
        Adds a PatchCircle artist to ax.

        :param      kwargs:  The keywords arguments to be sent to Text class
        :type       kwargs:  dict

        :returns:   The artist object
        :rtype:     PatchCircle
        """
        return PatchCircle(**kwargs)

    def add_colorbar(self, **kwargs: dict) -> Colorbar:
        """
        Adds a Colorbar artist to ax.

        :param      kwargs:  The keywords arguments to be sent to Colorbar class
        :type       kwargs:  dict

        :returns:   The artist object
        :rtype:     Colorbar
        """
        self.colorbar = Colorbar(**kwargs)
        self.show_colorbar = True

        return self.colorbar

    @add_artist_to_ax
    def add_ax_annotation(self, text: str, **kwargs: dict) -> Colorbar:
        """
        Adds a Colorbar artist to ax.

        :param      kwargs:  The keywords arguments to be sent to Colorbar class
        :type       kwargs:  dict

        :returns:   The artist object
        :rtype:     Colorbar
        """
        return AxAnnotation(text, **kwargs)


def Multipage(filename, figs=None, dpi=200):
    pp = PdfPages(filename)

    for fig in figs:
        fig._mpl_figure.savefig(pp, format='pdf')

    pp.close()


# -

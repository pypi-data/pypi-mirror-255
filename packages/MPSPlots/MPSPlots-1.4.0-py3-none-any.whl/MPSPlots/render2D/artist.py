#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Matplotlib imports
import matplotlib
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.pyplot as plt
from matplotlib.pyplot import axis as MPLAxis
from matplotlib.offsetbox import AnchoredText
from matplotlib.patches import PathPatch
from matplotlib.collections import PatchCollection
from matplotlib.path import Path
import matplotlib.colors as colors

# Other imports
import numpy
import shapely.geometry as geo
from itertools import cycle
from dataclasses import dataclass, field
from MPSPlots import colormaps

linecycler = cycle(["-", "--", "-.", ":"])


__all__ = [
    'Colorbar',
    'Contour',
    'Mesh',
    'Polygon',
    'FillLine',
    'STDLine',
    'Line',
    'VerticalLine',
    'Scatter',
    'Text',
    'AxAnnotation',
    'PatchPolygon',

]


@dataclass()
class Colorbar:
    artist: numpy.ndarray = None
    """ The artist to map """
    discreet: bool = False
    """ Buggy feature """
    position: str = 'right'
    """ Position of the colorbar """
    colormap: str = field(default_factory=lambda: colormaps.blue_black_red)
    """ Colormap to be used for the plot """
    orientation: str = "vertical"
    """ Orientation of the colorbar """
    symmetric: bool = False
    """ Set symmetric colormap """
    log_norm: bool = False
    """ Log normalization of the colorbar """
    numeric_format: str = None
    """ Format for the ticks on the colorbar """
    n_ticks: int = None
    """ Number of ticks for the colorbar """
    label_size: int = None
    """ Label size of the colorbar """
    width: str = "10%"
    """ Width of the colorbar """
    padding: float = 0.10
    """ Padding between the plot and the colorbar """
    norm: object = None
    """ Matplotlib norm """
    label: str = ""
    """ Colorbar label text """

    def __post_init__(self):
        self.norm = self.get_norm()

        if self.artist is None:
            self.mappable = None
        else:
            self.mappable = plt.cm.ScalarMappable(cmap=self.colormap, norm=self.norm)

            self.mappable.set_array(self.artist.scalar)

    def get_norm(self):
        if self.norm is not None:
            return self.norm

        if self.symmetric:
            return colors.CenteredNorm()

    def create_sub_ax(self, ax) -> object:
        divider = make_axes_locatable(ax.mpl_ax)

        colorbar_ax = divider.append_axes(
            self.position,
            size=self.width,
            pad=self.padding
        )

        return colorbar_ax

    def _render_(self, ax: MPLAxis) -> None:
        """
        Renders the artist on the given ax.

        :param      ax:   Matplotlib axis
        :type       ax:   MPLAxis

        :returns:   No returns
        :rtype:     None
        """
        if self.mappable is None:
            return None

        colorbar_ax = self.create_sub_ax(ax=ax)

        colorbar = plt.colorbar(
            mappable=self.mappable,
            norm=self.norm,
            ax=ax.mpl_ax,
            cax=colorbar_ax,
            orientation=self.orientation,
            format=self.numeric_format,
            extend='both',
            label=self.label
        )

        if self.n_ticks is not None:
            colorbar.ax.locator_params(nbins=self.n_ticks)
            colorbar.ax.tick_params(labelsize=self.label_size)


@dataclass(slots=True)
class Contour():
    x: numpy.ndarray
    """ y axis, can be vector or 2D grid """
    y: numpy.ndarray
    """ x axis, can be vector or 2D grid """
    scalar: numpy.ndarray
    """ Scalar 2D field """
    iso_values: numpy.ndarray
    """ Level values to which plot the iso contours """
    colormap: str = None
    """ Colormap to use for plottings """
    x_scale_factor: float = 1
    """ Scaling factor for the x axis """
    y_scale_factor: float = 1
    """ Scaling factor for the y axis """
    layer_position: int = 1
    """ Position of the layer """
    fill_contour: bool = False
    """ Fill the contour line with color """

    def __post_init__(self):
        if self.colormap is None:
            self.colormap = colormaps.blue_black_red

    def _render_(self, ax: MPLAxis) -> None:
        """
        Renders the artist on the given ax.

        :param      ax:   Matplotlib axis
        :type       ax:   MPLAxis

        :returns:   No returns
        :rtype:     None
        """
        ax.mpl_ax.contour(
            self.x * self.x_scale_factor,
            self.y * self.y_scale_factor,
            self.scalar,
            levels=self.iso_values,
            colors="black",
            zorder=self.layer_position
        )

        if self.fill_contour:
            ax.mpl_ax.contourf(
                self.x * self.x_scale_factor,
                self.y * self.y_scale_factor,
                self.scalar,
                levels=self.iso_values,
                cmap=self.colormap,
                zorder=self.layer_position
            )


@dataclass(slots=True)
class Mesh():
    scalar: numpy.ndarray
    """ 2 dimensional numpy array representing the mesh to be plotted """
    x: numpy.ndarray = None
    """ Array representing the x axis, if not defined a numpy arrange is used instead """
    y: numpy.ndarray = None
    """ Array representing the y axis, if not defined a numpy arrange is used instead """
    x_scale_factor: float = 1
    """ Scaling factor for the x axis """
    y_scale_factor: float = 1
    """ Scaling factor for the y axis """
    layer_position: int = 1
    """ Position of the layer """

    def __post_init__(self):
        if self.x is None:
            self.x = numpy.arange(self.scalar.shape[1])

        if self.y is None:
            self.y = numpy.arange(self.scalar.shape[0])

    def _render_(self, ax: MPLAxis) -> None:
        """
        Renders the artist on the given ax.

        :param      ax:   Matplotlib axis
        :type       ax:   MPLAxis

        :returns:   No returns
        :rtype:     None
        """
        image = ax.mpl_ax.pcolormesh(
            self.x * self.x_scale_factor,
            self.y * self.y_scale_factor,
            self.scalar,
            shading='auto',
            zorder=self.layer_position,
            norm=ax.colorbar.norm,
            cmap=ax.colorbar.colormap,
        )

        image.set_edgecolor('face')

        return image


@dataclass(slots=True)
class Polygon():
    instance: object
    """ Shapely geo instance representing the polygone to be plotted """
    name: str = ''
    """ Name to be added to the plot next to the polygon """
    alpha: float = 0.4
    """ Opacity of the polygon to be plotted """
    facecolor: str = 'lightblue'
    """ Color for the interior of the polygon """
    edgecolor: str = 'black'
    """ Color for the border of the polygon """
    x_scale_factor: float = 1
    """ Scaling factor for the x axis """
    y_scale_factor: float = 1
    """ Scaling factor for the y axis """
    layer_position: int = 1
    """ Position of the layer """

    def _render_(self, ax: MPLAxis) -> None:
        """
        Renders the artist on the given ax.

        :param      ax:   Matplotlib axis
        :type       ax:   MPLAxis

        :returns:   No returns
        :rtype:     None
        """
        if isinstance(self.instance, geo.MultiPolygon):
            for polygon in self.instance.geoms:
                self.add_polygon_to_ax(polygon, ax)

        else:
            self.add_polygon_to_ax(self.instance, ax)

    def add_polygon_to_ax(self, polygon, ax, add_name: str = None):
        collection = self.get_polygon_path(polygon)

        ax.mpl_ax.add_collection(collection, autolim=True)

        ax.mpl_ax.autoscale_view()

        if add_name:
            ax.mpl_ax.scatter(polygon.centroid.x, polygon.centroid.y)
            ax.mpl_ax.text(polygon.centroid.x, polygon.centroid.y, self.name)

    def get_polygon_path(self, polygon):
        exterior_coordinate = numpy.asarray(polygon.exterior.coords)

        exterior_coordinate[:, 0] *= self.x_scale_factor
        exterior_coordinate[:, 1] *= self.y_scale_factor

        path_exterior = Path(exterior_coordinate)

        path_interior = []
        for ring in polygon.interiors:
            interior_coordinate = numpy.asarray(ring.coords)
            path_interior.append(Path(interior_coordinate))

        path = Path.make_compound_path(
            path_exterior,
            *path_interior
        )

        patch = PathPatch(path)

        collection = PatchCollection(
            [patch],
            alpha=self.alpha,
            facecolor=self.facecolor,
            edgecolor=self.edgecolor
        )

        return collection


@dataclass(slots=True)
class FillLine():
    x: numpy.ndarray
    """ Array representing the x axis """
    y0: numpy.ndarray
    """ Array representing the inferior y axis to be filled with color """
    y1: numpy.ndarray
    """ Array representing the superior y axis to be filled with color """
    label: str = ""
    color: str = None
    """ Color for the fill """
    line_style: str = None
    """ Line style for the unique line default is next in cycle """
    line_width: float = 1
    """ Line width of the artists """
    show_outline: bool = True
    """ Show the outline of the filling """
    x_scale_factor: float = 1
    """ Scaling factor for the x axis """
    y_scale_factor: float = 1
    """ Scaling factor for the y axis """
    layer_position: int = 1
    """ Position of the layer """

    def _render_(self, ax: MPLAxis) -> None:
        """
        Renders the artist on the given ax.

        :param      ax:   Matplotlib axis
        :type       ax:   MPLAxis

        :returns:   No returns
        :rtype:     None
        """
        if self.line_style is None:
            self.line_style = next(linecycler)

        ax.mpl_ax.fill_between(
            self.x * self.x_scale_factor,
            self.y0 * self.y_scale_factor,
            self.y1 * self.y_scale_factor,
            color=self.color,
            linestyle=self.line_style,
            alpha=0.7,
            label=self.label,
            zorder=self.layer_position
        )

        if self.show_outline:
            ax.mpl_ax.plot(
                self.x * self.x_scale_factor,
                self.y1 * self.y_scale_factor,
                color='k',
                linestyle='-',
                linewidth=self.line_width,
                zorder=self.layer_position
            )

            ax.mpl_ax.plot(
                self.x * self.x_scale_factor,
                self.y0 * self.y_scale_factor,
                color='k',
                linestyle='-',
                linewidth=self.line_width,
                zorder=self.layer_position
            )


@dataclass(slots=True)
class STDLine():
    x: numpy.ndarray
    """ Array representing the x axis """
    y_mean: numpy.ndarray
    """ Array representing the mean value of y axis """
    y_std: numpy.ndarray
    """ Array representing the standard deviation value of y axis """
    label: str = ""
    """ Label to be added to the plot """
    color: str = None
    """ Color for the artist to be ploted """
    line_style: str = None
    """ Line style for the y_mean line default is straight lines '-' """
    line_width: float = 1
    """ Line width of the artists """
    x_scale_factor: float = 1
    """ Scaling factor for the x axis """
    y_scale_factor: float = 1
    """ Scaling factor for the y axis """
    layer_position: int = 1
    """ Position of the layer """

    def _render_(self, ax: MPLAxis):
        """
        Renders the artist on the given ax.

        :param      ax:   Matplotlib axis
        :type       ax:   MPLAxis

        :returns:   No returns
        :rtype:     None
        """
        if self.line_style is None:
            self.line_style = '-'

        y0 = self.y_mean - self.y_std / 2
        y1 = self.y_mean + self.y_std / 2

        line = ax.mpl_ax.plot(
            self.x * self.x_scale_factor,
            self.y_mean * self.y_scale_factor,
            color=self.color,
            linestyle=self.line_style,
            linewidth=self.line_width,
            zorder=self.layer_position
        )

        ax.mpl_ax.fill_between(
            self.x * self.x_scale_factor,
            y0 * self.y_scale_factor,
            y1 * self.y_scale_factor,
            color=line[-1].get_color(),
            linestyle='-',
            alpha=0.3,
            label=self.label,
            zorder=self.layer_position
        )


@dataclass
class Line():
    y: numpy.ndarray
    """ Array representing the y axis """
    x: numpy.ndarray = None
    """ Array representing the x axis, if not defined a numpy arrange is used instead """
    label: str = ""
    """ Label to be added to the plot """
    color: str = None
    """ Color for the artist to be ploted """
    line_style: str = '-'
    """ Line style for the unique line default is next in cycle """
    line_width: float = 1
    """ Line width of the artists """
    x_scale_factor: float = 1
    """ Scaling factor for the x axis """
    y_scale_factor: float = 1
    """ Scaling factor for the y axis """
    layer_position: int = 1
    """ Position of the layer """

    def __post_init__(self):
        if self.x is None:
            self.x = numpy.arange(len(self.y))

        self.y = numpy.asarray(self.y) * self.y_scale_factor
        self.x = numpy.asarray(self.x) * self.x_scale_factor

    def _render_(self, ax: MPLAxis):
        """
        Renders the artist on the given ax.

        :param      ax:   Matplotlib axis
        :type       ax:   MPLAxis

        :returns:   No returns
        :rtype:     None
        """
        if isinstance(self.line_style, str) and self.line_style.lower() == 'random':
            self.line_style = next(linecycler)

        if numpy.iscomplexobj(self.y):
            if ax.y_scale in ['log', 'logarithmic'] and (self.y.real.min() < 0 or self.y.imag.min() < 0):
                raise ValueError('Cannot plot negative value data on logarithmic scale!')

            ax.mpl_ax.plot(
                self.x,
                self.y.real,
                label=self.label + "[real]",
                color=self.color,
                linestyle=self.line_style,
                linewidth=self.line_width,
                zorder=self.layer_position
            )

            ax.mpl_ax.plot(
                self.x,
                self.y.imag,
                label=self.label + "[imag]",
                color=self.color,
                linestyle=self.line_style,
                linewidth=self.line_width,
                zorder=self.layer_position
            )

        else:
            x = self.x * self.x_scale_factor
            y = self.y * self.y_scale_factor

            if ax.y_scale in ['log', 'logarithmic'] and self.y.real.min() < 0:
                raise ValueError('Cannot plot negative value data on logarithmic scale!')

            ax.mpl_ax.plot(
                x,
                y,
                label=self.label,
                color=self.color,
                linestyle=self.line_style,
                linewidth=self.line_width,
                zorder=self.layer_position
            )


@dataclass(slots=True)
class Table():
    table_values: list
    column_labels: list = None
    row_labels: list = None
    position: str = 'top'
    cell_color: str = None
    text_position: str = 'center'

    def __post_init__(self):
        self.table_values = numpy.array(self.table_values, dtype=object)
        self.table_values = numpy.atleast_2d(self.table_values)
        n_rows, n_columns = numpy.shape(self.table_values)

        if self.row_labels is None:
            self.row_labels = [''] * n_rows

        if self.column_labels is None:
            self.column_labels = [''] * n_columns

    def _render_(self, ax: MPLAxis):
        """
        Renders the artist on the given ax.

        :param      ax:   Matplotlib axis
        :type       ax:   MPLAxis

        :returns:   No returns
        :rtype:     None
        """
        table = ax.mpl_ax.table(
            cellText=self.table_values,
            rowLabels=self.row_labels,
            colLabels=self.column_labels,
            loc=self.position,
            cellColours=self.cell_color,
            cellLoc=self.text_position,
        )

        return table


@dataclass(slots=True)
class VerticalLine():
    x: float
    """ Array representing the x axis, if not defined a numpy arrange is used instead """
    y_min: float = None
    """ Array representing the y axis """
    y_max: float = None
    """ Array representing the y axis """
    label: str = None
    """ Label to be added to the plot """
    color: str = None
    """ Color for the artist to be ploted """
    line_style: str = '-'
    """ Line style for the unique line default is next in cycle """
    line_width: float = 1
    """ Line width of the artists """
    x_scale_factor: float = 1
    """ Scaling factor for the x axis """
    y_scale_factor: float = 1
    """ Scaling factor for the y axis """
    layer_position: int = 1
    """ Position of the layer """

    def _render_(self, ax: MPLAxis):
        """
        Renders the artist on the given ax.

        :param      ax:   Matplotlib axis
        :type       ax:   MPLAxis

        :returns:   No returns
        :rtype:     None
        """
        if isinstance(self.line_style, str) and self.line_style.lower() == 'random':
            self.line_style = next(linecycler)

        ax.mpl_ax.vlines(
            x=self.x * self.x_scale_factor,
            ymin=self.y_min,
            ymax=self.y_max,
            colors=self.color,
            label=self.label,
            linestyle=self.line_style,
            linewidth=self.line_width,
            zorder=self.layer_position
        )


@dataclass(slots=True)
class HorizontalLine():
    y: float
    """ Array representing the x axis, if not defined a numpy arrange is used instead """
    x_min: float = None
    """ Array representing the x axis """
    x_max: float = None
    """ Array representing the x axis """
    label: str = None
    """ Label to be added to the plot """
    color: str = 'black'
    """ Color for the artist to be ploted """
    line_style: str = '-'
    """ Line style for the unique line default is next in cycle """
    line_width: float = 1
    """ Line width of the artists """
    x_scale_factor: float = 1
    """ Scaling factor for the x axis """
    y_scale_factor: float = 1
    """ Scaling factor for the y axis """
    layer_position: int = 1
    """ Position of the layer """

    def _render_(self, ax: MPLAxis):
        """
        Renders the artist on the given ax.

        :param      ax:   Matplotlib axis
        :type       ax:   MPLAxis

        :returns:   No returns
        :rtype:     None
        """
        if isinstance(self.line_style, str) and self.line_style.lower() == 'random':
            self.line_style = next(linecycler)

        ax.mpl_ax.hlines(
            y=self.y * self.y_scale_factor,
            xmin=self.x_min,
            xmax=self.x_max,
            colors=self.color,
            label=self.label,
            linestyle=self.line_style,
            linewidth=self.line_width,
            zorder=self.layer_position
        )


@dataclass(slots=True)
class Scatter():
    y: numpy.ndarray
    """ Array representing the y axis """
    x: numpy.ndarray = None
    """ Array representing the x axis, if not defined a numpy arrange is used instead """
    label: str = None
    """ Label to be added to the plot """
    color: str = 'black'
    """ Color for the artist to be ploted """
    marker: str = 'o'
    """ Line style for the unique line default is next in cycle """
    marker_size: float = 4
    """ Size of the markers """
    line_style: str = 'None'
    """ Line style for the unique line default is next in cycle """
    line_width: str = 1
    """ Line style for the unique line default is next in cycle """
    alpha: float = 0.7
    """ Opacity of the polygon to be plotted """
    edge_color: str = 'black'
    """ Scatter edge color """
    x_scale_factor: float = 1
    """ Scaling factor for the x axis """
    y_scale_factor: float = 1
    """ Scaling factor for the y axis """
    layer_position: int = 1
    """ Position of the layer """

    def __post_init__(self):
        if self.x is None:
            self.x = numpy.arange(len(self.y))

        self.y = numpy.asarray(self.y)
        self.x = numpy.asarray(self.x)

    def _render_(self, ax: MPLAxis):
        """
        Renders the artist on the given ax.

        :param      ax:   Matplotlib axis
        :type       ax:   MPLAxis

        :returns:   No returns
        :rtype:     None
        """
        ax.mpl_ax.scatter(
            self.x * self.x_scale_factor,
            self.y * self.y_scale_factor,
            label=self.label,
            color=self.color,
            marker=self.marker,
            s=self.marker_size,
            edgecolor=self.edge_color,
            linestyle=self.line_style,
            linewidth=self.line_width,
            alpha=self.alpha,
            zorder=self.layer_position
        )


@dataclass(slots=True)
class Text():
    text: str
    """ String to be plotted """
    position: tuple = (0.0, 0.0)
    """ Box position of the text """
    font_size: int = 8
    """ Font size of the text """
    weight: str = 'normal'
    """ Weight of the text """
    color: str = 'black'
    """ Color of the text """
    add_box: bool = False
    """ Boolean to enable a box around the text """
    layer_position: int = 1
    """ Position of the layer """
    localisation: str = 'lower right'
    """ Localisation of the text """

    def _render_(self, ax: MPLAxis):
        """
        Renders the artist on the given ax.

        :param      ax:   Matplotlib axis
        :type       ax:   MPLAxis

        :returns:   No returns
        :rtype:     None
        """
        artist = AnchoredText(
            self.text,
            loc=self.localisation,
            prop=dict(size=self.font_size, color=self.color, weight=self.weight, position=(0, 0)),
            frameon=self.add_box,
            bbox_to_anchor=self.position,
            bbox_transform=ax.mpl_ax.transData,  # ax.mpl_ax.transAxes,
            borderpad=0,
        )

        ax.mpl_ax.get_figure().add_artist(artist)


@dataclass(slots=True)
class WaterMark():
    text: str
    """ String to be plotted """
    position: tuple = (0.5, 0.1)
    """ Box position of the text """
    font_size: int = 30
    """ Font size of the text """
    weight: str = 'normal'
    """ Weight of the text """
    color: str = 'black'
    """ Color of the text """
    add_box: bool = False
    """ Boolean to enable a box around the text """
    layer_position: int = 1
    """ Position of the layer """
    localisation: str = 'lower right'
    """ Localisation of the text """
    alpha: float = 0.2
    """ Transparency of the text"""
    rotation: float = 45
    """ Rotation of the text """

    def _render_(self, ax: MPLAxis) -> None:
        """
        Renders the artist on the given ax.

        :param      ax:   Matplotlib axis
        :type       ax:   MPLAxis

        :returns:   No returns
        :rtype:     None
        """
        ax.mpl_ax.text(
            *self.position,
            self.text,
            transform=ax.mpl_ax.transAxes,
            fontsize=self.font_size,
            color=self.color,
            alpha=self.alpha,
            rotation=self.rotation,
            ha='center',
            va='baseline',
            zorder=-2
        )


@dataclass(slots=True)
class AxAnnotation():
    text: str = ""
    font_size: int = 18
    font_weight: str = 'bold'
    position: tuple = (-0.08, 1.08)

    def _render_(self, ax: MPLAxis) -> None:
        """
        Renders the artist on the given ax.

        :param      ax:   Matplotlib axis
        :type       ax:   MPLAxis

        :returns:   No returns
        :rtype:     None
        """
        ax.mpl_ax.text(
            *self.position,
            self.text,
            transform=ax.mpl_ax.transAxes,
            size=self.font_size,
            weight=self.font_weight
        )


@dataclass(slots=True)
class PatchPolygon():
    coordinates: numpy.ndarray = None
    """ Coordinate of the vertices """
    name: str = ''
    """ Name to be added to the plot next to the polygon """
    alpha: float = 0.4
    """ Opacity of the polygon to be plotted """
    facecolor: str = 'lightblue'
    """ Color for the interior of the polygon """
    edgecolor: str = 'black'
    """ Color for the border of the polygon """
    x_scale_factor: float = 1
    """ Scaling factor for the x axis """
    y_scale_factor: float = 1
    """ Scaling factor for the y axis """
    label: str = None
    """ Label to be added to the plot """

    def __post_init__(self):
        self.coordinates = numpy.asarray(self.coordinates)

    def _render_(self, ax: MPLAxis) -> None:
        """
        Renders the artist on the given ax.

        :param      ax:   Matplotlib axis
        :type       ax:   MPLAxis

        :returns:   No returns
        :rtype:     None
        """
        self.coordinates[:, 0] *= self.x_scale_factor
        self.coordinates[:, 1] *= self.y_scale_factor

        polygon = matplotlib.patches.Polygon(
            self.coordinates,
            facecolor=self.facecolor,
            alpha=self.alpha,
            edgecolor=self.edgecolor,
            label=self.label
        )

        ax.mpl_ax.add_patch(polygon)

        ax.mpl_ax.autoscale_view()


@dataclass(slots=True)
class PatchCircle():
    position: tuple
    """ Position of the center """
    radius: float
    """ Radius of the circle """
    name: str = ''
    """ Name to be added to the plot next to the polygon """
    alpha: float = 0.4
    """ Opacity of the polygon to be plotted """
    facecolor: str = 'lightblue'
    """ Color for the interior of the polygon """
    edgecolor: str = 'black'
    """ Color for the border of the polygon """
    x_scale_factor: float = 1
    """ Scaling factor for the x axis """
    y_scale_factor: float = 1
    """ Scaling factor for the y axis """
    label: str = None
    """ Label to be added to the plot """

    def __post_init__(self):
        self.position = numpy.asarray(self.position)

    def _render_(self, ax: MPLAxis) -> None:
        """
        Renders the artist on the given ax.

        :param      ax:   Matplotlib axis
        :type       ax:   MPLAxis

        :returns:   No returns
        :rtype:     None
        """
        self.position[0] *= self.x_scale_factor
        self.position[1] *= self.y_scale_factor

        polygon = matplotlib.patches.Circle(
            self.position,
            self.radius,
            facecolor=self.facecolor,
            alpha=self.alpha,
            edgecolor=self.edgecolor,
            label=self.label
        )

        ax.mpl_ax.add_patch(polygon)

        ax.mpl_ax.autoscale_view()


# -

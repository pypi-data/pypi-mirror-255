#   !/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
import pyvista
import numpy
from MPSPlots.colormaps import blue_black_red


@dataclass
class UnstructuredMesh():
    coordinates: numpy.ndarray
    colormap: object = field(default_factory=lambda: blue_black_red)
    symmetric_map: bool = True
    render_as_spheres: bool = True
    point_size: int = 100
    """ Size of the points in the plot """
    scalar_coloring: numpy.ndarray = None
    """ Scalar field for the coloring of the mesh """
    symmetric_colormap: bool = False
    """ If true the colormap will be symmetric """

    def get_colormap_limits(self):
        if self.scalar_coloring.std() == 0:
            return [-1, 1]

        if self.symmetric_colormap:
            max_abs = numpy.abs(self.scalar_coloring).max()
            return [-max_abs, max_abs]
        else:
            return None

    def _render_(self, ax) -> None:
        ax.scene.figure.subplot(*ax.plot_number)

        if self.scalar_coloring is not None:
            self.scalar_coloring = self.scalar_coloring.ravel(order='f')
            color_map_limit = self.get_colormap_limits()
        else:
            color_map_limit = None

        self.coordinates = numpy.array(self.coordinates).T

        points = pyvista.wrap(self.coordinates)

        self.mapper = ax.scene.figure.add_points(
            points,
            scalars=self.scalar_coloring,
            point_size=20,
            render_points_as_spheres=self.render_as_spheres,
            cmap=self.colormap,
            clim=color_map_limit,
            show_scalar_bar=False
        )


@dataclass
class ColorBar():
    artist: object
    title: str = ''
    n_labels: int = 5
    label_font_size: int = 20
    width: float = 0.4

    def _render_(self, ax) -> None:
        ax.scene.figure.subplot(*ax.plot_number)

        ax.scene.figure.add_scalar_bar(
            mapper=self.artist.mapper.mapper,
            title=self.title,
            n_labels=self.n_labels,
            label_font_size=self.label_font_size,
            width=self.width
        )


@dataclass
class Mesh():
    x: numpy.ndarray
    """ The x array """
    y: numpy.ndarray
    """ The y array """
    z: numpy.ndarray
    """ The z array """
    colormap: object = field(default_factory=lambda: blue_black_red)
    """ Colormap used for coloring the scalar, if provided """
    style: str = 'surface'
    """ Style of the mesh ['surface', 'points', 'wireframe'] """
    color: str = None
    """ Color of the plot, it is overrided if scalar is provided """
    opacity: float = 1
    """ Opacity of the object """
    show_edges: bool = True
    """ If True show verticies of the mesh """
    scalar_coloring: numpy.ndarray = None
    """ Scalar field for the coloring of the mesh """
    symmetric_colormap: bool = False
    """ If true the colormap will be symmetric """

    def _render_(self, ax) -> None:
        ax.scene.figure.subplot(*ax.plot_number)

        if self.scalar_coloring is not None:
            self.scalar_coloring = self.scalar_coloring.ravel(order='f')

        mesh = pyvista.StructuredGrid(self.x, self.y, self.z)

        colormap_limits = self.get_colormap_limits()

        self.mapper = ax.scene.figure.add_mesh(
            mesh=mesh,
            cmap=self.colormap,
            scalars=self.scalar_coloring,
            color=self.color,
            style=self.style,
            opacity=self.opacity,
            show_edges=self.show_edges,
            clim=colormap_limits,
            show_scalar_bar=False
        )

    def get_colormap_limits(self):
        if self.symmetric_colormap:
            max_abs = numpy.abs(self.scalar_coloring).max()
            return [-max_abs, max_abs]
        else:
            return None


@dataclass
class UnitSphere():
    radius: float = 1
    """ Radius of the sphere """
    opacity: float = 1
    """ Opacity of the object """

    def _render_(self, ax) -> None:
        ax.scene.figure.subplot(*ax.plot_number)
        sphere = pyvista.Sphere(radius=self.radius)
        ax.scene.figure.add_mesh(sphere, opacity=self.opacity)


@dataclass
class Cone():
    height: float
    """ Radius of the sphere """
    angle: float
    """ Opacity of the object """
    resolution: int = 100
    """ Resolution of the side of the cone """
    center: tuple = (0.0, 0.0, 0.0)
    """ Center of the long ax of the cone """
    direction: tuple = (1.0, 0.0, 0.0)
    """ Direction of the cone ax """
    color: str = 'black'
    """ Color of the cone """
    opacity: float = 1
    """ Opacity of the object """

    def _render_(self, ax) -> None:
        ax.scene.figure.subplot(*ax.plot_number)
        cone = pyvista.Cone(
            center=self.center,
            direction=self.direction,
            height=self.height,
            resolution=self.resolution,
            angle=self.angle
        )
        ax.scene.figure.add_mesh(cone, color=self.color, opacity=self.opacity)


@dataclass
class UnitAxis():
    show_label: bool = False
    """ Is x, y, z printed or not """

    def _render_(self, ax) -> None:
        ax.scene.figure.subplot(*ax.plot_number)
        ax.scene.figure.add_axes_at_origin(
            labels_off=not self.show_label,
        )


@dataclass
class UnitThetaVector():
    n_points: int = 10
    """ Number of arrows in each axis (2) """
    radius: float = 1
    """ Distance from center at which arrows are placed """
    color: str = 'black'
    """ Color of the arrows """
    opacity: float = 1
    """ Opacity of the object """

    def _render_(self, ax) -> None:
        ax.scene.figure.subplot(*ax.plot_number)

        theta = numpy.arange(0, 360, self.n_points)
        phi = numpy.arange(180, 0, -self.n_points)

        vector = numpy.array([1, 0, 0])

        x, y, z = pyvista.transform_vectors_sph_to_cart(
            theta,
            phi,
            self.radius,
            *vector
        )

        vector = numpy.c_[x.ravel(), y.ravel(), z.ravel()]

        spherical_vector = pyvista.grid_from_sph_coords(
            theta,
            phi, self.radius
        )

        spherical_vector.point_data["component"] = vector * 0.1

        vectors = spherical_vector.glyph(
            orient="component",
            scale="component",
            tolerance=0.005
        )

        ax.scene.figure.add_mesh(
            vectors,
            color=self.color,
            opacity=self.opacity
        )


@dataclass
class UnitPhiVector():
    n_points: int = 10
    """ Number of arrows in each axis (2) """
    radius: float = 1
    """ Distance from center at which arrows are placed """
    color: str = 'black'
    """ Color of the arrows """
    opacity: float = 1
    """ Opacity of the object """

    def _render_(self, ax) -> None:
        ax.scene.figure.subplot(*ax.plot_number)

        theta = numpy.arange(0, 360, self.n_points)
        phi = numpy.arange(180, 0, -self.n_points)

        vector = numpy.array([0, 1, 0])

        x, y, z = pyvista.transform_vectors_sph_to_cart(
            theta,
            phi,
            self.radius,
            *vector
        )

        vector = numpy.c_[x.ravel(), y.ravel(), z.ravel()]

        spherical_vector = pyvista.grid_from_sph_coords(
            theta,
            phi, self.radius
        )

        spherical_vector.point_data["component"] = vector * 0.1

        vectors = spherical_vector.glyph(
            orient="component",
            scale="component",
            tolerance=0.005
        )

        ax.scene.figure.add_mesh(
            vectors,
            color=self.color,
            opacity=self.opacity
        )


@dataclass
class UnitRadialVector():
    n_points: int = 10
    """ Number of arrows in each axis (2) """
    radius: float = 1
    """ Distance from center at which arrows are placed """
    color: str = 'black'
    """ Color of the arrows """
    opacity: float = 1
    """ Opacity of the object """

    def _render_(self, ax) -> None:
        ax.scene.figure.subplot(*ax.plot_number)

        theta = numpy.arange(0, 360, self.n_points)
        phi = numpy.arange(180, 0, -self.n_points)

        vector = numpy.array([0, 0, 1])

        x, y, z = pyvista.transform_vectors_sph_to_cart(
            theta,
            phi,
            self.radius,
            *vector
        )

        vector = numpy.c_[x.ravel(), y.ravel(), z.ravel()]

        spherical_vector = pyvista.grid_from_sph_coords(
            theta,
            phi,
            self.radius
        )

        spherical_vector.point_data["component"] = vector * 0.1

        vectors = spherical_vector.glyph(
            orient="component",
            scale="component",
            tolerance=0.005
        )

        ax.scene.figure.add_mesh(
            vectors,
            color=self.color,
            opacity=self.opacity
        )


@dataclass
class Text():
    string: str = ''

    def _render_(self, ax) -> None:
        ax.scene.figure.subplot(*ax.plot_number)

        ax.scene.figure.add_text(self.string)


# -

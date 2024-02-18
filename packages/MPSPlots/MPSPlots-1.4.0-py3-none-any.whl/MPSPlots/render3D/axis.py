#   !/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass

from MPSPlots.render3D.artist import (
    UnstructuredMesh,
    UnitSphere,
    UnitAxis,
    UnitThetaVector,
    UnitPhiVector,
    UnitRadialVector,
    Mesh,
    Text,
    ColorBar,
    Cone
)


@dataclass
class Axis():
    plot_number: tuple
    scene: object
    colorbar: object = None

    def __repr__(self) -> str:
        return f"3D axis:: Number of artists: {len(self.artist_list)}"

    @property
    def row(self) -> int:
        return self.plot_number[0]

    @property
    def column(self) -> int:
        return self.plot_number[1]

    def add_artist_to_ax(function):
        def wrapper(self, *args, **kwargs):
            artist = function(self, *args, **kwargs)
            self.artist_list.append(artist)

            return artist

        return wrapper

    def __post_init__(self) -> None:
        self.artist_list = []

    @add_artist_to_ax
    def add_unstructured_mesh(self, *args, **kwargs) -> UnstructuredMesh:
        return UnstructuredMesh(*args, **kwargs)

    @add_artist_to_ax
    def add_unit_sphere(self, *args, **kwargs) -> UnitSphere:
        return UnitSphere(*args, **kwargs)

    @add_artist_to_ax
    def add_cone(self, *args, **kwargs) -> Cone:
        return Cone(*args, **kwargs)

    @add_artist_to_ax
    def add_unit_axis(self, *args, **kwargs) -> UnitAxis:
        return UnitAxis(*args, **kwargs)

    @add_artist_to_ax
    def add_unit_theta_vector(self, *args, **kwargs) -> UnitThetaVector:
        return UnitThetaVector(*args, **kwargs)

    @add_artist_to_ax
    def add_unit_phi_vector(self, *args, **kwargs) -> UnitPhiVector:
        return UnitPhiVector(*args, **kwargs)

    @add_artist_to_ax
    def add_unit_radial_vector(self, *args, **kwargs) -> UnitRadialVector:
        return UnitRadialVector(*args, **kwargs)

    @add_artist_to_ax
    def add_mesh(self, *args, **kwargs) -> Mesh:
        return Mesh(*args, **kwargs)

    @add_artist_to_ax
    def add_text(self, *args, **kwargs) -> Text:
        return Text(*args, **kwargs)

    def add_colorbar(self, *args, **kwargs) -> ColorBar:
        self.colorbar = ColorBar(*args, **kwargs)

    def _render_(self):
        for artist in self.artist_list:
            artist._render_(ax=self)

        if self.colorbar is not None:
            self.colorbar._render_(ax=self)

# -

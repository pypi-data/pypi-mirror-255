#   !/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass

import numpy
import pyvista

from MPSPlots.render3D.axis import Axis


@dataclass
class SceneList:
    unit_size: tuple = (600, 600)
    """ Size of the individual axis composing the scene """
    background_color: str = 'white'
    """ Background of the rendering """
    ax_orientation: str = 'horizontal'

    def __post_init__(self) -> None:
        self.axis_list = []

    def __repr__(self) -> str:
        return f"3D scene:: Number of axis: {len(self.axis_list)}"

    def get_next_plot_number(self) -> tuple:
        if len(self.axis_list) == 0:
            return (0, 0)

        last_axis = self.axis_list[-1]
        last_plot_number = last_axis.plot_number

        if self.ax_orientation == 'horizontal':
            return last_plot_number[0], last_plot_number[1] + 1

        if self.ax_orientation == 'vertical':
            return last_plot_number[0] + 1, last_plot_number[1]

    def append_ax(self) -> Axis:
        plot_number = self.get_next_plot_number()

        ax = Axis(
            plot_number=plot_number,
            scene=self
        )

        self.axis_list.append(ax)

        return ax

    def get_shape(self) -> tuple:
        return (self.number_of_rows, self.number_of_columns)

    @property
    def number_of_columns(self) -> int:
        columns = [ax.column for ax in self.axis_list]
        return numpy.max(columns) + 1

    @property
    def number_of_rows(self) -> int:
        rows = [ax.row for ax in self.axis_list]
        return numpy.max(rows) + 1

    def show(self, save_directory: str = None):
        shape = self.get_shape()

        self.window_size = (self.unit_size[1] * shape[1], self.unit_size[0] * shape[0])

        self.figure = pyvista.Plotter(
            theme=pyvista.themes.DocumentTheme(),
            window_size=self.window_size,
            shape=shape,
        )

        self.figure.set_background(self.background_color)

        for ax in self.axis_list:
            ax._render_()

        self.figure.show(
            screenshot=save_directory,
            window_size=self.window_size,
        )

        return self

    def close(self):
        self.figure.close()

# -

#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2024 Yang 
# pdf-tool - canvas
# ==========================================
#
#
# 
"""
from typing import List, Tuple, Union, Mapping
from .area import Area, COLOR_PALETTE
from .plotarea import PlotArea


class Canvas(Area):
    def __init__(self, clip_outside_plot_areas: bool = True, **options):
        super(Canvas, self).__init__(**options)
        # self._background_color = COLOR_PALETTE["white"]
        self._clip_outside_plot_areas = clip_outside_plot_areas
        self._plot_areas: List[PlotArea] = []

    def _add_plot_area(self, plt: PlotArea):
        if not isinstance(plt, PlotArea):
            raise TypeError(f"The given argument is not a instance of PlotArea")
        self._plot_areas.append(plt)
        if self._clip_outside_plot_areas:
            self.clip_outside_plotareas()

    def add_plot_area(self, plt: PlotArea = None, name: str = None,
                      plot_area: Tuple[Union[int, float], ...] = (0, 0, 0, 0),
                      plot_scale: Tuple[Union[int, float], ...] = (0, 100, 0, 100), **options):
        """
        Args:
            plt: PlotArea instance
            name: PlotArea name, mandatory when plt is not given
            plot_area: plot area defined by four numbers (left margin, bottom margin, with, height)
                       relative to the canvas. Note that these four number should be in range [0, 1]
            plot_scale: plot scale defined by (xMin, xMax, yMin, yMax)

        Returns:

        """
        if plt is None and name is not None:
            plot_width, plot_height = self._width * plot_area[2], self._height * plot_area[3]
            margin_left = self._margin_left + self._width * plot_area[0]
            margin_bottom = self._margin_bottom + self._height * plot_area[1]
            plt = PlotArea(name=name, margin_left=margin_left, margin_bottom=margin_bottom,
                           width=plot_width, height=plot_height, scale=plot_scale, unit="pt", **options)
        self._add_plot_area(plt)
        return plt

    def clip_outside_plotareas(self, clip_outside_plot_areas=None):
        if clip_outside_plot_areas is not None:
            self._clip_outside_plot_areas = clip_outside_plot_areas
        if self.has_comp("__ClipOutsidePlotAreas"):
            self.del_component(self.get_comp(comp_name="__ClipOutsidePlotAreas"))
        if not self._clip_outside_plot_areas:
            return
        wind_inside_rects = [
            (plt._margin_left, plt._margin_bottom, plt._width, plt._height) for plt in self._plot_areas]
        self.rect(name="__ClipOutsidePlotAreas", left_bottom=(0, 0), width=self._width, height=self._height,
                  wind_style="WIND_EVEN_ODD",
                  wind=True, wind_inside_rects=wind_inside_rects)

    def plot_area(self, name="", default=...):
        try:
            return next(filter(lambda x: x._name == name, self._plot_areas))
        except StopIteration and not isinstance(default, ellipsis):
            return default

    def text(self, x, y, unit="pt", **options):
        x, y = self.unit_to_points(x, y, unit)
        return super(Canvas, self).text(x=x, y=y, **options)

    def line(self, start: List[int], end: List[int], unit="pt", **options):
        start = self.unit_to_points(*start, unit)
        end = self.unit_to_points(*end, unit)
        return super(Canvas, self).line(start=list(start), end=list(end), **options)

    def rect(self, left_bottom: Union[list, tuple], width: Union[int, float], height: Union[int, float],
             unit: str = "pt", **options):
        left_bottom = self.unit_to_points(*left_bottom, unit=unit)
        width, height = self.unit_to_points(width, height, unit=unit)
        return super(Canvas, self).rect(left_bottom=left_bottom, width=width, height=height, **options)

    def scatter(self, x: Union[int, float], y: Union[int, float], unit: str = "pt", **options):
        x, y = self.unit_to_points(x, y, unit)
        return super(Canvas, self).scatter(x=x, y=y, **options)

    def all_components(self):
        return self._components + [comp for plt in self._plot_areas for comp in plt._components]

    def left_bottom(self, lb: Tuple[Union[int, float], ...] = None):
        """
        note that positions of all components including components of the plot area
        will be changed correspondingly
        Args:
            lb:

        Returns:
        """
        if lb is not None:
            diff = [lb[0] - self._margin_left, lb[1] - self._margin_bottom]
            for comp in self.all_components():
                self.move_comp(comp, diff=diff)
            self._margin_left, self._margin_bottom = lb

        return self._margin_left, self._margin_bottom

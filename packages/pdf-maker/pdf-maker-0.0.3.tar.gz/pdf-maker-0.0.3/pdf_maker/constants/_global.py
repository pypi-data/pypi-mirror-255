#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2024 Yang 
# pdf-tool - global
# ==========================================
#
#
# 
"""
import os
from typing import List, Mapping, Union


SOURCE_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources")


FONT_LIB = {
    "arial": os.path.join(SOURCE_ROOT, "font\\arial.xml"),
    "Arial": os.path.join(SOURCE_ROOT, "font\\arial.xml"),
    "helvetica": os.path.join(SOURCE_ROOT, "font\\helvetica.xml"),
    "Helvetica": os.path.join(SOURCE_ROOT, "font\\helvetica.xml"),
    "helvetica-normal": os.path.join(SOURCE_ROOT, "font\\helvetica-normal.ttf"),
    "Helvetica-Normal": os.path.join(SOURCE_ROOT, "font\\helvetica-normal.ttf"),
    "AdobeSongStd-Light": os.path.join(SOURCE_ROOT, "font\\AdobeSongStd-Light.otf"),
}


COLOR_PALETTE: dict = {
    "black": [0, 0, 0],
    "red": [1, 0, 0],
    "green": [0, 1, 0],
    "blue": [0, 0, 1],
    "white": [1, 1, 1],
    "yellow": [1, 1, 0],
    "magenta": [1, 0, 1],
    "cyan": [0, 1, 1],
    "grey": [0.5, 0.5, 0.5],

    "myColor1": [0.145, 0.54, 0.745],  # #2596be rgb(37, 150, 190)
    "myColor2": [0.671, 0.859, 0.89],  # #abdbe3 rgb(171,219,227)
}


PAGE_SIZE: dict = {
    "a3": (842, 1191),
    "a4": (595, 842),
    "a5": (420, 595),
    "b5": (516, 729),
    "letter": (612, 792),
    "legal": (612, 1008),
}

ALIGN: List[str] = [
    "left_top", "middle_top", "right_top",
    "left_center", "middle_center", "right_center",
    "left_bottom", "middle_bottom", "right_bottom",
]

UNIT: Mapping[str, Union[int, float]] = {
    "cm": 0.393701, "inch": 1.0, "mm": 0.0393701, "point": 1, "pt": 1
}

LINE_STYLE: Mapping[str, Union[int, float]] = {
    "solid": ...,
    "dotted": (1, 1),
    "dashed": (5, 5),
    "dashdot": (5, 2, 1, 2),
    "densely_dashed": (5, 1),
    "loosely_dashed": (5, 10),
    "densely_dotted": (1, 10),
    "loosely_dotted": (1, 1),
}

WIND = ["WIND_EVEN_ODD", "WIND_NON_ZERO"]

KEYNAMES = [
    "__ClipOutsidePlotAreas", "__CanvasFrame"
]

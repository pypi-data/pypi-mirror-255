#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2024 Yang 
# pdf-tool - comps
# ==========================================
#
#
# 
"""
import re
from fontTools.ttLib import TTFont
from pdf_maker.constants._global import FONT_LIB, COLOR_PALETTE, LINE_STYLE, WIND
from typing import Tuple, Union, List
from xml.etree import ElementTree


class BaseContent:
    def __init__(self, name: str = "", z_index: int = 0, **options):
        self._name = name
        self._z_index = z_index
        for key, value in options.items():
            names = [key, f"_{key.lower()}"]
            for name in names:
                if hasattr(self, name) and not callable(getattr(self, name)):
                    setattr(self, name, value)

        self._code: str = ""

    def code(self):
        return ""

    def name(self):
        return self._name

    def z_index(self):
        return self._z_index


class Text(BaseContent):
    def __init__(self, font_name, size, x, y, text, font, **options):
        self._font_name = font_name  # font name defined in page resources
        self._font = font
        self._size = size
        self._x = x
        self._y = y
        self._text = text
        self._sub_size = int(self._size * 2. / 3.)
        self._sup_size = int(self._size * 2. / 3.)
        self._sub_Ts = -int(self._size * 1. / 4.)
        self._sup_Ts = int(self._size * 1. / 3.)
        self._color = COLOR_PALETTE.get('black', [0, 0, 0])
        self._line_space = 1.3
        self._line_height = 0

        super().__init__(**options)

        if isinstance(self._color, str):
            self._color = COLOR_PALETTE.get(self._color, [0, 0, 0])

        self.code()

    def code(self):
        self._line_height = ((abs(self._sub_Ts)) + max(
            (abs(self._sup_Ts) + self.get_text_height(self._text, self._font, self._sup_size)),
            self.get_text_height(self._text, self._font, self._size))) * self._line_space
        text_list = self.read_rich_text(self._text)
        self._code = f"BT\n{self._x} {self._y} Td\n" + "\n".join([f"/{self._font_name} {self.size(script)} Tf\n{color} rg\n{color} RG\n{self.Ts(script)} Ts\n{f'0 -{self._line_height} Td' if r == 'r' else ''}\n({item}) Tj" for (item, script, color, r) in text_list]) + "\nET"
        return self._code

    def size(self, flag: str):
        if flag == "sub": return self._sub_size
        if flag == "sup": return self._sup_size
        return self._size

    def Ts(self, flag: str):
        if flag == "sub": return self._sub_Ts
        if flag == "sup": return self._sup_Ts
        return 0

    def read_rich_text(self, text):
        rich_text_list = self.read_script(text)
        rich_text_list = [(color[0], script[1], color[1]) for script in rich_text_list for color in self.read_color(script[0])]
        rich_text_list = [(r[0], script, color, r[1]) for (item, script, color) in rich_text_list for r in self.read_break(item)]
        return rich_text_list

    def read_color(self, rich_text):
        for name, value in COLOR_PALETTE.items():
            if rich_text.startswith(f"<{name}>") and rich_text.endswith(f"</{name}>"):
                return [(rich_text.removeprefix(f"<{name}>").removesuffix(f"</{name}>"), ' '.join([str(i) for i in value]))]

            if f"<{name}>" in rich_text and f"</{name}>" in rich_text:
                reg = f"(<{name}>.*?</{name}>)"
                text_list = re.split(reg, rich_text)
                return [i for item in text_list for i in self.read_color(item)]

        return [(rich_text, ' '.join([str(i) for i in self._color]))]

    def read_script(self, rich_text):
        if rich_text.startswith("<sub>") and rich_text.endswith("</sub>"):
            return [(rich_text.removeprefix("<sub>").removesuffix("</sub>"), "sub")]
        if rich_text.startswith("<sup>") and rich_text.endswith("</sup>"):
            return [(rich_text.removeprefix("<sup>").removesuffix("</sup>"), "sup")]
        if "<sub>" in rich_text and "</sub>" in rich_text:
            text_list = re.split(r"(<sub>.*?</sub>)", rich_text)
            return [i for item in text_list for i in self.read_script(item)]
        if "<sup>" in rich_text and "</sup>" in rich_text:
            text_list = re.split(r"(<sup>.*?</sup>)", rich_text)
            return [i for item in text_list for i in self.read_script(item)]
        return [(rich_text, "normal")]

    def read_break(self, rich_text: str):
        if "<r>" in rich_text:
            text = rich_text.split("<r>")
            return [(text[0], ""), (text[1], "r")]
        return [(rich_text, "")]

    @staticmethod
    def to_chr(code: str):
        return "".join([chr(int(f"0x{each}", 16)) for each in code.lstrip("FEFF").split(" ")])

    @staticmethod
    def get_text_width(text: str, font: str, size: int):
        font = TTFont(FONT_LIB.get(str(font).lower()))
        cmap = font['cmap']
        t = cmap.getcmap(3, 1).cmap
        s = font.getGlyphSet()
        pixels_per_em = font['head'].unitsPerEm
        total = 0
        for c in text:
            if ord(c) in t and t[ord(c)] in s:
                total += s[t[ord(c)]].width
            else:
                total += s['.notdef'].width
        total = total * float(size) / pixels_per_em
        return int(total)

    @staticmethod
    def get_text_height(text: str, font: str, size: int):
        # font = TTFont(FONT_LIB.get(str(font).lower()))
        # pixels_per_em = font['head'].unitsPerEm
        # ascender = font['OS/2'].sTypoAscender
        # descender = font['OS/2'].sTypoDescender
        # line_gap = font['OS/2'].sTypoLineGap

        tree = ElementTree.parse(FONT_LIB.get(font.lower()))
        root = tree.getroot()
        head_obj = root.find('head')
        OS_2_obj = root.find('OS_2')
        pixels_per_em = head_obj.find("unitsPerEm").attrib['value']
        ascender = OS_2_obj.find("sTypoAscender").attrib['value']
        descender = OS_2_obj.find("sTypoDescender").attrib['value']
        line_gap = OS_2_obj.find("sTypoLineGap").attrib['value']
        line_height = (float(ascender) + float(descender) + float(line_gap)) / float(pixels_per_em) * size
        return int(line_height)


class Line(BaseContent):
    def __init__(self, start, end, line_style: str = "solid", **options):
        self._start = start
        self._end = end
        self._width = 1
        self._line_style = line_style
        self._color = COLOR_PALETTE.get('black', [0, 0, 0])

        super().__init__(**options)

        if isinstance(self._color, str):
            self._color = COLOR_PALETTE.get(self._color, [0, 0, 0])

        self.code()

    def code(self, start=None, end=None, lt: str = None):
        if start is None or end is None:
            start, end = self._start, self._end
        if lt is None:
            lt = self._line_style
        distance = ((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2) ** .5
        if distance == 0:
            return ""
        if lt == "solid":
            color = " ".join([str(i) for i in self._color])
            start = " ".join([str(i) for i in start])
            end = " ".join([str(i) for i in end])
            code = f"{str(self._width)} w\n{color} RG\n{start} m\n{end} l\nS"
        elif lt in ["dashed", "dotted", "densely_dotted", "densely_dashed", "loosely_dashed", "loosely_dotted"]:
            dash_length = LINE_STYLE[lt][0]
            blank_length = LINE_STYLE[lt][1]
            step_x = (dash_length + blank_length) / distance * (end[0] - start[0])
            step_y = (dash_length + blank_length) / distance * (end[1] - start[1])
            add_x = dash_length / distance * (end[0] - start[0])
            add_y = dash_length / distance * (end[1] - start[1])
            code = "\n".join([self.code(
                start=[start[0] + i * step_x, start[1] + i * step_y],
                end=[start[0] + i * step_x + add_x, start[1] + i * step_y + add_y],
                lt="solid") for i in range(int(distance // (dash_length + blank_length) + 1))]
            )
        elif lt == "dashdot":
            step_x = sum(LINE_STYLE[lt]) / distance * (end[0] - start[0])
            step_y = sum(LINE_STYLE[lt]) / distance * (end[1] - start[1])
            add_x_1 = LINE_STYLE[lt][0] / distance * (end[0] - start[0])
            add_y_1 = LINE_STYLE[lt][0] / distance * (end[1] - start[1])
            add_x_2 = sum(LINE_STYLE[lt][:2]) / distance * (end[0] - start[0])
            add_y_2 = sum(LINE_STYLE[lt][:2]) / distance * (end[1] - start[1])
            add_x_3 = sum(LINE_STYLE[lt][:3]) / distance * (end[0] - start[0])
            add_y_3 = sum(LINE_STYLE[lt][:3]) / distance * (end[1] - start[1])
            code = "\n".join(
                ["\n".join([
                    self.code(
                        start=[start[0] + i * step_x, start[1] + i * step_y],
                        end=[start[0] + i * step_x + add_x_1, start[1] + i * step_y + add_y_1],
                        lt="solid"),
                    self.code(
                        start=[start[0] + i * step_x + add_x_2, start[1] + i * step_y + add_y_2],
                        end=[start[0] + i * step_x + add_x_3, start[1] + i * step_y + add_y_3],
                        lt="solid"),
                ]) for i in range(int(distance // sum(LINE_STYLE[lt]) + 1))]
            )
        else:
            raise ValueError(f"line style must be one of f{', '.join(LINE_STYLE.keys())}, but got {lt} instead.")
        return code


class Rect(BaseContent):
    def __init__(self, x, y, width, height, **options):
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._line_width = 1
        self._color = COLOR_PALETTE.get('black', [0, 0, 0])
        self._fill: bool = False
        self._wind: bool = False
        self._wind_color = COLOR_PALETTE.get('white', [1, 1, 1])
        self._wind_style = "WIND_NON_ZERO"
        self._wind_inside_rects: List[Tuple[Union[float, int], ...]] = ...

        super().__init__(**options)

        if isinstance(self._color, str):
            self._color = COLOR_PALETTE.get(self._color, [0, 0, 0])

        self.code()

    def code(self):
        wind = ""
        if self._wind and len(self._wind_inside_rects) > 0:
            rects = '\n'.join([' '.join([str(i) for i in rect]) + ' re' for rect in self._wind_inside_rects])
            wind = f"\n{rects} f{'*' if self._wind_style == 'WIND_EVEN_ODD' else ''}"
        self._code = f"{str(self._line_width)} w\n" \
                     f"{' '.join([str(i) for i in self._color])} RG\n" \
                     f"{(' '.join([str(i) for i in self._wind_color]) + ' rg') if self._wind else ''}\n" \
                     f"{self._x} {self._y} {self._width} {self._height} re {wind}\nS"
        return self._code


class Scatter(BaseContent):
    def __init__(self, x, y, **options):
        """
        Args:
            x: center of the point
            y: center of the point
            **options: type: circle, rectangle
        """
        self._x = x
        self._y = y
        self._size = 5
        self._line_width = 1
        self._fill_color = COLOR_PALETTE.get('black', [0, 0, 0])
        self._stroke_color = COLOR_PALETTE.get('black', [0, 0, 0])
        self._scale_factor = 1
        self._type = "circle"

        super().__init__(**options)

        if isinstance(self._fill_color, str):
            self._fill_color = COLOR_PALETTE.get(self._fill_color, [0, 0, 0])
        if isinstance(self._stroke_color, str):
            self._stroke_color = COLOR_PALETTE.get(self._stroke_color, [0, 0, 0])

        self.code()

    def code(self):
        stroke_color = f"{' '.join([str(i) for i in self._stroke_color])} RG"
        fill_color = f"{' '.join([str(i) for i in self._fill_color])} rg"
        line_width = f"{self._line_width} w"
        line = ""
        if self._type.lower()[:3] == "rec":
            x = self._x - self._size
            y = self._y - self._size * self._scale_factor
            line = f"{x} {y} {self._size * 2} {self._size * self._scale_factor * 2} re b"
        if self._type.lower()[:3] == "cir":
            r = 0.55228 * self._size
            s = (str(self._x - self._size), str(self._y))
            k1 = (str(self._x - self._size), str(r + self._y))
            k2 = (str(self._x - r), str(self._y + self._size))
            e1 = (str(self._x), str(self._y + self._size))
            k3 = (str(self._x + r), str(self._y + self._size))
            k4 = (str(self._x + self._size), str(r + self._y))
            e2 = (str(self._x + self._size), str(self._y))
            k5 = (str(self._x + self._size), str(self._y - r))
            k6 = (str(self._x + r), str(self._y - self._size))
            e3 = (str(self._x), str(self._y - self._size))
            k7 = (str(self._x - r), str(self._y - self._size))
            k8 = (str(self._x - self._size), str(self._y - r))
            e4 = s
            # line = f"{self._x} {self._y} {self._size} 0 360 arc"
            line = f"{' '.join(s)} m\n{' '.join(k1)} {' '.join(k2)} {' '.join(e1)} c\n" \
                   f"{' '.join(k3)} {' '.join(k4)} {' '.join(e2)} c\n" \
                   f"{' '.join(k5)} {' '.join(k6)} {' '.join(e3)} c\n" \
                   f"{' '.join(k7)} {' '.join(k8)} {' '.join(e4)} c\nh B"
        self._code = f"{line_width}\n{stroke_color}\n{fill_color}\n{line}"
        return self._code

#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2024 Yang 
# pdf-tool - objs
# ==========================================
#
#
# 
"""
from typing import List, Union, Tuple
import re
from datetime import datetime, timezone, timedelta
from .comps import BaseContent, Text, Scatter, Line, Rect, FONT_LIB
from xml.etree import ElementTree
import io


class Resources:
    def __init__(self, font, font_index, procset: str = None, **options):
        if procset is None:
            procset = "[/PDF /Text]"
        self._font = font
        self._font_index = font_index
        self._procset = procset
        self._code: str = ...

        self.code()

    def code(self):
        self._code = f"/Procset {self._procset}\n" + "\n".join([
            f"/{key.capitalize()} <<\n"
            f"/{val['name']} {val['index']} 0 R\n>>\n" for key, val in self.to_dict().items()])
        return self._code

    def to_dict(self):
        return {
            "font": {"name": f"{self._font}", "index": f"{self._font_index}"}
        }

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return object.__getattribute__(self, f"_{name}")


class Obj:
    def __init__(self, index, type, **options):
        self._prefix: str = ""
        self._pages: str = ""
        self._basefont = ""
        self._name = ""
        self._index: int = index
        self._type: str = type
        self._kids: List[str] = []
        self._parent: Union[int, str] = ""
        self._contents: Union[int, str] = ""
        self._length: Union[int, str] = ""
        self._mediabox: Union[tuple, list] = [0, 0, 612, 792]
        self._title: str = ""
        self._author: str = ""
        self._producer: str = ""
        self._creator: str = ""
        self._subject: str = ""
        self._keywords: str = ""
        self._creation_date: str = ""
        self._mod_date: str = ""
        self._resources: Resources = ...
        self._text: List[Text] = []
        self._line: List[Line] = []
        self._rect: List[Rect] = []
        self._scatter: List[Scatter] = []
        self._subtype = ""
        self._offset: Union[str, int] = ""
        self._number: Union[str, int] = ""
        self._state: str = "n"
        self._font_name = ""
        self._encoding = ""
        self._base_encoding = ""  # "MacRomanEncoding", "MacExpertEncoding", or "WinAnsiEncoding"
        self._font_bbox = [-166, -225, 1000, 931]
        self._flags = ""
        self._ascent = ""
        self._cap_height = ""
        self._descent = ""
        self._italic_angle = ""
        self._stemv = ""
        self._missing_width = ""
        self._font_descriptor = ""
        self._first_char = ""
        self._last_char = ""
        self._widths = []
        self._differences = []
        self._horizontal_scale = 1

        for key, value in options.items():
            names = [key, f"_{key.lower()}"]
            for name in names:
                if hasattr(self, name) and not callable(getattr(self, name)):
                    setattr(self, name, value)

        self._data = ""
        self._stream = ""

        if self.get_type() == "FontDescriptor":
            tree = ElementTree.parse(FONT_LIB.get(str(self._font_name).lower()))
            root = tree.getroot()
            head_obj = root.find('head')
            hhea_obj = root.find('hhea')
            OS_2_obj = root.find('OS_2')
            post_obj = root.find('post')
            self._flags = head_obj.find("flags").attrib['value']
            xMin = head_obj.find("xMin").attrib['value']
            yMin = head_obj.find("yMin").attrib['value']
            xMax = head_obj.find("xMax").attrib['value']
            yMax = head_obj.find("yMax").attrib['value']
            self._font_bbox = [xMin, yMin, xMax, yMax]
            self._italic_angle = post_obj.find("italicAngle").attrib['value']
            self._ascent = OS_2_obj.find("sTypoAscender").attrib['value']
            self._descent = OS_2_obj.find("sTypoDescender").attrib['value']
            self._ascent = hhea_obj.find("ascent").attrib['value']
            self._descent = hhea_obj.find("descent").attrib['value']
            self._cap_height = OS_2_obj.find("sCapHeight").attrib['value']
            self._font_weight = OS_2_obj.find("usWeightClass").attrib['value']
            # The possible values of font weight are 100, 200, 300, 400, 500, 600, 700, 800, or 900
            self._stemv = int(10 + 220 * (int(OS_2_obj.find("usWeightClass").attrib['value']) - 50) / 900)

            self._avg_char_width = OS_2_obj.find("xAvgCharWidth").attrib['value']
            self._max_char_width = OS_2_obj.find("xAvgCharWidth").attrib['value']
            self._first_char = OS_2_obj.find("usFirstCharIndex").attrib['value']
            self._last_char = OS_2_obj.find("usLastCharIndex").attrib['value']
            self._x_height = OS_2_obj.find("sxHeight").attrib['value']

            self._missing_width = self._avg_char_width

        if self.get_type() == "Font" or self.get_type() == "Encoding":
            tree = ElementTree.parse(FONT_LIB.get(str(self._basefont or self._font_name).lower()))
            root = tree.getroot()
            mtx_objs = root.find('hmtx').findall('mtx')
            map_objs = root.find('cmap').find('cmap_format_4').findall('map')
            OS_2_obj = root.find('OS_2')
            self._missing_width = int(int(OS_2_obj.find("xAvgCharWidth").attrib['value']) * self._horizontal_scale)
            # pixels_per_em = root.find('head').find('unitsPerEm').items()
            # print(pixels_per_em)

            chars = {}
            self._differences = []
            for map_obj in map_objs:
                chars.update({int(map_obj.attrib.get("code"), 16): {"name": map_obj.attrib.get("name")}})
                self._differences.append(f"{int(map_obj.attrib.get('code'), 16)} /{map_obj.attrib.get('name')}")

            chars_list = [(code, char['name'], self._missing_width, "0") for code, char in chars.items()]
            chars_list = sorted(chars_list, key=lambda x: x[0])
            char_names = [char[1] for char in chars_list]
            char_codes = [char[0] for char in chars_list]

            mtx_list = [(mtx.attrib.get('name'), mtx.attrib.get('width'), mtx.attrib.get('lsb')) for mtx in mtx_objs]

            # 选取ASCII 255个标准字符
            self._first_char = 0
            self._last_char = 255
            for i in range(self._first_char, self._last_char + 1):
                if i not in char_codes:
                    chars_list.append((i, "", f"{self._missing_width}", "0"))
                else:
                    name = char_names[char_codes.index(i)]
                    index = [mtx[0] for mtx in mtx_list].index(name)
                    if index != -1:
                        chars_list[char_codes.index(i)] = (
                            i, name, f"{int(int(mtx_list[index][1]) * self._horizontal_scale)}", mtx_list[index][2])
            chars_list = sorted(chars_list, key=lambda x: x[0])
            self._widths = [char[2] for char in chars_list[self._first_char:(self._last_char + 1)]]

    def get_type(self):
        return self._type

    def type(self, type: str = None):
        if type is not None:
            self._type = type
        if self.get_type() in ["Page", "Pages", "Font", "Catalog", "Encoding", "FontDescriptor"]:
            return f"/Type /{self.get_type()}\n"
        return ""

    def data(self):
        data = f"{self.index()} 0 obj\n{self._prefix}\n" \
               f"<<\n{self.type()}{self.kids()}" \
               f"{self.parent()}{self.mediabox()}{self.contents()}{self.resources()}" \
               f"{self.length()}{self.subtype()}{self.name()}{self.first_char()}{self.last_char()}" \
               f"{self.widths()}{self.base_encoding()}{self.differences()}" \
               f"{self.basefont()}{self.encoding()}{self.pages()}{self.font_descriptor()}" \
               f"{self.title()}{self.author()}{self.producer()}{self.creator()}" \
               f"{self.font_bbox()}{self.font_name()}{self.flags()}{self.ascent()}{self.descent()}" \
               f"{self.cap_height()}{self.italic_angle()}{self.stemv()}{self.missing_width()}" \
               f"{self.creation_date()}{self.mod_date()}{self.subject()}{self.keywords()}" \
               f">>\n" \
               f"{self.stream()}" \
               f"endobj\n"
        self._data = data
        return data

    """ Attributes of objects """
    def _base_attr(self, key, val, is_index: bool = False):
        if isinstance(val, str) and val.startswith("/") and val[1:] == "":
            return ""
        if val != "" and val is not None:
            return f"{key} {val} {'0 R' if is_index else ''}\n"
        else:
            return ""

    def pages(self, pages: int = None):
        if self.get_type() != "Catalog":
            return ""
        if pages is not None:
            pass
        if self.get_type() != "Catalog" or not self._pages.isdigit():
            return ""
        return self._base_attr("/Pages", self._pages, True)

    def kids(self, kids: Union[list, int, str] = None):
        if self.get_type() != "Pages":
            return ""
        if kids is not None:
            if isinstance(kids, (int, str)):
                kids = [kids]
            kids = [str(i) for i in kids]
        else:
            kids = []
        for kid in kids:
            self._kids.append(kid)
        kids = ' '.join([f"{i} 0 R" for i in self._kids])
        return f"/Kids [{kids}]\n/Count {len(self._kids)}\n"

    def parent(self, parent: int = None):
        if self.get_type() != "Page":
            return ""
        if parent is not None:
            self._parent = str(parent)
        if not self._parent.isdigit():
            return ""
        return self._base_attr("/Parent", str(self._parent), True)

    def contents(self, contents: int = None):
        if self.get_type() != "Page":
            return ""
        if contents is not None:
            self._contents = str(contents)
        if not self._contents.isdigit():
            return ""
        return self._base_attr("/Contents", str(self._contents), True)

    def resources(self, resources: Resources = None):
        if self.get_type() != "Page":
            return ""
        if resources is not None:
            self._resources = resources
        if not isinstance(self._resources, Resources):
            return ""
        resources = self._resources.code()
        return self._base_attr("/Resources", f"<<\n{resources}>>")

    def length(self, length: int = None):
        if self.get_type() != "Stream":
            return ""
        if length is not None:
            self._length = str(length)
        if not str(self._length).isdigit():
            return ""
        return self._base_attr("/Length", f"{self._length} 0 R")

    def subtype(self, subtype: str = None):
        if self.get_type() != "Font":
            return ""
        if subtype is not None:
            self._subtype = subtype
        return self._base_attr("/Subtype", f"/{self._subtype}")

    def name(self, name: str = None):
        if self.get_type() != "Font":
            return ""
        if name is not None:
            self._name = name
        return self._base_attr("/Name", f"/{self._name}")

    def basefont(self, basefont: str = None):
        if self.get_type() != "Font":
            return ""
        if basefont is not None:
            self._basefont = basefont
        return self._base_attr("/BaseFont", f"/{self._basefont}")

    def encoding(self, encoding: str = None):
        if self.get_type() != "Font":
            return ""
        if encoding is not None:
            self._encoding = encoding
        return self._base_attr("/Encoding", self._encoding, True)

    def base_encoding(self, base_encoding: str = None):
        if self.get_type() != "Encoding":
            return ""
        if base_encoding is not None:
            self._base_encoding = base_encoding
        return self._base_attr("/BaseEncoding", f"/{self._base_encoding}")

    def differences(self, differences=None):
        if self.get_type() != "Encoding":
            return ""
        if differences is not None:
            self._differences = differences
        else:
            try:
                differences = ""
                for index, item in enumerate(self._differences):
                    if (index + 1) % 10 == 0:
                        differences = differences + f"{item}" + "\n"
                    else:
                        differences = differences + f"{item}" + " "
            except (KeyError, AttributeError):
                return ""
        return f"/Differences\n[{differences}]\n"

    def font_descriptor(self, font_descriptor: Union[str, int] = None):
        if self.get_type() != "Font":
            return ""
        if font_descriptor is not None:
            self._font_descriptor = font_descriptor
        return self._base_attr("/FontDescriptor", self._font_descriptor, True)

    def first_char(self, first_char: Union[str, int] = None):
        if self.get_type() != "Font":
            return ""
        if first_char is not None:
            self._first_char = first_char
        return self._base_attr("/FirstChar", self._first_char)

    def last_char(self, last_char: Union[str, int] = None):
        if self.get_type() != "Font":
            return ""
        if last_char is not None:
            self._last_char = last_char
        return self._base_attr("/LastChar", self._last_char)

    def widths(self, widths=None):
        if self.get_type() != "Font":
            return ""
        if widths is not None:
            self._widths = widths
        else:
            try:
                widths = ""
                for index, item in enumerate(self._widths):
                    if (index + 1) % 10 == 0:
                        widths = widths + item + "\n"
                    else:
                        widths = widths + item + " "
            except (KeyError, AttributeError):
                return ""
        return f"/Widths\n[{widths}]\n"

    def mediabox(self, mediabox: Union[tuple, list] = None):
        if self.get_type() != "Page":
            return ""
        if mediabox is not None:
            self._mediabox = mediabox
        return f"/MediaBox [{' '.join([str(i) for i in self._mediabox])}]\n"

    def title(self, title: str = None):
        if self.get_type() != "Info":
            return ""
        if title is not None:
            self._title = title
        return f"/Title ({self._title})\n"

    def author(self, author: str = None):
        if self.get_type() != "Info":
            return ""
        if author is not None:
            self._author = author
        return f"/Author ({self._author})\n"

    def producer(self, producer: str = None):
        if self.get_type() != "Info":
            return ""
        if producer is not None:
            self._producer = producer
        return f"/Producer ({self._producer})\n"

    def subject(self, subject: str = None):
        if self.get_type() != "Info":
            return ""
        if subject is not None:
            self._subject = subject
        return f"/subject ({self._subject})\n"

    def keywords(self, keywords: str = None):
        if self.get_type() != "Info":
            return ""
        if keywords is not None:
            self._keywords = keywords
        return f"/keywords ({self._keywords})\n"

    def creator(self, creator: str = None):
        if self.get_type() != "Info":
            return ""
        if creator is not None:
            self._creator = creator
        return f"/Creator ({self._creator})\n"

    def creation_date(self, creation_date: str = None):
        date = str(datetime.now(tz=timezone(offset=timedelta(hours=8))))
        date = ("D:" + "".join(re.findall(r"(\d*|\+)", date)))[:-2] + "'00'"
        self._creation_date = date
        if self.get_type() != "Info":
            return ""
        if creation_date is not None:
            self._creation_date = creation_date
        return f"/CreationDate ({self._creation_date})\n"

    def mod_date(self, mod_date: str = None):
        date = str(datetime.now(tz=timezone(offset=timedelta(hours=8))))
        date = ("D:" + "".join(re.findall(r"(\d*|\+)", date)))[:-2] + "'00'"
        self._mod_date = date
        if self.get_type() != "Info":
            return ""
        if mod_date is not None:
            self._mod_date = mod_date
        return f"/ModDate ({self._mod_date})\n"

    def font_name(self, font_name: str = None):
        if font_name is not None:
            self._font_name = font_name
        if self.get_type() != "FontDescriptor":
            return ""
        return self._base_attr("/FontName", f"/{self._font_name}")

    def font_bbox(self, font_bbox: List[Union[int, str]] = None):
        if self.get_type() != "FontDescriptor":
            return ""
        if font_bbox is not None:
            self._font_bbox = font_bbox
        return f"/FontBBox [{' '.join([str(i) for i in self._font_bbox])}]\n"

    def flags(self, flags: Union[int, str] = None):
        if self.get_type() != "FontDescriptor":
            return ""
        if flags is not None:
            self._flags = flags
        return self._base_attr("/Flags", self._flags)

    def ascent(self, ascent: Union[int, str] = None):
        if self.get_type() != "FontDescriptor":
            return ""
        if ascent is not None:
            self._ascent = ascent
        return self._base_attr("/Ascent", self._ascent)

    def descent(self, descent: Union[int, str] = None):
        if self.get_type() != "FontDescriptor":
            return ""
        if descent is not None:
            self._descent = descent
        return self._base_attr("/Descent", self._descent)

    def cap_height(self, cap_height: Union[int, str] = None):
        if self.get_type() != "FontDescriptor":
            return ""
        if cap_height is not None:
            self._cap_height = cap_height
        return self._base_attr("/CapHeight", self._cap_height)

    def italic_angle(self, italicangle: Union[int, str] = None):
        if self.get_type() != "FontDescriptor":
            return ""
        if italicangle is not None:
            self._italic_angle = italicangle
        return self._base_attr("/ItalicAngle", self._italic_angle)

    def stemv(self, stemv: Union[int, str] = None):
        if self.get_type() != "FontDescriptor":
            return ""
        if stemv is not None:
            self._stemv = stemv
        return self._base_attr("/StemV", self._stemv)

    def font_weight(self, font_weight: Union[int, str] = None):
        if self.get_type() != "FontDescriptor":
            return ""
        if font_weight is not None and font_weight.isdigit():
            self._font_weight = font_weight
        return self._base_attr("/FontWeight", self._font_weight)

    def missing_width(self, missing_width: Union[int, str] = None):
        if self.get_type() != "FontDescriptor":
            return ""
        if missing_width is not None:
            self._missing_width = missing_width
        return self._base_attr("/MissingWidth", self._missing_width)

    def stream(self):
        if self.get_type() != "Stream":
            return ""
        contents: List[BaseContent] = sorted([*self._text, *self._line, *self._rect, *self._scatter], key=lambda obj: obj.z_index())
        code = '\n'.join([obj.code() for obj in contents])
        self._stream = code
        return f"stream\n{code}\nendstream\n"

    """ Functions """
    def text(self, text: Text):
        self._text.append(text)

    def line(self, line: Line):
        self._line.append(line)

    def rect(self, rect: Rect):
        self._rect.append(rect)

    def scatter(self, scatter: Scatter):
        self._scatter.append(scatter)

    def index(self):
        return str(self._index)

    def offset(self):
        return str(self._offset)

    def number(self):
        return str(self._number)

    def state(self):
        return str(self._state)

    def page_size(self, page_size: Tuple[Union[int, float], ...] = None):
        if page_size is not None:
            self._mediabox = [0, 0, *page_size[:2]]
        return self._mediabox[2:4]

    def get_contents_index(self):
        return self._contents

    def get_font_name(self):
        if self.get_type() == "Page":
            return self._resources.font
        elif self.get_type() == "Font":
            return self._name

    def remove_kid(self, index: Union[str, int]):
        if str(index) in self._kids:
            self._kids.remove(str(index))

    def get_basefont(self):
        return self._basefont

#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2024 Yang 
# pdf-tool - crf
# ==========================================
#
#
# 
"""


class Crf:
    def __init__(self, **options):

        self._startoffset = ""
        self._objs = [{
            "index": "", "type": "", "offset": "", "number": "00000", "state": "n"
        }]

        for key, value in options.items():
            names = [key, f"_{key.lower()}"]
            for name in names:
                if hasattr(self, name) and not callable(getattr(self, name)):
                    setattr(self, name, value)

    def size(self):
        return len(self._objs)

    def update(self):
        return "\n".join([
            f"{self.offset(obj['offset'])} "
            f"{self.number(obj['number'])} "
            f"{obj['state'][0]}" for obj in self._objs])

    def data(self):
        return f"xref\n0 {self.size()}\n{self.update()}\n"

    def startoffset(self):
        return self._startoffset

    @staticmethod
    def offset(offset: str = None):
        if offset is None or not offset.isdigit():
            return "0000000000"
        return f"{'0000000000'[:10-len(offset)] + offset}"

    @staticmethod
    def number(number: str = None):
        if number is None or not number.isdigit():
            return "00000"
        return f"{'00000'[:5-len(number)] + number}"

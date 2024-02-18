#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2024 Yang 
# pdf-tool - base
# ==========================================
#
#
# 
"""


def snake_to_camel(snake: str):
    return "".join([each.capitalize() for each in snake.split("_")])


def camel_to_snake(camel: str):
    return "".join([("_" + each.lower()) if index != 0 and each.capitalize() == each else each for index, each in enumerate(camel)])


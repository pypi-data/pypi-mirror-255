#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
# ==========================================
# Copyright 2024 Yang 
# pdf-maker - warns
# ==========================================
#
#
# 
"""


def custom_warn(message, category, filename, lineno, file=None, line=None):
    print(f"{category.__name__}: {message}")



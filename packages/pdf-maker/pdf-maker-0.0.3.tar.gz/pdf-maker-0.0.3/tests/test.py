"""
# ==========================================
# Copyright 2024 Yang 
# pdf-tool - test
# ==========================================
#
#
# 
"""

import numpy as np
import pdf_maker as pm

file = pm.NewPDF(filepath="myPDF.pdf")
# as default, an empty pdf will have no page
file.add_page()

# create a canvas
cv = pm.Canvas(width=17, height=12, unit="cm", show_frame=True, frame_line_width=1, clip_outside_plot_areas=False)

# add plot areas to the canvas and define coordinate scale,
# the position and widths and heights of the plot area are defined relative to the canvas
# plot_area = (margin_to_left, margin_to_bottom, width, height), plot_scale = (xMin, xMax, yMix, yMax)
pt = cv.add_plot_area(name="Plot1", plot_area=(0.1, 0.1, 0.35, 0.35), plot_scale=(0, 200, 0, 200), show_frame=True)
pt2 = cv.add_plot_area(name="Plot2", plot_area=(0.6, 0.1, 0.35, 0.35), plot_scale=(0, 200, 0, 200), show_frame=True)
pt3 = cv.add_plot_area(name="Plot3", plot_area=(0.12, 0.6, 0.75, 0.35), plot_scale=(0, 200, 0, 200), show_frame=True)

# add text based on coordinate scales. If the position is out of the scale, the item will be not plotted.
pt2.text(name="TEXT02", x=40, y=70, text="AaBbCcDdEeFfGg", size=12, font="Arial", coordinate="scale")
# z_index is used to move it to the top, otherwise they will be plotted based on the sequene of generation,
# and the former shapes will be overlapped by the latters.
pt3.text(name="TEXT03", x=40, y=70, text="This is the first plot area, which has a <red>z-index</red> of 999.", size=12,
         coordinate="scale", z_index=999)

# plot lines and scatters
for i in range(10):
    pt3.line(name=f"LINE_{i}", start=[0, i * 10], end=[300, i * 10 + 50], width=1, color="grey", line_style="solid")

xs = np.random.randint(low=0, high=200, size=10)
ys = np.random.randint(low=0, high=200, size=10)

# name attribute is not mandatory, but they are recommaned for finding they easier.
for x, y in zip(xs, ys):
    pt.scatter(name=f"SCATTER_{x}_{y}", x=x, y=y, size=2, coordinate="scale", fill_color="red" if y <= 100 else "grey")

# eight line styles are supported currently, namely:
#    "solid" "dotted" "dashed" "dashdot" "densely_dashed" "loosely_dashed" "densely_dotted" "loosely_dotted"
for x in range(0, 200, 50):
    pt.line(name=f"LINE_X_{x}", start=[x, 0], end=[x, 300], width=1, color="grey", line_style="dashed")
    pt2.line(name=f"LINE_X_{x}", start=[x, 0], end=[x, 300], width=1, color="grey", line_style="dashed")

for y in range(0, 200, 50):
    pt.line(name=f"LINE_Y_{y}", start=[0, y], end=[300, y], width=1, color="grey", line_style="dashdot")
    pt2.line(name=f"LINE_Y_{y}", start=[0, y], end=[300, y], width=1, color="grey", line_style="dashdot")

# Finally we need to add canvas to a page
# As default, the page index starts from 1 because it is more intuitional. It can be defined as base = 0
file.canvas(page=1, margin_left=1, margin_top=10, canvas=cv, unit="cm")

# add text to page instead of a canvas, in this case the position will be in pixel
# <r> for break, <sup> and <sub> for superscript and subscript respectively.
file.text(page=0, x=200, y=700, line_space=1.2, text=f"Hello World!    <r><sup>=</sup>o<sup>=</sup>", size=36, base=0)

# save pdf
file.save()

# import ararpy as ap
# # open ararpy files
# file_path = r'D:\PythonProjects\pdf-maker\venv\Lib\site-packages\ararpy\examples\22WHA0433.arr'
# sample = ap.from_arr(file_path=file_path)

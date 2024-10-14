import os
from PyQt5 import QtWidgets
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import pandas as pd
from matplotlib.collections import LineCollection
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class nonRectanglePlotWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Climate Spiral")
        self.setGeometry(200, 200, 1000, 800)
        
        self.figure, self.ax = plt.subplots(figsize=(14, 14))

        self.canvas = FigureCanvas(self.figure)
        self.setCentralWidget(self.canvas)
        self.draw_plot()

    def draw_plot(self):

        def segment_circle(num_segments):
            segment_rad = 2 * np.pi / num_segments
            segment_rads = segment_rad * np.arange(num_segments)
            coordX = np.cos(segment_rads)
            coordY = np.sin(segment_rads)
            return np.c_[coordX, coordY, segment_rads]

        r = 7.0
        months = [
            "Mar", "Feb", "Jan", "Dec", "Nov", "Oct", "Sep", "Aug", "Jul", "Jun", "May", "Apr"
        ]
        month_idx = [2, 1, 0, 11, 10, 9, 8, 7, 6, 5, 4, 3]
        radius = r + 0.4
        month_points = segment_circle(len(months))

        df = pd.read_csv("dataset\HadCRUT.5.0.2.0.analysis.summary_series.global.monthly.csv")
        df['Time'] = pd.to_datetime(df['Time'])
        r_factor = r / 3.6
        x_orig = df["Anomaly (deg C)"].to_numpy() + 1.5
        x_vals = []
        y_vals = []
        for i in range(len(x_orig)):
            r_pos = x_orig[i] * r_factor
            x_unit_r, y_unit_r = month_points[month_idx[i % 12], :2]
            x_r, y_r = (r_pos * x_unit_r, r_pos * y_unit_r)
            x_vals.append(x_r)
            y_vals.append(y_r)

        self.ax.patch.set_facecolor("grey")
        self.ax.axis("equal")
        self.ax.set(xlim=(-10, 10), ylim=(-10, 10))

        circle = plt.Circle((0, 0), r, fc="#000000")
        self.ax.add_patch(circle)
        circle_2 = plt.Circle((0, 0), r_factor * 2.5, ec="red", fc=None, fill=False, lw=3.0)
        self.ax.add_patch(circle_2)
        circle_1_5 = plt.Circle((0, 0), r_factor * 3.0, ec="red", fc=None, fill=False, lw=3.0)
        self.ax.add_patch(circle_1_5)

        props_months = {"ha": "center", "va": "center", "fontsize": 24, "color": "white"}
        props_year = {"ha": "center", "va": "center", "fontsize": 36, "color": "white"}
        props_temp = {"ha": "center", "va": "center", "fontsize": 32, "color": "red"}
        self.ax.text(0, r_factor * 2.5, "1.5°C", props_temp, bbox=dict(facecolor="black"))
        self.ax.text(0, r_factor * 3.0, "2.0°C", props_temp, bbox=dict(facecolor="black"))

        # month labels 
        for j in range(len(months)):
            x_unit_r, y_unit_r, angle = month_points[j]
            x_radius, y_radius = (radius * x_unit_r, radius * y_unit_r)
            angle = angle - 0.5 * np.pi
            self.ax.text(x_radius, y_radius, months[j], props_months, rotation=np.rad2deg(angle))

        # create LineCollection
        lc = LineCollection([], cmap=plt.get_cmap("jet"), norm=plt.Normalize(0, 3.6))
        self.ax.add_collection(lc)
        # year text placeholder
        year_text = self.ax.text(0, 0, "", props_year)

        def animate(i):
            if i > 1:
                pts = np.array([x_vals[:i], y_vals[:i]]).T.reshape(-1, 1, 2)
                segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
                lc.set_segments(segs)
                lc.set_array(np.asarray(x_orig[:i]))  # update color array
            year = 1850 + (i // 12)  
            year_text.set_text(str(year))  # year text

        self.anim = FuncAnimation(self.figure, animate, frames=len(x_orig), interval=0.5, repeat=False)
        self.canvas.draw()

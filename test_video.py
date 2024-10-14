import os
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import pandas as pd
from matplotlib.collections import LineCollection


def segment_circle(num_segments):
    """Split a circle into num_segments segments"""
    segment_rad = 2 * np.pi / num_segments
    segment_rads = segment_rad * np.arange(num_segments)
    coordX = np.cos(segment_rads)
    coordY = np.sin(segment_rads)
    return np.c_[coordX, coordY, segment_rads]


# Constants
r = 7.0
months = [
    "Mar",
    "Feb",
    "Jan",
    "Dec",
    "Nov",
    "Oct",
    "Sep",
    "Aug",
    "Jul",
    "Jun",
    "May",
    "Apr",
]
month_idx = [2, 1, 0, 11, 10, 9, 8, 7, 6, 5, 4, 3]
radius = r + 0.4
month_points = segment_circle(len(months))

# Load data
df = pd.read_csv("C:\Hassnaa\QtDesigner_Projects\Task1_Signal_Viewer\dataset\HadCRUT.5.0.2.0.analysis.summary_series.global.monthly.csv")
print("Time: ", df["Time"])

df['Time'] = pd.to_datetime(df['Time'])
print("discription: ",df.describe())
r_factor = r / 3.6
x_orig = df["Anomaly (deg C)"].to_numpy() + 1.5
x_vals = []
y_vals = []
print("len: ", len(x_orig))
for i in range(len(x_orig)):
    r_pos = x_orig[i] * r_factor
    x_unit_r, y_unit_r = month_points[month_idx[i % 12], :2]
    x_r, y_r = (r_pos * x_unit_r, r_pos * y_unit_r)
    x_vals.append(x_r)
    y_vals.append(y_r)
print("x_vals: ", len(x_vals), "Y VALS: ", len(y_vals))

# Prepare the plot
fig, ax = plt.subplots(figsize=(14, 14))
fig.patch.set_facecolor("grey")
ax.axis("equal")
ax.set(xlim=(-10, 10), ylim=(-10, 10))

# Draw circles only once
circle = plt.Circle((0, 0), r, fc="#000000")
ax.add_patch(circle)
circle_2 = plt.Circle((0, 0), r_factor * 2.5, ec="red", fc=None, fill=False, lw=3.0)
ax.add_patch(circle_2)
circle_1_5 = plt.Circle((0, 0), r_factor * 3.0, ec="red", fc=None, fill=False, lw=3.0)
ax.add_patch(circle_1_5)

# Set properties
props_months = {"ha": "center", "va": "center", "fontsize": 24, "color": "white"}
props_year = {"ha": "center", "va": "center", "fontsize": 36, "color": "white"}
props_temp = {"ha": "center", "va": "center", "fontsize": 32, "color": "red"}
ax.text(0, r_factor * 2.5, "1.5°C", props_temp, bbox=dict(facecolor="black"))
ax.text(0, r_factor * 3.0, "2.0°C", props_temp, bbox=dict(facecolor="black"))

# Draw month labels only once
for j in range(len(months)):
    x_unit_r, y_unit_r, angle = month_points[j]
    x_radius, y_radius = (radius * x_unit_r, radius * y_unit_r)
    angle = angle - 0.5 * np.pi
    ax.text(x_radius, y_radius, months[j], props_months, rotation=np.rad2deg(angle))

# Create a LineCollection
lc = LineCollection([], cmap=plt.get_cmap("jet"), norm=plt.Normalize(0, 3.6))
ax.add_collection(lc)

# Year text placeholder
year_text = ax.text(0, 0, "", props_year)

j = 1
# Animation function
def animate(i):
    # max_data_points = len(x_vals)  # Get the number of data points
    # if i > max_data_points:  # Ensure we don't exceed the available data points
    #     i = max_data_points

    # Update LineCollection
    
    # if i >= 176:
    #     i = j + 1 
    #     j += 1
    print("i = ", i)
    if i > 1:
        pts = np.array([x_vals[:i], y_vals[:i]]).T.reshape(-1, 1, 2)
        segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
        lc.set_segments(segs)
        lc.set_array(np.asarray(x_orig[:i]))  # Update color array

    # Update year text
    year = 1850 + (i //12)  # Calculate the year based on index
    year_text.set_text(str(year))  # Update the text


# Create the animation
anim = FuncAnimation(
    fig, animate, frames=len(x_orig), interval=0.5, repeat=False
)  # Reduced interval for faster animation

# Show the animation
plt.show()

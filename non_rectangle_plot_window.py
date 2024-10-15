from PyQt5 import QtWidgets
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib.collections import LineCollection
from matplotlib import cm


class nonRectanglePlotWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Climate Spiral")
        self.setGeometry(200, 200, 1000, 800)

        self.figure, self.ax = plt.subplots(
            subplot_kw={"projection": "polar"}, figsize=(14, 14), facecolor="#22283e"
        )

        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.draw_plot()

    def draw_plot(self):
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

        df = pd.read_csv(
            "dataset\HadCRUT.5.0.2.0.analysis.summary_series.global.monthly.csv"
        )
        df["Time"] = pd.to_datetime(df["Time"])

        r_factor = 7.0 / 3.6  # scaling factor
        anomalies = df["Anomaly (deg C)"].to_numpy() + 1.5  # offset + 1.5

        # calc angles of months
        num_months = len(months)
        theta_vals = np.linspace(0, 2 * np.pi, num_months, endpoint=False)

        r_vals = []
        theta_plot_vals = []

        for i in range(len(anomalies)):
            # radius based on temperature anomaly
            r_pos = anomalies[i] * r_factor
            # angle of the month
            theta_pos = theta_vals[month_idx[i % 12]]
            r_vals.append(r_pos)
            theta_plot_vals.append(theta_pos)

        self.ax.set_facecolor("#2D324D")
        self.ax.set_ylim(0, r_factor * 3.6)
        self.ax.set_theta_direction(-1)  # clockwise
        self.ax.set_theta_offset(np.pi / 2.0)
        self.ax.tick_params(colors="white")
        self.ax.grid(True, color="white", linestyle="--")
        self.ax.spines["polar"].set_color("white")

        # self.ax.text(np.pi/2, r_factor * 2.5, "1.5°C", ha="center", va="center", fontsize=16, color="yellow")
        # self.ax.text(np.pi/2, r_factor * 3.0, "2.0°C", ha="center", va="center", fontsize=16, color="yellow")
        self.ax.plot([0], [0], marker="o", color="yellow")

        # write months names
        for i, month in enumerate(months):
            self.ax.text(
                theta_vals[i],
                r_factor * 4.3,
                month,
                ha="center",
                va="center",
                fontsize=16,
                color="white",
            )

        # create LineCollection
        lc = LineCollection(
            [],
            cmap=cm.get_cmap("jet"),
            norm=plt.Normalize(min(anomalies), max(anomalies)),
        )
        self.ax.add_collection(lc)

        # year text placeholder
        year_text = self.ax.text(
            0.5,
            0.5,
            "",
            ha="center",
            va="center",
            fontsize=36,
            color="white",
            transform=self.ax.transAxes,
        )

        def animate(i):
            if i > 1:  # min 2 points to draw line
                pts = np.array([theta_plot_vals[:i], r_vals[:i]]).T.reshape(-1, 1, 2)
                segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
                lc.set_segments(segs)
                lc.set_array(
                    np.array(anomalies[:i])
                )  # color based on temperature anomaly

            year = 1850 + (i // 12)
            year_text.set_text(str(year))

        self.anim = FuncAnimation(
            self.figure, animate, frames=len(anomalies), interval=0.5, repeat=False
        )
        self.canvas.draw()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    ui = nonRectanglePlotWindow()
    ui.show()
    app.exec_()

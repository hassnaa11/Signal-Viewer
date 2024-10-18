from PyQt5 import QtWidgets, QtCore, QtGui
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
from matplotlib import cm
from matplotlib.colors import Normalize


class nonRectanglePlotWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Climate Anomalies")
        self.setGeometry(300, 100, 1150, 800)

        self.main_layout = QtWidgets.QVBoxLayout()
        header_widget = QtWidgets.QWidget()
        header_layout = QtWidgets.QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 30, 0) 
        header_widget.setStyleSheet("background-color: #2D324D; border-radius:15px;") 
        self.label = QtWidgets.QLabel("Global Temperature Change (1850 - 2024)")
        self.label.setStyleSheet("color: white; font-size: 30px;padding: 15px;")

        self.play_button = QtWidgets.QPushButton()
        self.play_button.setStyleSheet(
            "background-color: rgb(120, 207, 233); border-radius: 20; width: 40px; height: 40px;"
        )
        self.play_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.rewind_button = QtWidgets.QPushButton()
        self.rewind_button.setStyleSheet(
            "background-color: rgb(120, 207, 233); border-radius: 20px; width: 40px; height: 40px;"
        )
        self.rewind_button.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.play_button.setIcon(QtGui.QIcon("images\icons8-play-32.png"))
        self.play_button.setIconSize(QtCore.QSize(35, 35))
        self.rewind_button.setIcon(QtGui.QIcon("images\icons8-rewind-64.png"))
        self.rewind_button.setIconSize(QtCore.QSize(30, 30))

        header_layout.addWidget(self.label)
        header_layout.addStretch()
        header_layout.addWidget(self.play_button)
        header_layout.addWidget(self.rewind_button)

        self.main_layout.addWidget(header_widget)

        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(self.main_layout)
        central_widget.setStyleSheet("background-color: #22283e;")
        self.setCentralWidget(central_widget)

        self.counter = 0
        self.current_frame = 0
        self.is_paused = False
        self.is_rewind = False
        self.play_button.clicked.connect(self.pause_resume)
        self.rewind_button.clicked.connect(self.rewind)
        self.draw_plot()

    def draw_plot(self):
        self.figure, self.ax = plt.subplots(
            subplot_kw={"projection": "polar"}, figsize=(14, 14), facecolor="#22283e"
        )
        self.canvas = FigureCanvas(self.figure)
        self.main_layout.addWidget(self.canvas)
        
        months = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]

        df = pd.read_csv(
            "dataset\HadCRUT.5.0.2.0.analysis.summary_series.global.monthly.csv"
        )
        self.anomaly_values = df["Anomaly (deg C)"] + 1.5
        months_degrees = np.linspace(0, 2 * np.pi, 12, endpoint=False)
        theta_values = np.tile(months_degrees, 175)

        self.ax.set_facecolor("#2D324D")
        self.ax.set_ylim(0, 3)
        self.ax.set_theta_direction(-1)
        self.ax.set_theta_offset(np.pi / 2.0)
        self.ax.tick_params(colors="white")
        self.ax.grid(True, color="white", linestyle="--")
        self.ax.spines["polar"].set_color("white")

        # write months names
        for i, month in enumerate(months):
            self.ax.text(
                months_degrees[i],
                3.6,
                month,
                ha="center",
                va="center",
                fontsize=16,
                color="white",
            )

        # year number placeholder
        year_number = self.ax.text(
            0.5,
            0.5,
            "",
            ha="center",
            va="center",
            fontsize=34,
            color="white",
            transform=self.ax.transAxes,
        )
        norm = Normalize(vmin=min(self.anomaly_values), vmax=max(self.anomaly_values))
        cmap = cm.jet

        def animate(i):
            if not self.is_paused:
                if i > 1:
                    color = cmap(norm(self.anomaly_values[i]))
                    self.ax.plot(
                        theta_values[self.counter : i],
                        self.anomaly_values[self.counter : i],
                        color=color,
                    )
                    self.counter += 1
                    print(self.counter)

                year = 1850 + (i // 12)
                year_number.set_text(str(year))

        self.anim = FuncAnimation(
            self.figure, animate, frames=len(self.anomaly_values), interval=0.1, repeat=False
        )
        self.canvas.draw()
        
    def pause_resume(self):
        if self.counter >= 2094:
            return
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.play_button.setIcon(QtGui.QIcon("images\icons8-pause-90.png"))
            self.anim.event_source.stop()
        else:
            self.play_button.setIcon(QtGui.QIcon("images\icons8-play-32.png"))
            self.anim.event_source.start()
            
        
    def rewind(self):
        self.is_paused = False 
        self.play_button.setIcon(QtGui.QIcon("images\icons8-play-32.png"))
        if self.counter < 2094:
            self.anim.event_source.stop()
        self.counter = 0    
        
        self.figure.clear()
        self.figure = None
        self.canvas.deleteLater()
        self.ax.cla() 
        self.ax = None 
        
        self.draw_plot()



if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    ui = nonRectanglePlotWindow()
    ui.show()
    app.exec_()

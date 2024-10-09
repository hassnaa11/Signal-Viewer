import sys
import numpy as np
import pyqtgraph as pg
from PyQt5 import QtWidgets, QtCore

class CineModeApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Signal Viewer with Cine Mode")

        # Central widget and layout
        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)
        layout = QtWidgets.QVBoxLayout(self.centralwidget)

        # Create a PlotWidget for the graph
        self.graphWidget = pg.PlotWidget()
        layout.addWidget(self.graphWidget)

        # Initial plot data (Example: sine wave signal)
        self.x = np.linspace(0, 10, 1000)  # Time values
        self.signal = np.sin(self.x)  # Example signal (sine wave)
        self.plot_data = self.graphWidget.plot(self.x, self.signal[:1])  # Start with the first point only

        # Timer for updating the graph (simulates "cine mode")
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_cine_mode)
        self.timer.start(50)  # Update every 50 ms (~20 fps)

        # Cine mode variables
        self.current_index = 0  # Start from 0
        self.frame_length = 1   # Start with 1 data point

    def update_cine_mode(self):
        # Update the visible frame of the signal (starting from 0 and increasing)
        self.frame_length += 1  # Gradually increase the number of points to display
        self.plot_data.setData(self.x[:self.frame_length], self.signal[:self.frame_length])

        # Stop when the entire signal is displayed
        if self.frame_length >= len(self.x):
            self.timer.stop()  # Stop the timer when the full signal is displayed

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = CineModeApp()
    window.show()
    sys.exit(app.exec_())

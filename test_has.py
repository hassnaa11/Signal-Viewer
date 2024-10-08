import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
import pyqtgraph as pg
import numpy as np

class MyApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zoomable Graph with Timer")

        # Central widget and layout
        self.centralwidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralwidget)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.centralwidget)

        # Create graph widget and layout
        self.graph1Widget = QtWidgets.QWidget(self.centralwidget)
        self.graph1Widget.grid_graph_3 = QtWidgets.QGridLayout(self.graph1Widget)
        self.horizontalLayout_2.addWidget(self.graph1Widget)

        # Initialize PlotWidget from pyqtgraph
        self.graph1Widget.graph = pg.PlotWidget(self.graph1Widget)
        self.graph1Widget.graph.setBackground('#2D324D')
        self.graph1Widget.graph.setMouseEnabled(x=True, y=True)
        self.graph1Widget.grid_graph_3.addWidget(self.graph1Widget.graph, 0, 0, 1, 1)

        # Data for the plot (example)
        self.x = np.linspace(0, 10, 100)
        self.y = np.sin(self.x)

        # Plot the initial data
        self.plot_data = self.graph1Widget.graph.plot(self.x, self.y)

        # Setup a QTimer to update the plot periodically
        self.graph1Widget.timer = QTimer()
        self.graph1Widget.timer.timeout.connect(self.update_plot)
        self.graph1Widget.timer.start(1000)  # Update every second

    def update_plot(self):
        # Update the y-data for example (simulating a signal update)
        self.y = np.sin(self.x + np.random.rand())
        self.plot_data.setData(self.x, self.y)  # Update the plot with new data

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())

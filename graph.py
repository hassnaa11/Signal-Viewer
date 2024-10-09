import pyqtgraph as pg
import numpy as np
from PyQt5 import QtCore
class Graph:
    def __init__(self, graph_widget):
        self.plot_widget = graph_widget
        self.plot_widget.setBackground('#2D324D')
        self.plot_widget.getAxis('left').setPen('w')
        self.plot_widget.getAxis('bottom').setPen('w')
        self.zero_line = pg.InfiniteLine(angle=0, pos=0, pen=pg.mkPen('r', width=1, style=pg.QtCore.Qt.DashLine))
        self.plot_widget.addItem(self.zero_line)

    def update_graph(self, data, current_index, window_width,graph1_color):
        self.plot_widget.clear()
        self.plot_widget.addItem(self.zero_line)

        if data is not None:
            x_data = np.arange(current_index, current_index + len(data)) * 0.001
            self.plot_widget.plot(x_data, data, pen=pg.mkPen(graph1_color))
            self.plot_widget.setXRange(current_index * 0.001, (current_index + window_width) * 0.001)



    # def update_graph(self, data, current_index, window_width):
    #     self.plot_widget.clear()  # Clear previous plot
    #     self.plot_widget.addItem(self.zero_line)  # Re-add the zero line to the updated graph

    #     if data is not None:
    #         # Generate x-axis data
    #         x_data = np.arange(0, window_width) * 0.001
    #         self.plot_widget.plot(x_data, data, pen=pg.mkPen('w'))
            # self.plot_widget.setXRange(current_index * 0.001, ( current_index + window_width) * 0.001, padding = 0)
            # x_data = range(current_index  - window_width, current_index )
            # self.plot_widget.plot(x_data, data, pen=pg.mkPen('w'))  # Plot data
            

>>>>>>> 9aea7bf3d5b723442d19f9d12ab752ec94e3fcda

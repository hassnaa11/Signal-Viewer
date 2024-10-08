import pyqtgraph as pg
from PyQt5 import QtCore

class Graph:
    def __init__(self, graph1Widget, graph2Widget):
        # Set up the plot widget for graph 1 and graph 2
        self.plot_widget_1 = graph1Widget.graph
        self.plot_widget_2 = graph2Widget.graph_2
        self.color_1 = 'w'  # Default color for graph 1
        self.color_2 = 'w'  # Default color for graph 2
        self.last_data = None  # Store last data for redraw

        # Configure plot background and axis colors
        for plot_widget in [self.plot_widget_1, self.plot_widget_2]:
            plot_widget.getAxis('left').setPen('w')  # White y-axis
            plot_widget.getAxis('bottom').setPen('w')  # White x-axis

    def update_graph(self, data, current_index, window_width,graph1_color):
        """Update the graphs with new data."""
        self.last_data = data  # Store the current data for potential redraw
        # Clear previous plot for both plot widgets
        self.plot_widget_1.clear()  # Clear previous items for graph 1
        self.plot_widget_2.clear()  # Clear previous items for graph 2

        if data is not None:
            # Generate x-axis data
            x_data = range(current_index, current_index + window_width)

            # Plot data on both plot widgets using the current colors
            self.plot_widget_1.plot(x_data, data, pen=pg.mkPen(graph1_color))
            self.plot_widget_2.plot(x_data, data, pen=None,symbolBrush=pg.mkBrush(self.color_1), width=2,symbol='o', 
                                          symbolSize=5)



           

    
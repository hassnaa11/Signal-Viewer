import pyqtgraph as pg

class Graph:
    def __init__(self, graph1Widget, graph2Widget):
        # Set up the plot widget for graph 1 and graph 2
        self.plot_widget_1 = graph1Widget.graph
        self.plot_widget_2 = graph2Widget.graph_2
        
        # Configure plot background and axis colors
        for plot_widget in [self.plot_widget_1, self.plot_widget_2]:
            #plot_widget.setBackground('k')  # Black background
            plot_widget.getAxis('left').setPen('w')  # White y-axis
            plot_widget.getAxis('bottom').setPen('w')  # White x-axis
        
    def update_graph(self, data, current_index, window_width):
        # Clear previous plot for both plot widgets
        self.plot_widget_1.plotItem.clear()
        self.plot_widget_2.plotItem.clear()
        
        if data is not None:
            # Generate x-axis data and plot for both widgets
            x_data = range(current_index, current_index + window_width)
            
            # Plot data on both plot widgets
            self.plot_widget_1.plotItem.plot(x_data, data, pen=pg.mkPen('w'))
            self.plot_widget_2.plotItem.plot(x_data, data, pen=pg.mkPen('w'))

import pyqtgraph as pg
import numpy as np
class Graph:
    previous_signal_points = []  # To store x values
    previous_x_data = []  # To store y values
    def __init__(self, graph_widget):
        self.plot_widget = graph_widget
        self.plot_widget.setBackground('#2D324D')
        self.plot_widget.getAxis('left').setPen('w')
        self.plot_widget.getAxis('bottom').setPen('w')
        self.zero_line = pg.InfiniteLine(angle=0, pos=0, pen=pg.mkPen('r', width=1, style=pg.QtCore.Qt.DashLine))
        self.plot_widget.addItem(self.zero_line)
        
       

    def update_graph(self, data, current_index, window_width, graph1_color):
        if data is not None:
            # Create x-axis data for plotting based on current_index
            x_data = np.arange(current_index, current_index + len(data)) * 0.001  # 0.001 assumes 1 unit is 1 ms
            self.previous_signal_points.extend(data)
            self.previous_x_data.extend(x_data)
            
            # Clear the previous plot before replotting the entire signal with the new color
            
            # Replot the entire signal with the updated color
            self.plot_widget.plot(x_data, data, pen=pg.mkPen(graph1_color))
            print(f"Previous signal points: {self.previous_signal_points[:3]}")  # Print first 10 points
            print(f"Previous x data: {self.previous_x_data[:3]}") 

            
            # Handle the x-axis range for scrolling
            if current_index < 50:
                # Initially, plot and fix the x-axis range to show the data from 0 to window_width
                print("Less than window width, no scrolling", current_index)
                self.plot_widget.setXRange(0, window_width * 0.001)  # window_width in ms
            else:
                # After filling the initial window, make the graph scroll by updating the x-axis range
                print("Window filled, scrolling", current_index)
                self.plot_widget.setXRange((current_index - window_width) * 0.001, current_index * 0.001)

import sys
import numpy as np
import pandas as pd
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QPushButton, QFileDialog, QWidget, QGridLayout
from PyQt5.QtCore import QTimer
from scipy.interpolate import make_interp_spline

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # Set up UI components
        self.graph1Widget_3 = QWidget()
        self.graph1Widget_3.num = 0
        
        # Create the PlotWidget
        self.graph1Widget_3.graph = pg.PlotWidget(self.graph1Widget_3)
        self.graph1Widget_3.grid_graph_3 = QGridLayout()
        self.graph1Widget_3.timer = QTimer()
        
        # Set layout and add graph to it
        self.graph1Widget_3.setLayout(self.graph1Widget_3.grid_graph_3)
        self.graph1Widget_3.grid_graph_3.addWidget(self.graph1Widget_3.graph, 0, 0, 1, 1)
        
        # Create Open Button
        self.open_button = QPushButton('Open CSV File')
        self.open_button.clicked.connect(self.open_file)
        self.graph1Widget_3.grid_graph_3.addWidget(self.open_button, 1, 0)
        
        # Timer to update the graph
        self.graph1Widget_3.timer.timeout.connect(self.update)
        
        # Layout for main widget
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.graph1Widget_3)
        self.setLayout(main_layout)
        
        # Data storage
        self.data = None
        self.current_index = 0
        self.window_width = 500  # Number of points to show in the window at a time

        # Add a horizontal line at y=0
        self.zero_line = pg.InfiniteLine(angle=0, pos=0, pen=pg.mkPen('r', width=1, style=pg.QtCore.Qt.DashLine))
        self.graph1Widget_3.graph.addItem(self.zero_line)

        # Add a PlotDataItem for smoother updates
        self.plot_data_item = pg.PlotDataItem(pen=pg.mkPen('w', width=2))
        self.graph1Widget_3.graph.addItem(self.plot_data_item)

    def open_file(self):
        # Open file dialog to select CSV file
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv)", options=options)
        if file_path:
            # Read CSV file into a DataFrame
            df = pd.read_csv(file_path)
            # Assuming the CSV has one column of data; adjust as necessary
            self.data = df.values.flatten()
            self.current_index = 0
            # Start the timer for real-time update
            self.graph1Widget_3.timer.start(500)  # Update interval in ms

    def update(self):
        # Clear previous plot if no data
        if self.data is None:
            return
        
        # Check if we have data to plot
        if self.current_index < len(self.data):
            # Define x values starting from 0.001
            x_data = np.linspace(0.001, 0.001 * (self.current_index + 1), self.current_index + 1)
            y_data = self.data[:self.current_index + 1]  # Include the current index data

            # Create a smooth curve using interpolation
            if len(x_data) > 3:  # Ensure enough points for smoothing
                # Generate smooth x values
                x_smooth = np.linspace(x_data[0], x_data[-1], 300)
                # Interpolate to get smooth y values
                spline = make_interp_spline(x_data, y_data, k=3)  # Cubic spline
                y_smooth = spline(x_smooth)
                
                # Update the plot with the smooth data
                self.plot_data_item.setData(x_smooth, y_smooth)
            else:
                # Update plot directly if not enough points
                self.plot_data_item.setData(x_data, y_data)

            # Adjust the x-axis range to create a scrolling effect
            if self.current_index >= self.window_width:
                self.graph1Widget_3.graph.setXRange(x_data[self.current_index - self.window_width + 1], x_data[self.current_index])

            # Move to the next index
            self.current_index += 1
        else:
            # Stop the timer if all data has been plotted
            self.graph1Widget_3.timer.stop()

# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWidget()
    window.setWindowTitle("CSV Signal Viewer")
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())

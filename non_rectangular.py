import sys
import numpy as np
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
import pyqtgraph as pg
import pandas as pd

class BubbleChartApp:
    def __init__(self, graph_widget):
        # Set up the plot widget
        self.plot_widget = graph_widget
        self.plot_widget.setBackground('#2D324D')
        self.plot_widget.getAxis('left').setPen('w')  # Set axis pen color to white
        self.plot_widget.getAxis('bottom').setPen('w')  # Set axis pen color to white

        # Add a zero line to the chart
     

        # Set chart title and axes labels
        self.plot_widget.setTitle("Bubble Chart")
        self.plot_widget.setLabel('bottom', 'Years')
        self.plot_widget.setLabel('left', 'Sales')

        # Empty data placeholders
        self.x = None
        self.y = None
        self.sizes = None
        self.current_index = 0
        self.total_length = 0

        # Set up the scatter plot (bubble chart)
        self.bubble_plot = self.plot_widget.plot([], [], symbol='o', pen=None, symbolSize=10, symbolBrush=(120, 207, 233))

    def open_file(self, parent_widget):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(parent_widget, "Open CSV File", "", "CSV Files (*.csv)", options=options)
    
        if file_path:
            # Read CSV into pandas dataframe
            df = pd.read_csv(file_path)

            # Check the first few rows of the file (for debugging)
            print(df.head())

            # Assuming the first column is year, second is sales, and third is bubble size
            self.x = df.iloc[:, 0].to_numpy()  # Year data
            self.y = df.iloc[:, 1].to_numpy()  # Sales data
            self.sizes = np.array(df.iloc[:, 2].to_numpy() * 100)  # Bubble size, scaled

            # Set the total length of the data
            self.total_length = len(self.x)

            # Reset current index for animation
            self.current_index = 0

            # Reset the graph
            self.bubble_plot.clear()

    def update_graph(self):
        """Update the bubble chart in cine mode"""
        if self.current_index < self.total_length:
            # Get the current data for cine mode
            x_data = self.x[:self.current_index + 1]
            y_data = self.y[:self.current_index + 1]
            size_data = self.sizes[:self.current_index + 1]
            bubble_sizes = np.sqrt(size_data) * 3  # Scaling to prevent large bubbles

            # Update the bubble plot data
            self.bubble_plot.setData(x_data, y_data,  symbol='o', symbolSize=bubble_sizes, symbolBrush=(120, 207, 233))

            # Increment the current index to animate the data
            self.current_index += 1

    def closeEvent(self, event):
        """Stop the timer when closing the application"""
        event.accept()
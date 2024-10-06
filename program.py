from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
from PyQt5 import QtCore
import json
import numpy as np
from datetime import datetime
from main_gui import Ui_MainWindow

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTimer  # For QTimer
from PyQt5.QtWidgets import QGridLayout  # For QGridLayout

import matplotlib
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as Navi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from signal_1 import SignalProcessor
from graph import Graph
#import pyedflib
import pyqtgraph as pg


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.online_connected = False
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.timer = QtCore.QTimer()
        self.ui.graph1Widget.graph.setLimits(xMin=0)
        self.signal_processor = SignalProcessor()
        self.graph_1 = Graph(self.ui.graph1Widget, self.ui.graph2Widget)
        self.graph_2 = Graph(self.ui.graph1Widget, self.ui.graph2Widget)
        
        # Connect the button to open_file function
        self.ui.open_button_graph_1.clicked.connect(self.open_file)
        self.ui.open_button_graph_2.clicked.connect(self.open_file)
        
        # Set up the timer for updating the graph
        #self.timer.timeout.connect(self.update_graph)
        
        self.window_width = 100 
        self.plot_curve = self.ui.graph1Widget.graph.plotItem.plot(
            pen=pg.mkPen(color="orange", width=2), symbol="o"
        )
        self.ui.connect_online_button_graph_1.clicked.connect(self.update_online_plot)
        self.ui.connect_online_button_graph_2.clicked.connect(self.update_online_plot)
        self.ui.play_button_graph_1.clicked.connect(self.stop_run_graph_1)
        self.timer.start(1000)


    def format_time_string(self, time_str):
        parts = time_str.split(":")
        if len(parts) == 3:
            hour, minute, second = parts
            return f"{hour.zfill(2)}:{minute.zfill(2)}:{second.zfill(2)}"
        return time_str


    def update_online_plot(self):
        if(self.online_connected == False):
            self.timer.timeout.connect(self.update_online_plot)
            self.online_connected = True
            
        try:
            # Read and process the JSON data
            with open("online_data.json", "r") as file:
                self.data = json.load(file)
            # Convert y-axis data to floats
            y_axis = []
            for item in self.data["Data_Y"]:
                try:
                    item = float(item.replace(",", ""))
                except ValueError:
                    item = np.nan
                y_axis.append(item)
            # Convert time strings to elapsed seconds with standardized format
            time_data = self.data["Time"]
            if len(time_data) > 0:
                time_data = [self.format_time_string(t) for t in time_data] 
                base_time = datetime.strptime(time_data[0], "%H:%M:%S")  # First timestamp as the base
                x_axis = [
                    (datetime.strptime(self.format_time_string(t), "%H:%M:%S") - base_time).total_seconds()
                    for t in time_data
                ]
            else:
                x_axis = []
                
            y_axis = np.array(y_axis, dtype=np.float64)
            x_axis = np.array(x_axis, dtype=np.float64)

            valid_indices = np.isfinite(y_axis) & np.isfinite(x_axis)
            x_axis = x_axis[valid_indices]
            y_axis = y_axis[valid_indices]

            if len(x_axis) > 0 and len(y_axis) > 0:
                self.plot_curve.setData(x_axis, y_axis)
        except Exception as e:
            print(f"Error loading or plotting data: {e}")
    
    def stop_run_graph_1(self):
        if(self.online_connected == True):
            self.timer.timeout.disconnect(self.update_online_plot)
            self.online_connected = False
            self.ui.play_button_graph_1.setIcon(self.ui.icon1)
            
        else:    
            self.timer.timeout.connect(self.update_online_plot)
            self.online_connected = True
            self.ui.play_button_graph_1.setIcon(self.ui.icon)
    def open_file(self):
        self.signal_processor.open_file(self)
        if self.signal_processor.data is not None:
            self.timer.start(500)  # Start timer with interval in ms

    def update_graph(self):  # Ensure this method is indented correctly within the class
        data = self.signal_processor.get_next_data(self.window_width)
        if data is not None:
            # Update graph 1 with scrolling x-axis
            self.graph_1.update_graph(data, self.signal_processor.current_index, self.window_width)
            # Update graph 2 with scrolling x-axis
            self.graph_2.update_graph(data, self.signal_processor.current_index, self.window_width)
        else:
            self.timer.stop()        

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    app.setApplicationDisplayName("PyQt5 Tutorial with pyqtgraph")
    ui = MainWindow()
    ui.show()
    app.exec_()

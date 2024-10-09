from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
from PyQt5 import QtCore
import json
import numpy as np
from datetime import datetime
from main_gui import Ui_MainWindow

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QColorDialog


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
from non_rectangular import BubbleChartApp
#import pyedflib
import pyqtgraph as pg


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        
        self.ui.setupUi(self)
        self.timer = QtCore.QTimer()
        self.ui.graph1Widget.graph.setLimits(xMin=0)


        self.signal_processor_1 = SignalProcessor(self.ui.graph1Widget.graph)
        self.signal_processor_2 = SignalProcessor(self.ui.graph2Widget.graph_2)

        self.graph_1 = Graph(self.ui.graph1Widget.graph)
        self.graph_2 = Graph(self.ui.graph2Widget.graph_2)
        self.graph_3=BubbleChartApp(self.ui.graph1Widget_3.graph)
        self.graph1_color="w"
        self.graph2_color="w"
        self.signal_processor_1 = [] 
        self.signal_processor_2=[] # List to hold all signal processors
        self.graphs_1 = []  # List to hold corresponding graph widgets
        self.graphs_2=[]

        # Connect buttons to their respective functions
        self.ui.open_button_graph_1.clicked.connect(self.open_file_graph_1)
        self.ui.open_button_graph_2.clicked.connect(self.open_file_graph_2)
        self.ui.open_button_graph_3.clicked.connect(self.open_file_graph_3)
       
        self.ui.signal_color_button_graph_1.clicked.connect(lambda: self.open_color_dialog(1))
        self.ui.signal_color_button_graph_2.clicked.connect(lambda: self.open_color_dialog(2))
        self.ui.signal_name_lineEdit_graph_1.returnPressed.connect(self.update_graph_name_1)
        
        
        # Set up the timer for updating the graph
        self.timer.timeout.connect(self.update_graphs)
        self.timer.timeout.connect(self.graph_3.update_graph)
        
        self.window_width = 50
        self.graph1_on = True
        self.graph2_on = True
        self.plot_online_curve_graph1 = self.ui.graph1Widget.graph.plotItem.plot(
            pen=pg.mkPen(color="orange", width=2), symbol="o")
        self.plot_online_curve_graph2 = self.ui.graph2Widget.graph_2.plotItem.plot(
            pen=pg.mkPen(color="orange", width=2), symbol="o")
        self.ui.connect_online_button_graph_1.clicked.connect(self.update_online_plot)
        self.ui.connect_online_button_graph_2.clicked.connect(self.update_online_plot)
        self.ui.play_button_graph_1.clicked.connect(self.stop_run_graph)
        self.ui.play_button_graph_2.clicked.connect(self.stop_run_graph)
        self.timer.start(10)


    def format_time_string(self, time_str):
        parts = time_str.split(":")
        if len(parts) == 3:
            hour, minute, second = parts
            return f"{hour.zfill(2)}:{minute.zfill(2)}:{second.zfill(2)}"
        return time_str
    def closeEvent(self, event):
        """Handle window close event to stop the timer"""
        self.graph_3.closeEvent(event)


    def update_online_plot(self):
        sender_button = self.sender()
        print(sender_button)
        
        if sender_button != self.ui.connect_online_button_graph_1 and  sender_button != self.ui.connect_online_button_graph_2: # No new click
            sender_button = self.last_sender
        elif (sender_button == self.ui.connect_online_button_graph_1) and self.graph1_on: # clicked on connect_online_button_graph_1
            self.timer.timeout.connect(self.update_online_plot)
            self.last_sender = sender_button
            self.first_graph_online_connected = True
        elif (sender_button == self.ui.connect_online_button_graph_2) and self.graph1_on: # clicked on connect_online_button_graph_2
            self.timer.timeout.connect(self.update_online_plot)
            self.last_sender = sender_button 
            self.second_graph_online_connected = True      
            
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
                if self.graph1_on and self.first_graph_online_connected: self.plot_online_curve_graph1.setData(x_axis, y_axis)
                if self.graph2_on and self.second_graph_online_connected: self.plot_online_curve_graph2.setData(x_axis, y_axis) 
                else: print("hahaha no sender")       
        except Exception as e:
            print(f"Error loading or plotting data: {e}")
    
    def stop_run_graph(self):
        sender_button = self.sender()
        if sender_button == self.ui.play_button_graph_1:
            self.graph1_on = not self.graph1_on
            if self.graph1_on:
                self.ui.play_button_graph_1.setIcon(self.ui.icon)
            else:
                self.ui.play_button_graph_1.setIcon(self.ui.icon1)   
        elif sender_button == self.ui.play_button_graph_2:
            self.graph2_on = not self.graph2_on
            if self.graph2_on:
                self.ui.play_button_graph_2.setIcon(self.ui.icon)
            else:
                self.ui.play_button_graph_2.setIcon(self.ui.icon1)  

    

    def open_file_graph_1(self):
        #self.timer.start(500)
        signal_processor = SignalProcessor(self.ui.graph1Widget.graph)
        self.signal_processor_1.append(signal_processor)  # Add to the list

        # Load the file and start plotting
        signal_processor.open_file(self)

        # Associate each signal processor with its graph widget
        graph = Graph(signal_processor.plot_widget)
        self.graphs_1.append(graph)


    def open_file_graph_2(self):
        signal_processor = SignalProcessor(self.ui.graph2Widget.graph_2)
        self.signal_processor_2.append(signal_processor)  # Add to the list

        # Load the file and start plotting
        signal_processor.open_file(self)

        # Associate each signal processor with its graph widget
        graph = Graph(signal_processor.plot_widget)
        self.graphs_2.append(graph)
    def open_file_graph_3(self):
        self.graph_3.open_file(self)
        #self.timer.start(500)

    def update_graphs(self):
       
        ''' data_1 = self.signal_processor_1.get_next_data(self.window_width)
        data_2 = self.signal_processor_2.get_next_data(self.window_width)'''

        window_width = 500 # Adjust the window width as needed
        for signal_processor_2, graph in zip(self.signal_processor_2, self.graphs_2):
            data = signal_processor_2.get_next_data(self.window_width)
            if data is not None:
                graph.update_graph(data, signal_processor_2.current_index, window_width,self.graph2_color)


        for signal_processor_1, graph in zip(self.signal_processor_1, self.graphs_1):
            data = signal_processor_1.get_next_data(self.window_width)
            if data is not None:
                graph.update_graph(data, signal_processor_1.current_index, window_width,self.graph1_color)

        ''''  if data_1 is not None:
            self.graph_1.update_graph(data_1, self.signal_processor_1.current_index, self.window_width,self.graph1_color)
        if data_2 is not None:
            self.graph_2.update_graph(data_2, self.signal_processor_2.current_index, self.window_width,self.graph2_color)'''
    def open_color_dialog(self, graph_number):
    # Open a color dialog and get the selected color
        color = QColorDialog.getColor()
        
        if color.isValid():
            # Update the signal color based on the chosen color
            hex_color = color.name()  # Get color in hex format
            print(hex_color)
            self.update_signal_color(hex_color, graph_number)

    def update_signal_color(self, color, graph_number):
        # Update the color of the plotted signal for the selected graph
        print(graph_number)
        if graph_number==1 :
            self.graph1_color=color
        else :self.graph2_color=color

     
    def update_graph_name_1(self):  
        new_name = self.ui.signal_name_lineEdit_graph_1.text()
        print(new_name)
        self.ui.nameegraph1.setText(new_name)
        
        # Create the label text item
       

        
        # Get the viewBox from the PlotWidget (for scaling)
        ''' text_item = pg.TextItem(text=new_name, color='w', anchor=(0.5, 1))
        viewBox = self.graph_1.plot_widget.getViewBox()
        
        # Get the current scale (zoom level) of the viewBox
        scale_x, scale_y = viewBox.viewRange()[0][1], viewBox.viewRange()[1][1]
        
        # Calculate the font size based on the scale (zoom factor)
        # You can adjust the scaling factor for the font size as needed
        font_size = max(10, int(10 * scale_x))  # Make sure it doesn’t get too small
        
        # Set the label's font size (adjust dynamically with zoom)
        text_item.setFont(QtGui.QFont("Arial", font_size))
        
        # Get the PlotWidget's scene (this is where we can add floating items)
        scene = self.graph_1.plot_widget.scene()

        # Add the label to the scene (this keeps it floating above the plot)
        scene.addItem(text_item)
        
        # Position the label in absolute coordinates (fixed position in scene)
        text_item.setPos(700, 40)  # Adjust (x, y) for floating label position'''


                
                    

    
   
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    app.setApplicationDisplayName("PyQt5 Tutorial with pyqtgraph")
    ui = MainWindow()
    ui.show()
    app.exec_()
        



       
    
        
    
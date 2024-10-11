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
        self.timer2 = QtCore.QTimer()
        self.ui.graph1Widget.graph.setLimits(xMin=0)
        self.ui.graph2Widget.graph_2.setLimits(xMin=0)
        self.ui.graph1Widget_3.graph.setLimits(xMin=0)


        self.signal_processor_1 = SignalProcessor(self.ui.graph1Widget.graph)
        self.signal_processor_2 = SignalProcessor(self.ui.graph2Widget.graph_2)

        self.graph_1 = Graph(self.ui.graph1Widget.graph)
        self.graph_2 = Graph(self.ui.graph2Widget.graph_2)
        self.graph_3=BubbleChartApp(self.ui.graph1Widget_3.graph)
        self.graph1_color="w"
        self.graph2_color="w"
        self.signal_processor1 = [] 
        self.signal_processor2=[] # List to hold all signal processors
        self.graphs_1 = []  # List to hold corresponding graph widgets
        self.graphs_2=[]

        # Connect buttons to their respective functions
        self.ui.open_button_graph_1.clicked.connect(self.open_file_graph_1)
        self.ui.open_button_graph_2.clicked.connect(self.open_file_graph_2)
        self.ui.open_button_graph_3.clicked.connect(self.open_file_graph_3)
       
        self.ui.signal_color_button_graph_1.clicked.connect(lambda: self.open_color_dialog(1))
        self.ui.signal_color_button_graph_2.clicked.connect(lambda: self.open_color_dialog(2))
        self.ui.signal_name_lineEdit_graph_1.returnPressed.connect(self.update_graph_name_1)
        
        self.timer_graph_1 = QtCore.QTimer()
        self.timer_graph_1.start(10)
        self.timer_graph_2 = QtCore.QTimer()
        self.speed_graph_1 = 500  # Default speed in ms
        self.speed_graph_2 = 500  # Default speed in ms
        
        # Initialize speed sliders and connect them
        self.ui.speed_slider_graph_1.valueChanged.connect(self.set_speed_graph_1)
        self.ui.speed_slider_graph_2.valueChanged.connect(self.set_speed_graph_2)
        
        # Set up the timer for updating the graph
        # self.timer.timeout.connect(self.update_graphs)
        
        self.ui.link_button.clicked.connect(self.link_graphs)
        self.ui.link_play_button.clicked.connect(self.stop_run_graph)
        self.isLinked = False
        
        self.is_timer_graph1_connected = False
        self.is_timer_graph2_connected = False
        
        
        self.window_width = 100
        self.graph1_on = True
        self.graph2_on = True
        self.play_both = False
        self.is_file1_opened = False
        self.is_file2_opened = False
        self.first_graph_online_connected = False
        self.second_graph_online_connected = False
        self.plot_online_curve_graph1 = self.ui.graph1Widget.graph.plotItem.plot(
            pen=pg.mkPen(color="orange", width=2), symbol="o")
        self.plot_online_curve_graph2 = self.ui.graph2Widget.graph_2.plotItem.plot(
            pen=pg.mkPen(color="orange", width=2), symbol="o")
        self.ui.connect_online_button_graph_1.clicked.connect(self.update_online_plot)
        self.ui.connect_online_button_graph_2.clicked.connect(self.update_online_plot)
        
        self.ui.play_button_graph_1.clicked.connect(self.stop_run_graph)
        self.ui.play_button_graph_2.clicked.connect(self.stop_run_graph)
        self.timer2.start(1000)
        self.timer2.timeout.connect(self.graph_3.update_graph)
        self.timer.start(1000)
        


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
        elif (sender_button == self.ui.connect_online_button_graph_2) and self.graph2_on: # clicked on connect_online_button_graph_2
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
            
    def format_time_string(self, time_str):
        parts = time_str.split(":")
        if len(parts) == 3:
            hour, minute, second = parts
            return f"{hour.zfill(2)}:{minute.zfill(2)}:{second.zfill(2)}"
        return time_str
    
    def stop_run_graph(self):
        sender_button = self.sender()
        if sender_button == self.ui.play_button_graph_1:
            self.graph1_on = not self.graph1_on
            if self.graph1_on:
                self.timer_graph_1.timeout.connect(self.update_graph1)
                self.ui.play_button_graph_1.setIcon(self.ui.icon)
            else:
                self.timer_graph_1.timeout.disconnect(self.update_graph1)
                self.ui.play_button_graph_1.setIcon(self.ui.icon1)
        elif sender_button == self.ui.play_button_graph_2:
            self.graph2_on = not self.graph2_on
            if self.graph2_on:
                self.timer_graph_2.timeout.connect(self.update_graph2)
                self.ui.play_button_graph_2.setIcon(self.ui.icon)
            else:
                self.timer_graph_2.timeout.disconnect(self.update_graph2)
                self.ui.play_button_graph_2.setIcon(self.ui.icon1)
        
        elif sender_button == self.ui.link_play_button:
            print("heyyyy link_play_button")
            self.play_both = not self.play_both
            if self.play_both :
                print("runnnnnnnnn")
                self.timer_graph_1.timeout.connect(self.update_graph1)
                self.timer_graph_2.timeout.connect(self.update_graph2) 
                self.ui.link_play_button.setIcon(self.ui.icon)
            elif not self.play_both :
                print("stoppppppppp")
                self.timer_graph_1.timeout.disconnect(self.update_graph1)
                self.timer_graph_2.timeout.disconnect(self.update_graph2)
                print("Successfully disconnected from update_graph1.")
                self.ui.link_play_button.setIcon(self.ui.icon1)        
    
    def open_file_graph_1(self):
          #self.timer.start(500)
        signal_processor= SignalProcessor(self.ui.graph1Widget.graph)
        self.signal_processor1.append(signal_processor)  # Add to the list

        # Load the file and start plotting
        signal_processor.open_file(self)

        # Associate each signal processor with its graph widget
        graph = Graph(signal_processor.plot_widget)
        self.graphs_1.append(graph)
        if not self.is_timer_graph1_connected:
            self.timer_graph_1.timeout.connect(self.update_graph1)
            self.is_timer_graph1_connected = True
        self.timer_graph_1.setInterval(self.speed_graph_1)
        if not self.timer_graph_1.isActive():
            self.timer_graph_1.start()

    def open_file_graph_2(self):
        
        signal_processor= SignalProcessor(self.ui.graph2Widget.graph_2)
        self.signal_processor2.append(signal_processor)  # Add to the list

        # Load the file and start plotting
        signal_processor.open_file(self)

        # Associate each signal processor with its graph widget
        graph = Graph(signal_processor.plot_widget)
        self.graphs_2.append(graph)
        if not self.is_timer_graph2_connected:
            self.timer_graph_2.timeout.connect(self.update_graph2)
            self.is_timer_graph2_connected = True
        self.timer_graph_2.setInterval(self.speed_graph_2)
        if not self.timer_graph_2.isActive():
            self.timer_graph_2.start()

        
    def update_graph1(self):
        window_width = 500 # Adjust the window width as needed
        for signal_processor_1, graph in zip(self.signal_processor1, self.graphs_1):
            data = signal_processor_1.get_next_data(self.window_width)
            if data is not None:
                print("update graph 1")
                self.is_file1_opened = True
                graph.update_graph(data, signal_processor_1.current_index, window_width,self.graph1_color)

        
    def update_graph2(self): 
        window_width = 500 # Adjust the window width as needed
        for signal_processor_2, graph in zip(self.signal_processor2, self.graphs_2):
                    data = signal_processor_2.get_next_data(self.window_width)
                    if data is not None:
                        print("update graph 2")
                        self.is_file2_opened = True
                        graph.update_graph(data, signal_processor_2.current_index, window_width,self.graph2_color)

    def open_file_graph_3(self):
        if self.graph_3 is None:
            self.graph_3 = BubbleChartApp(self.graph_widget_3)
        
        # Call the open_file method to open a CSV file
        self.graph_3.open_file(self)



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
    
    def set_speed_graph_1(self, value):
        print("set speed graph 1")
        self.speed_graph_1 = value
        self.timer_graph_1.setInterval(self.speed_graph_1)
        if not self.timer_graph_1.isActive():
            self.timer_graph_1.start()
            
        if self.isLinked:   
            self.timer_graph_2.setInterval(self.speed_graph_1) 
            if not self.timer_graph_2.isActive():
                self.timer_graph_2.start()

    def set_speed_graph_2(self, value):
        print("set speed graph 2")
        self.speed_graph_2 = value
        self.timer_graph_2.setInterval(self.speed_graph_2)
        if not self.timer_graph_2.isActive():
            self.timer_graph_2.start()
            
        if self.isLinked:   
            self.timer_graph_1.setInterval(self.speed_graph_2) 
            if not self.timer_graph_1.isActive():
                self.timer_graph_1.start()


     
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
        
    def link_graphs(self):
        self.play_both = True  
        self.isLinked = not self.isLinked
        if self.isLinked :
            if self.is_file1_opened and self.is_file2_opened:
                # initially play
                if not self.graph1_on:
                    print("Connect 1111 after link ")
                    self.timer_graph_1.timeout.connect(self.update_graph1)
                if not self.graph2_on:
                    print("Connect 2222 after link ")
                    self.timer_graph_2.timeout.connect(self.update_graph2)    

                # Clear both graphs
                for graph in self.graphs_1:
                    graph.plot_widget.clear()   
                for graph in self.graphs_2:
                    graph.plot_widget.clear()    
                # start from first
                for signal_processor in self.signal_processor1:
                    signal_processor.current_index = 0
                for signal_processor in self.signal_processor2:
                    signal_processor.current_index = 0
                
                
                self.ui.link_button.setText("Un Link")
                self.ui.link_play_button.show()
                self.ui.link_rewind_button.show()
                self.ui.play_button_graph_1.hide()  
                self.ui.play_button_graph_2.hide() 
                self.ui.pause_button_graph_1.hide() 
                self.ui.pause_button_graph_2.hide() 
                self.ui.stop_button_graph_1.hide()
                self.ui.stop_button_graph_2.hide()
                self.ui.zoom_in_button_graph_1.hide()
                self.ui.zoom_in_button_graph_2.hide()
                
                self.timer_graph_1.start(self.speed_graph_1)
                self.timer_graph_2.start(self.speed_graph_1)
            else:
                self.isLinked = False    
        else:
            self.un_link_graphs()
            self.ui.link_button.setText("Link")
            self.ui.link_play_button.hide()
            self.ui.link_rewind_button.hide()
            self.ui.play_button_graph_1.show()  
            self.ui.play_button_graph_2.show() 
            self.ui.pause_button_graph_1.show() 
            self.ui.pause_button_graph_2.show() 
            self.ui.stop_button_graph_1.show()
            self.ui.stop_button_graph_2.show()
            self.ui.zoom_in_button_graph_1.show()
            self.ui.zoom_in_button_graph_2.show() 
            
            
    def un_link_graphs(self):
        print("un linkk")  
        # Return graphs to play as after start linking
        if self.graph1_on and not self.play_both:
            self.timer_graph_1.timeout.connect(self.update_graph1)
        elif not self.graph1_on and self.play_both:
            self.timer_graph_1.timeout.disconnect(self.update_graph1)
            
        if self.graph2_on and not self.play_both:
            self.timer_graph_2.timeout.connect(self.update_graph2)
        elif not self.graph2_on and self.play_both:
            self.timer_graph_2.timeout.disconnect(self.update_graph2)  
            
        self.play_both = False 
    
   
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    app.setApplicationDisplayName("PyQt5 Tutorial with pyqtgraph")
    ui = MainWindow()
    ui.show()
    app.exec_()
        



       
    
        
    
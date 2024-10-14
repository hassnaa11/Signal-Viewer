from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
from PyQt5 import QtCore
from PyQt5.QtGui import QPainter, QPixmap
from matplotlib.widgets import RectangleSelector
from scipy import interpolate 
import json
import os
import numpy as np
from datetime import datetime
from main_gui import Ui_MainWindow

from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QColorDialog
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QRubberBand, QFileDialog
from PyQt5.QtCore import QRect, QPoint, QSize, Qt
from PyQt5.QtCore import QRect, QPoint
from PyQt5.QtGui import QPixmap, QMouseEvent
from fpdf import FPDF


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
        self.images=[]


        self.signal_processor_1 = SignalProcessor(self.ui.graph1Widget.graph)
        self.signal_processor_2 = SignalProcessor(self.ui.graph2Widget.graph_2)

        self.graph_1 = Graph(self.ui.graph1Widget.graph)
        self.graph_2 = Graph(self.ui.graph2Widget.graph_2)
        #self.graph_3=BubbleChartApp(self.ui.graph1Widget_3.graph)
        self.graph1_color="w"
        self.graph2_color="w"
        self.signal_processor1 = [] 
        self.signal_processor2=[] # List to hold all signal processors
        self.graphs_1 = []  # List to hold corresponding graph widgets
        self.graphs_2=[]
        self.graph2_filtered_x = []
        self.graph2_filtered_y = []
        self.graph1_filtered_x = []
        self.graph1_filtered_y = []
        self.x_shifted=[]
        self.whole_x_data=[]
        self.whole_y_data=[]
        self.graph1_plot = None
        self.graph2_plot = None
        self.ui.slider_glue.setMinimum(-40)  # Set minimum value
        self.ui.slider_glue.setMaximum(40)    # Set maximum value
        self.ui.slider_glue.setValue(0)       # Initial slider value
        self.ui.slider_glue.setSingleStep(1)  # Increment step when slider is moved
        self.ui.slider_glue.valueChanged.connect(self.on_slider_change)
        self.total_shifed_glue_slider = 0.0
        self.graph1_end_x = None
        self.graph1_start_x=None
        self.graph1_end_y = None
        self.graph1_start_y=None  
        self.graph2_start_x = None
        self.graph2_end_x=None
        self.graph2_start_y =None
        self.graph2_end_y=None
        # Connect the slider value change to the function
        

        # Connect buttons to their respective functions
        self.ui.open_button_graph_1.clicked.connect(self.open_file_graph_1)
        self.ui.open_button_graph_2.clicked.connect(self.open_file_graph_2)
        self.ui.open_button_graph_3.clicked.connect(self.open_file_graph_3)
        
        self.ui.stop_button_graph_3.clicked.connect(lambda:self.taking_snapshot(3))
        self.ui.snapshot_button.clicked.connect(lambda:self.taking_snapshot(1))
        self.ui.snapshot_button_graph2.clicked.connect(lambda:self.taking_snapshot(2))
        self.ui.export_button.clicked.connect(self.PDF_maker)
        self.ui.select_button_graph1.clicked.connect(self.select_graph_to_cut)
        self.ui.select_button_graph2.clicked.connect(self.select_graph_to_cut_2)
        self.ui.pushButton.clicked.connect(self.on_glue_button_click)
        


       
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
        #self.timer2.timeout.connect(self.graph_3.update_graph)
        self.timer.start(1000)
        self.rect_roi = pg.RectROI([0.1, 0], [0.2, 0.2], pen='r')
        self.rect_roi.addScaleHandle([1, 0.5], [0.5, 0.5])  # Adding scale handles
        
        

        # Variable to store selected range
        self.selected_range = None


    def format_time_string(self, time_str):
        parts = time_str.split(":")
        if len(parts) == 3:
            hour, minute, second = parts
            return f"{hour.zfill(2)}:{minute.zfill(2)}:{second.zfill(2)}"
        return time_str
   


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
                print("runnnnnnnnn:   ", self.play_both)
                self.timer_graph_1.timeout.connect(self.update_graph1)
                self.timer_graph_2.timeout.connect(self.update_graph2) 
                self.ui.link_play_button.setIcon(self.ui.icon)
            elif not self.play_both :
                print("stoppppppppp:   ",self.play_both)
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
        self.isLinked = not self.isLinked
        if self.isLinked :
            if self.is_file1_opened and self.is_file2_opened:
                self.play_both = True  
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
        print(self.play_both)
        if self.play_both:
            print("play both:  ",self.play_both)
            if not self.graph1_on:
                self.timer_graph_1.timeout.disconnect(self.update_graph1)
            if not self.graph2_on:
                self.timer_graph_2.timeout.disconnect(self.update_graph2) 
        else:
            print("not play both:  ",self.play_both)
            if self.graph1_on:
                self.timer_graph_1.timeout.connect(self.update_graph1)
            if self.graph2_on:
                self.timer_graph_2.timeout.connect(self.update_graph2)                                
        self.play_both = False 
    

                
    def taking_snapshot(self, x):
        snapshot = QPixmap(self.ui.graph1Widget_3.graph.size()) if x == 3 else QPixmap(self.ui.graph1Widget.graph.size()) if x == 1 else QPixmap(self.ui.graph2Widget.graph_2.size())
        painter = QPainter(snapshot)

        # Render the appropriate graph based on x
        if x == 3:
            self.ui.graph1Widget_3.graph.render(painter)
        elif x == 1:
            self.ui.graph1Widget.graph.render(painter)
        elif x == 2:
            self.ui.graph2Widget.graph_2.render(painter)

        # End the painter session
        painter.end()

        # Save the snapshot to an image file
        index = len(self.images)  # Get the current index for the snapshot
        snapshot.save(f"graph{x}_snapshot{index}.png")
        self.images.append((x, f"graph{x}_snapshot{index}.png"))  # Save a tuple of (graph_number, file_name)
        print(f"Snapshot saved: graph{x}_snapshot{index}.png")



    def PDF_maker(self):
        # Create a PDF report using FPDF
        pdf = FPDF()
        pdf.add_page()

        # Add title to the PDF
        pdf.set_font("Arial", "B", size=16)
        pdf.cell(200, 10, txt="Signal Glue Report", ln=True, align="C")

        for i, (graph_index, snapshot_file) in enumerate(self.images):
            # Set the initial y_offset with more space between sections
            y_offset = 30 + (i * 100)  # Increase the space between sections to avoid overlap

            # Add snapshot image and center it
            pdf.image(snapshot_file, x=pdf.get_x() + 55, y=y_offset, w=100)  # Adjust x position to center

            # Define the data for the current graph based on its index
            if graph_index == 1:
                x_data, y_data = self.graph1_filtered_x, self.graph1_filtered_y
                graph_name = "Graph 1"
            elif graph_index == 2:
                x_data, y_data = self.graph2_filtered_x, self.graph2_filtered_y
                graph_name = "Graph 2"
            elif graph_index == 3:
                x_data, y_data = self.whole_x_data, self.whole_y_data  # Glued graph data
                graph_name = "Glued Graph 3"

            # Calculate statistics for the current graph data
            mean_value = np.mean(y_data)
            std_value = np.std(y_data)
            min_value = np.min(y_data)
            max_value = np.max(y_data)
            duration = x_data[-1] - x_data[0]  # Duration of the signal

            # Add table title for each graph and center it
            pdf.set_xy(10, y_offset + 40)  # Adjust y position for table to be right after the image
            pdf.set_font("Arial", "B", size=12)
            pdf.cell(0, 10, txt=f"Statistics for {graph_name}", ln=True, align="C")  # Center align

            # Set font for the table
            pdf.set_font("Arial", size=10)

            # Define the statistics data
            data = [
                ["Mean", f"{mean_value:.2f}"],
                ["Standard Deviation", f"{std_value:.2f}"],
                ["Min Value", f"{min_value:.2f}"],
                ["Max Value", f"{max_value:.2f}"],
                ["Duration", f"{duration:.2f}"]
            ]

            # Set column widths and center the table
            col_width = 80  # Increase the column width to balance the table width
            row_height = 8
            pdf.set_x((210 - (col_width * 2)) / 2)  # Center the table

            # Add table header without an extra empty cell
            headers = ["Statistic", "Value"]
            for header in headers:
                pdf.cell(col_width, row_height, header, border=1, align='C')
            pdf.ln(row_height)

            # Add the data rows to the table without an extra empty cell
            for row in data:
                pdf.set_x((210 - (col_width * 2)) / 2)  # Center each row
                for item in row:
                    pdf.cell(col_width, row_height, item, border=1, align='C')
                pdf.ln(row_height)

        # Save the PDF to a file
        pdf_path = "signal_glue_report.pdf"
        pdf.output(pdf_path)

        if os.path.exists(pdf_path):
            print(f"Report generated and saved at: {pdf_path}")
        else:
            print(f"Error: PDF report was not saved at {pdf_path}")


    def select_graph_to_cut_2(self):
        if self.is_file2_opened == True:
            self.ui.graph2Widget.graph_2.addItem(self.rect_roi)
            # When the selection is made, you can access the ROI's position and size
            self.ui.pause_button_graph_2.clicked.connect(self.on_select_2)

    def select_graph_to_cut(self):
        """Triggered when the 'Select Signal Portion' button is clicked"""
        print("Rectangle selector activated. Select a portion of the signal.")
        # You can now move or resize the rect_roi interactively to select a region
        if self.is_file1_opened == True:
            self.ui.graph1Widget.graph.addItem(self.rect_roi)
            # When the selection is made, you can access the ROI's position and size
            self.ui.pause_button_graph_1.clicked.connect(self.on_select)
            

     # Make sure NumPy is imported

    def on_select(self):
        """Handles the selection event"""
        # Get the selected rectangle's coordinates and size
        pos = self.rect_roi.pos()  # Position (top-left corner)
        size = self.rect_roi.size()  # Size of the rectangle (width, height)

        # Store the selected range (left, right, top, bottom)
        left = pos.x()  # x-axis (time/sample) start
        right = pos.x() + size[0]  # x-axis (time/sample) end
        top = pos.y()  # y-axis (amplitude) start
        bottom = pos.y() + size[1]  # y-axis (amplitude) end

        # Debug: Print the selected rectangle bounds
        print(f"Rectangle bounds - Left: {left}, Right: {right}, Top: {top}, Bottom: {bottom}")

        # 1. Slice the x-data range
        x_data = self.graph_1.previous_x_data  # Original x-data
        y_data = self.graph_1.previous_signal_points  # Original y-data

        # Find the nearest index for the 'left' and 'right' boundaries
        left_idx = 0
        right_idx = 0

        # Find the nearest index to 'left'
 
        for i, x in enumerate(x_data):
            if x >= left:  # As soon as you hit or exceed the left boundary, take the index
                left_idx = i
                break  # Exit the loop as soon as the condition is met

        # Find the nearest index to 'right'
        for i, x in enumerate(x_data):
            if x >= right:  # As soon as you hit or exceed the right boundary, take the index
                right_idx = i
                break  # Exit the loop as soon as the condition is met


        # Ensure right_idx is greater than left_idx
        right_idx = max(right_idx, left_idx + 1)

        # Slice the x and y data based on the approximated x-axis selection
        selected_x = x_data[left_idx:right_idx]
        selected_y = y_data[left_idx:right_idx]

        # Debug: Print the selected x and y data range
        print(f"Selected x data: {selected_x[:5]}")  # Print the first 5 values for verification
        print(f"Selected y data: {selected_y[:5]}")


        left_value = selected_x[0]

        filtered_selected_x = []
        filtered_selected_y = []

        for x, y in zip(selected_x, selected_y):
            if x >= left_value:  # Keep only x values greater than or equal to left_value
                filtered_selected_x.append(x)
                filtered_selected_y.append(y)

        # Debug: Print the filtered x and y data
        print(f"Filtered x values: {filtered_selected_x[:5]}")
        print(f"Filtered y values: {filtered_selected_y[:5]}")


     
        # 2. Filter y-data based on the selected y-range (top to bottom) and ensure one-to-one mapping with x
        

        # Use a dictionary to store only one y-value per x-value
        unique_data = {}



        # Iterate through both x and y data simultaneously
        for i, (x, y) in enumerate(zip(filtered_selected_x, filtered_selected_y)):
            if top <= y <= bottom:  # Filter y-values within the y-axis range
                if x not in unique_data:  # Only keep the first occurrence of x
                    unique_data[x] = y

        # Convert the dictionary back to two lists
        self.graph1_filtered_x = list(unique_data.keys())
        self.graph1_filtered_y = list(unique_data.values())

        # Debug: Print the filtered x and y data
        print(f"Filtered x values: {self.graph1_filtered_x[:5]}")
        print(f"Filtered y values: {self.graph1_filtered_y[:5]}")


        self.zero_line = pg.InfiniteLine(angle=0, pos=0, pen=pg.mkPen('r', width=1, style=pg.QtCore.Qt.DashLine))
        self.ui.graph1Widget_3.graph.addItem(self.zero_line)


        self.graph1_plot= self.ui.graph1Widget_3.graph.plot(self.graph1_filtered_x, self.graph1_filtered_y, pen=pg.mkPen('w', width=1))

       

        # Store and print the selected range for verification
        self.selected_range = (left, right, top, bottom)
        print(f"Selected range: {self.selected_range}")

    def on_select_2(self):
        pos = self.rect_roi.pos()  # Position (top-left corner)
        size = self.rect_roi.size()  # Size of the rectangle (width, height)

        # Store the selected range (left, right, top, bottom)
        left = pos.x()  # x-axis (time/sample) start
        right = pos.x() + size[0]  # x-axis (time/sample) end
        top = pos.y()  # y-axis (amplitude) start
        bottom = pos.y() + size[1]  # y-axis (amplitude) end

        # Debug: Print the selected rectangle bounds
        print(f"Rectangle bounds - Left: {left}, Right: {right}, Top: {top}, Bottom: {bottom}")

        # 1. Slice the x-data range
        x_data = self.graph_2.previous_x_data  # Original x-data
        y_data = self.graph_2.previous_signal_points  # Original y-data

        # Find the nearest index for the 'left' and 'right' boundaries
        left_idx = 0
        right_idx = 0

        # Find the nearest index to 'left'
        # Find the nearest index to 'left'
        for i, x in enumerate(x_data):
            if x >= left:  # As soon as you hit or exceed the left boundary, take the index
                left_idx = i
                break  # Exit the loop as soon as the condition is met

        # Find the nearest index to 'right'
        for i, x in enumerate(x_data):
            if x >= right:  # As soon as you hit or exceed the right boundary, take the index
                right_idx = i
                break  # Exit the loop as soon as the condition is met


        # Ensure right_idx is greater than left_idx
        right_idx = max(right_idx, left_idx + 1)

        # Slice the x and y data based on the approximated x-axis selection
        selected_x = x_data[left_idx:right_idx]
        selected_y = y_data[left_idx:right_idx]

       


        left_value = selected_x[0]

        filtered_selected_x = []
        filtered_selected_y = []

        for x, y in zip(selected_x, selected_y):
            if x >= left_value:  # Keep only x values greater than or equal to left_value
                filtered_selected_x.append(x)
                filtered_selected_y.append(y)

        # Debug: Print the filtered x and y data
        


     
        # 2. Filter y-data based on the selected y-range (top to bottom) and ensure one-to-one mapping with x
        

        # Use a dictionary to store only one y-value per x-value
        unique_data = {}



        # Iterate through both x and y data simultaneously
        for i, (x, y) in enumerate(zip(filtered_selected_x, filtered_selected_y)):
            if top <= y <= bottom:  # Filter y-values within the y-axis range
                if x not in unique_data:  # Only keep the first occurrence of x
                    unique_data[x] = y

        # Convert the dictionary back to two lists
        self.graph2_filtered_x = list(unique_data.keys())
        self.graph2_filtered_y = list(unique_data.values())

        # Debug: Print the filtered x and y data
        
        print(f"Filtered y values: {self.graph2_filtered_y[:5]}")


        self.zero_line = pg.InfiniteLine(angle=0, pos=0, pen=pg.mkPen('r', width=1, style=pg.QtCore.Qt.DashLine))
        self.ui.graph1Widget_3.graph.addItem(self.zero_line)


        self.graph2_plot=self.ui.graph1Widget_3.graph.plot(self.graph2_filtered_x, self.graph2_filtered_y, pen=pg.mkPen('w', width=1))
        

    def on_slider_change(self, value):
         # Fixed amount to shift the graph
        shift_amount = 0.01  # Fixed amount to shift the graph
        self.total_shifed_glue_slider =  value * shift_amount  # Update the total shift amount
        
        # Shift x-data by the total shift amount
        self.x_shifted = [x + self.total_shifed_glue_slider for x in self.graph1_filtered_x]
        # Clear the previous plot before re-plotting
        self.graph1_plot.clear()  # Clear the previous plot
        self.graph1_plot = self.ui.graph1Widget_3.graph.plot(self.x_shifted, self.graph1_filtered_y, pen=pg.mkPen('w', width=1))

        self.graph1_end_x = self.x_shifted[-1]
        self.graph1_start_x=self.x_shifted[0]
        self.graph1_end_y = self.graph1_filtered_y[-1]
        self.graph1_start_y=self.graph1_filtered_y[0]  
        self.graph2_start_x = self.graph2_filtered_x[0]
        self.graph2_end_x=self.graph2_filtered_x[-1]
        self.graph2_start_y = self.graph2_filtered_y[0]
        self.graph2_end_y=self.graph2_filtered_y[-1]
        
        
        

    def on_glue_button_click(self):
        # Get the interpolation method from the user (linear, cubic, etc.)
        interpolation_order=self.ui.comboBox.currentText()

        x1_end = self.graph1_end_x  
        y1_end=self.graph1_end_y
        x1_start=self.graph1_start_x
        y1_start=self.graph1_start_y
        x2_start = self.graph2_start_x
        y2_start=self.graph2_start_y 
        x2_end=self.graph2_end_x
        y2_end=self.graph2_end_y
        

        if x1_end < x2_start:  # Gap detected, interpolate
            x_new = np.linspace(x1_end, x2_start, num=100)  # Generate new x points between graph 1 and 2
            
            if interpolation_order == "linear":
                f = interpolate.interp1d([x1_end, x2_start], [y1_end, y2_start], kind='linear')
               
            elif interpolation_order == "cubic":
                f = interpolate.interp1d([x1_end, x2_start,x1_start,x2_end], [y1_end, y2_start,y1_start,y2_end], kind='cubic')
            else:
                self.status_label.setText("Invalid interpolation order")
                return
            
            y_new = f(x_new)  # Get the interpolated y values
            self.whole_x_data = list(self.graph1_filtered_x) + list(x_new) + list(self.graph2_filtered_x)
            self.whole_y_data = list(self.graph1_filtered_y) + list(y_new) + list(self.graph2_filtered_y)
            
            # Plot the interpolated signal in the third graph
            self.ui.graph1Widget_3.graph.plot(x_new, y_new, pen=pg.mkPen('w', width=1))

        else:  # Overlap detected, average points
            overlap_x = np.intersect1d(self.x_shifted, self.graph2_filtered_x)
            
            # Remove overlapping points and keep non-overlapping parts from both graphs
            graph1_non_overlap_x = [x for x in self.x_shifted if x not in overlap_x]
            graph1_non_overlap_y = [self.graph1_filtered_y[self.x_shifted.index(x)] for x in graph1_non_overlap_x]
            
            graph2_non_overlap_x = [x for x in self.graph2_filtered_x if x not in overlap_x]
            graph2_non_overlap_y = [self.graph2_filtered_y[self.graph2_filtered_x.index(x)] for x in graph2_non_overlap_x]

            # Interpolate the overlapping part
            overlap_y1 = np.interp(overlap_x, self.x_shifted, self.graph1_filtered_y)
            overlap_y2 = np.interp(overlap_x, self.graph2_filtered_x, self.graph2_filtered_y)
            averaged_y = (overlap_y1 + overlap_y2) / 2  # Calculate the average of the overlapping y values

            # Combine all x and y values into a single list
            self.whole_x_data=graph1_non_overlap_x + list(overlap_x) + graph2_non_overlap_x
           
            self.whole_y_data= graph1_non_overlap_y + list(averaged_y) + graph2_non_overlap_y

            # Sort the combined points by x to ensure smooth plotting
            self.whole_x_data, self.whole_x_data= zip(*sorted(zip(self.whole_x_data, self.whole_y_data)))

            # Clear the graph to remove any existing points
            self.ui.graph1Widget_3.graph.clear()

            # Plot the combined non-overlapping and overlapping data together
            self.ui.graph1Widget_3.graph.plot(self.whole_x_data, self.whole_y_data, pen=pg.mkPen('w', width=1))

            # Disconnect the slider signal to prevent further changes during glue operation
            self.ui.slider_glue.valueChanged.disconnect(self.on_slider_change)

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    app.setApplicationDisplayName("PyQt5 Tutorial with pyqtgraph")
    ui = MainWindow()
    ui.show()
    app.exec_()
        



       
    
        
    
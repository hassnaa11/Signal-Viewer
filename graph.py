import pyqtgraph as pg
import numpy as np
from signal_1 import SignalProcessor
from PyQt5.QtCore import QTimer
import copy
class Graph:
    previous_signal_pointss = []  # To store x values
    previous_x_dataa = []  # To store y values
    def __init__(self, graph_widget):
        self.plot_widget = graph_widget
        self.plot_widget.setBackground('#2D324D')
        self.plot_widget.getAxis('left').setPen('w')
        self.plot_widget.getAxis('bottom').setPen('w')        
        self.zero_line = pg.InfiniteLine(angle=0, pos=0, pen=pg.mkPen('r', width=1, style=pg.QtCore.Qt.DashLine))
        self.signals = {}  # Track signal plot items and their visibility status
        self.legend = self.plot_widget.addLegend()
        self.signal_processor = None
        self.second_time = False
        self.index = 1
        # self.timer = QTimer()  # Initialize a timer for the graph
        # self.timer.timeout.connect(self.update_graph)  # Connect the timer to update_graph method
        # self.timer.start(100)  # Set the interval for updates (in milliseconds)
        

    def add_signal(self, name, color):
        """Add a new signal to the graph."""
        if name not in self.signals:  # Avoid duplicate signals
            plot_item = self.plot_widget.plot([], [], pen=pg.mkPen(color), name=name)
            self.signals[name] = {
                'processor': self.signal_processor,  # Store the SignalProcessor instance
                'item': plot_item,                   # Store the plot item
                'visible': True                       # Store visibility status
            }  # Track visibility
            print(f"Signal '{name}' added to the plot.")
            # Add this signal to the legend
            self.legend.removeItem(name)  # Remove the old entry if it exists
            self.legend.addItem(plot_item, name)

        else:
            print(f"Signal '{name}' already exists in Graph.")

    def update_signal_label(self, name, color):
        #Update signal color and legend entry.
        if name in self.signals:
            self.signals[name]['item'].setPen(pg.mkPen(color))

    def toggle_signal_visibility(self, name, visible):
        #Toggle visibility of a specific signal.
        if name in self.signals:
            self.signals[name]['item'].setVisible(visible)
            self.signals[name]['visible'] = visible
        # else:
        #     print(f"Signal '{name}' not found in the graph.")

    def update_graph(self, data, current_index, window_width, graph1_color):
        
        if data is not None:
            # print("in update graph.py", current_index)

            if self.zero_line not in self.plot_widget.items():
                self.plot_widget.addItem(self.zero_line)  # Add the zero line back  
            
            # Create x-axis data for plotting based on current_index
            new_x_data = np.arange(current_index, current_index + len(data)) * 0.001 
            self.previous_signal_pointss.extend(data)
             # 0.001 assumes 1 unit is 1 ms
            previous_x_data = np.arange(0, current_index) * 0.001
            self.previous_x_dataa.extend(previous_x_data)

            for signal_name, signal_info in self.signals.items():
                if signal_info['visible']:  # Only update visible signals
                    # get current data
                    if self.second_time:
                        x_data, y_data = signal_info['item'].getData()
                        self.second_time = True
                    else:
                        self.second_time = True
                        x_data = None
                        y_data = None    
                    if x_data is None or y_data is None:
                        x_data = np.array([]) 
                        y_data = np.array([])

                    x_data = np.append(x_data, new_x_data)
                    y_data = np.append(y_data, data)

                    signal_info['item'].setData(x=previous_x_data, y=data)
                    # print ("setData   doneee")
                    # print(signal_info)
                    # print("XDATA: ",previous_x_data,"YDATA: ",data)
                    # signal_info['item'].setData(x=new_x_data, y=data)  # Keep this line to update signals
            
            if current_index < 500:
                # At begin x-axis range from 0 to window_width
                self.plot_widget.setXRange(0, window_width * 0.001)   
                self.plot_widget.setLimits(xMin=0, xMax=window_width *0.001 , yMin=min(data), yMax=max(data))              
            else:
                self.index+=1
                # After filling the initial window, make the graph scroll by updating the x-axis range
                # print("Window filled, scrolling", current_index)
                self.plot_widget.setXRange((current_index - window_width) * 0.001, current_index * 0.001)
                self.plot_widget.setLimits(xMin=0, xMax=(window_width + self.index) * 0.001, yMin=min(data), yMax=max(data))

    #this meyhod to remove the signal from the graph and used while moving the selected signal from a graph to another one so we need to remove the signal from the graph it moving from
    def remove_signal(self, name):
        if name in self.signals:
            # self.signals[name]['item'].setVisible(False)  # Optionally hide it first
            self.signals[name]['item'].scene().removeItem(self.signals[name]['item'])  # Remove from scene
            del self.signals[name]  # Remove the selected signal from the dictionary
            print(f"Signal '{name}' removed from the graph.")
        else:
            print(f"Signal '{name}' not found in the graph.")

    
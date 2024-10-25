import pyqtgraph as pg
import numpy as np

class Graph:
    previous_signal_pointss = [] 
    previous_x_dataa = []
    index = 1
    ymax = 0
    ymin = 0 
    
    def __init__(self, graph_widget):
        self.plot_widget = graph_widget
        self.plot_widget.setBackground('#2D324D')
        self.plot_widget.getAxis('left').setPen('w')
        self.plot_widget.getAxis('bottom').setPen('w')        
        self.zero_line = pg.InfiniteLine(angle=0, pos=0, pen=pg.mkPen('r', width=1, style=pg.QtCore.Qt.DashLine))
        self.signals = {} 
        self.legend = self.plot_widget.addLegend()
        self.signal_processor = None
        self.second_time = False
        


    def add_signal(self, name, color):
        if name not in self.signals: 
            plot_item = self.plot_widget.plot([], [], pen=pg.mkPen(color), name=name)
            self.signals[name] = {
                'processor': self.signal_processor,
                'item': plot_item,
                'visible': True 
            } 
            self.legend.removeItem(name) 
            self.legend.addItem(plot_item, name)


    def update_signal_label(self, name, color):
        if name in self.signals:
            self.signals[name]['item'].setPen(pg.mkPen(color))

    def toggle_signal_visibility(self, name, visible):
        if name in self.signals:
            self.signals[name]['item'].setVisible(visible)
            self.signals[name]['visible'] = visible

    def update_graph(self, data, current_index,min_index, window_width, graph1_color):
        
        if data is not None:
            if self.zero_line not in self.plot_widget.items():
                self.plot_widget.addItem(self.zero_line)   
            
            
            new_x_data = np.arange(current_index, current_index + len(data)) * 0.001
            previous_x_data = np.arange(0, current_index) * 0.001
            self.previous_signal_pointss.extend(data)
            self.previous_x_dataa.extend(previous_x_data)
            for signal_name, signal_info in self.signals.items():
                if signal_info['visible']: 
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
            
            # y range limit
            if Graph.ymax < max(data):
                Graph.ymax = max(data)
            elif Graph.ymin > min(data):
                Graph.ymin = min(data)    
            self.plot_widget.setLimits( yMin=Graph.ymin, yMax=Graph.ymax)
            
            # x range that viewed
            if min_index < 500 :
                self.plot_widget.setXRange(0, window_width * 0.001)   
            else:
                self.index += 1
                self.plot_widget.setXRange((current_index - window_width) * 0.001, current_index * 0.001)

    def remove_signal(self, name):
        if name in self.signals:
            self.signals[name]['item'].scene().removeItem(self.signals[name]['item'])
            del self.signals[name] 
    
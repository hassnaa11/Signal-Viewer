import sys
import pandas as pd
import numpy as np
import pyqtgraph as pg
from PyQt5 import QtWidgets, QtCore
from scipy.interpolate import CubicSpline

class SpiralPlot(QtWidgets.QMainWindow):
    def __init__(self, data_file):
        super().__init__()
        self.setWindowTitle("Temperature Anomaly Spiral Plot")
        
        # Set up the plot widget
        self.plot_widget = pg.PlotWidget()
        self.setCentralWidget(self.plot_widget)

        # Read data from the CSV file
        self.data = pd.read_csv(data_file)

        # Extract the year column and the anomalies for each year
        self.years = self.data['Year'].values
        self.anomalies_all_years = self.data.iloc[:, 1:13].apply(pd.to_numeric, errors='coerce').values  # Jan to Dec anomalies

        # Handle missing data by replacing NaNs with 0
        self.anomalies_all_years = np.nan_to_num(self.anomalies_all_years)

        # Initialize plot data
        self.index = 0
        self.year_index = 0  # Track which year is being plotted
        self.num_interp_points = 100  # Number of interpolated points between months

        # Timer for cine mode
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(20)  # Update every 20 ms for faster animation

        # Set up angles for months (12 months = 12 angles)
        self.angles = np.linspace(0, 2 * np.pi, 12, endpoint=False)
        
        # Initialize cumulative lists to store all x, y coordinates across years
        self.x_total = []
        self.y_total = []

    def update_plot(self):
        if self.year_index < len(self.years):
            print("update: ", self.year_index)
            # Extract anomalies for the current year
            anomalies = self.anomalies_all_years[self.year_index]

            # Increase the radius with each year (expanding spiral)
            base_radius = 100  # Adjust this to control spiral tightness
            radius = base_radius + self.year_index * 10  # Radius grows with each year
            
            # Interpolate the data to create a smooth curve for this year
            interp_angles = np.linspace(0, 2 * np.pi, len(anomalies) * self.num_interp_points)

            # Use cubic spline interpolation for smooth curves
            spline_x = CubicSpline(self.angles, anomalies * np.cos(self.angles) * radius)
            spline_y = CubicSpline(self.angles, anomalies * np.sin(self.angles) * radius)

            # Generate smooth x and y data using interpolation
            x_smooth = spline_x(interp_angles)
            y_smooth = spline_y(interp_angles)

            # Append to cumulative x and y lists for continuous plotting
            self.x_total.extend(x_smooth)
            self.y_total.extend(y_smooth)

            # Incrementally plot the points for cine mode
            if self.index < len(self.x_total):
                self.plot_widget.plot(self.x_total[:self.index], self.y_total[:self.index], pen=pg.mkPen(color='b', width=2))
                self.index += 20  # Increment by 20 points for faster drawing
            else:
                # Move to the next year once the current year's data is fully drawn
                self.year_index += 1
                self.index = 0  # Reset index for the next year's data
        else:
            # Once all years have been plotted, stop the animation
            self.timer.stop()

if __name__ == "__main__":
    data_file = r'dataset\GLB.Ts+dSST.csv'  # Change this to your CSV file path
    app = QtWidgets.QApplication(sys.argv)
    window = SpiralPlot(data_file)
    window.show()
    sys.exit(app.exec_())

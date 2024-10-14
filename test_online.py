import re  # for data cleaning
import datetime
import json
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from PyQt5 import QtCore, QtWidgets
import sys

online_data_dict = {"Data_Y": [], "Time": []}

# Define a custom QThread class for data collection
class DataCollectionThread(QtCore.QThread):
    data_fetched = QtCore.pyqtSignal(str, str)  # Signal to emit fetched data

    def __init__(self):
        super().__init__()
        self.driver = self.initialize_driver()
        self.running = True  # Control flag for the thread

    def initialize_driver(self):
        # Setup Chrome options to run in headless mode
        options = Options()
        options.add_argument("--headless")  # set headless mode
        options.add_argument("--disable-gpu")  # disable GPU acceleration
        options.add_argument("--no-sandbox")  # bypass OS security model
        options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
        options.add_argument("--window-size=1920x1080")  # window size 1920*1080
        options.add_argument("--window-position=-1920,-1080")  # change window position
        options.add_argument("--log-level=3")  # Suppress warning messages in console
        options.add_argument("start-maximized")  # Start maximized
        options.add_argument("disable-infobars")  # Disables the 'Chrome is being controlled by automated software' info bar
        options.add_argument("--disable-extensions")  # Disable extensions
        options.add_argument("--user-data-dir=/tmp/temporary-profile")  # Use a temporary profile
        options.add_experimental_option("excludeSwitches", ["enable-logging"])  # Suppress logging

        # Use Service to pass the ChromeDriver path
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(30)  # Implicit wait for data loading
        return driver

    def run(self):
        while self.running:
            self.data_update()  # Call the data update method
            self.sleep(1)  # Wait for 1 second before the next fetch

    def data_update(self):
        url = "https://theskylive.com/saturn-info"
        self.driver.get(url)

        # Find the element by CLASS_NAME
        try:
            content = self.driver.find_element(By.CLASS_NAME, "distanceKm.text-flash").text
        except Exception as e:
            print("Error in finding element:", e)
            return None, None

        # Data cleaning
        content = re.split("\n|[' ']", content)
        content = re.split(r"-|\+", content[0])
        data_y = content[0]

        time = datetime.datetime.now()
        time_reg = "{H}:{M}:{S}".format(H=time.hour, M=time.minute, S=time.second)

        if data_y and time_reg:
            online_data_dict["Data_Y"].append(data_y)
            online_data_dict["Time"].append(time_reg)
            with open("online_data.json", "w") as f:
                json.dump(online_data_dict, f)
            print(online_data_dict)
            self.data_fetched.emit(data_y, time_reg)  # Emit the fetched data
        else:
            print("Failed to fetch data.")

    def stop(self):
        self.running = False  # Set the running flag to False to stop the thread
        self.driver.quit()  # Quit the driver when stopping

# Main window class to handle the UI
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Online Data Collection")
        self.setGeometry(100, 100, 400, 250)

        # Button to start data collection
        self.start_button = QtWidgets.QPushButton("Start Data Collection", self)
        self.start_button.clicked.connect(self.start_data_collection)
        self.start_button.setGeometry(100, 50, 200, 50)

        # Button to stop data collection
        self.stop_button = QtWidgets.QPushButton("Stop Data Collection", self)
        self.stop_button.clicked.connect(self.stop_data_collection)
        self.stop_button.setGeometry(100, 120, 200, 50)

        # Text area to display fetched data
        self.data_display = QtWidgets.QTextEdit(self)
        self.data_display.setGeometry(50, 180, 300, 60)
        self.data_display.setReadOnly(True)

        # Create the data collection thread
        self.data_thread = DataCollectionThread()
        self.data_thread.data_fetched.connect(self.update_data)  # Connect signal to slot

    def start_data_collection(self):
        if not self.data_thread.isRunning():  # Ensure the thread isn't already running
            self.data_thread.start()  # Start the thread

    def stop_data_collection(self):
        if self.data_thread.isRunning():  # Check if the thread is running
            self.data_thread.stop()  # Stop the thread

    def update_data(self, data_y, timestamp):
        # Update the UI with the fetched data (run in the main thread)
        self.data_display.append(f"{timestamp} - {data_y}")

    def closeEvent(self, event):
        self.data_thread.stop()  # Stop the thread
        event.accept()  # Accept the event to close the window

# Main execution
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

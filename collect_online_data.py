import re  # for data cleaning
import datetime
import json
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from PyQt5 import QtCore

online_data_dict = {"Data_Y": [], "Time": []}

class CollectOnlineData(QtCore.QThread):
    # Signal to emit data
    data_fetched = QtCore.pyqtSignal(str, str)    
    
    def __init__(self):
        super().__init__()
        self.driver = None
        self.running = False

    def initialize_driver(self):
        options = Options()        
        options.add_argument("--headless")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")  # Disable GPU acceleration (helps on Windows)
        options.add_argument("--no-sandbox")  # Bypass OS security model
        options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
        options.add_argument("--window-size=1920x1080")  # Window size for headless mode
        options.add_argument("--window-size=1920x1080")  # window size 1920*1080
        options.add_argument("--window-position=-1920,-1080") 
        options.add_argument("--remote-debugging-port=9222")  # Avoid port conflicts
        options.add_argument("disable-infobars")  # Disable 'Chrome is being controlled' infobar
        options.add_argument("--disable-extensions")  # Disable extensions
        options.add_experimental_option("excludeSwitches", ["enable-logging"])  # Suppress logging
        
        # Use Service to pass the ChromeDriver path
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        driver.implicitly_wait(30)  # Implicit wait for data loading
        return driver


    def run(self):
        self.running = True 
        while self.running:
            try:
                if not self.driver:
                    self.driver = self.initialize_driver()
                self.data_update()
            except Exception as e:
                print(f"Error during data update: {e}")
                if self.driver:
                    try:
                        self.driver.quit()
                    except Exception as e_quit:
                        print(f"Error during driver quit: {e_quit}")
                self.driver = None
            self.sleep(1)  # Wait for 1 second

            
    def stop(self):
        self.running = False
        if self.driver:
            self.driver.quit()

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
            self.data_fetched.emit(data_y,time_reg)    
        else:
            print("Failed to fetch data.")

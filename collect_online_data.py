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
    def __init__(self):
        super().__init__()
        self.driver = None
        self.running = False

    def initialize_driver(self):
        options = Options()        
        options.add_argument("--headless")
        options.add_argument("--window-position=-1920,-1080") 
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.implicitly_wait(30)
        return driver


    def run(self):
        self.running = True 
        while self.running:
            if not self.driver:
                self.driver = self.initialize_driver()
            self.data_update()
            
    def stop(self):
        self.running = False
        online_data_dict["Data_Y"].clear()
        online_data_dict["Time"].clear()
        self.terminate()    

    def data_update(self):
        url = "https://theskylive.com/saturn-info"
        self.driver.get(url) 

        # Find the element by CLASS_NAME
        try:
            data_y = self.driver.find_element(By.CLASS_NAME, "distanceKm.text-flash").text
        except Exception as e:
            print("error find element: ", e)
            return None, None

        time = datetime.datetime.now()
        time_register = "{H}:{M}:{S}".format(H=time.hour, M=time.minute, S=time.second)

        if data_y and time_register:
            online_data_dict["Data_Y"].append(data_y)
            online_data_dict["Time"].append(time_register)
            with open("online_data.json", "w") as file:
                json.dump(online_data_dict, file)
            print(online_data_dict)
        else:
            print("failed to add data")

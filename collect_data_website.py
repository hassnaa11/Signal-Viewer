import datetime
import json
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

online_data_dict = {"Data_Y": [], "Time": []}

def initialize_driver():
    options = Options()
    options.add_argument("--headless")  
    options.add_argument("--window-position=-1920,-1080") 
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(30)
    return driver


def data_update(driver):
    url = "https://theskylive.com/saturn-info"
    driver.get(url) 

    # Find the element by CLASS_NAME
    try:
        data_y = driver.find_element(By.CLASS_NAME, "distanceKm.text-flash").text
    except Exception as e:
        print("Error in finding element:", e)
        return None, None

    time = datetime.datetime.now()
    time_reg = "{H}:{M}:{S}".format(H=time.hour, M=time.minute, S=time.second)

    return data_y, time_reg

        
if __name__ == "__main__":
    driver = initialize_driver()
    try:
        while True:
            data_y, time_reg = data_update(driver)
            if data_y and time_reg:
                online_data_dict["Data_Y"].append(data_y)
                online_data_dict["Time"].append(time_reg)
                with open("online_data.json", "w") as f:
                    json.dump(online_data_dict, f)
                print(online_data_dict)
            else:
                print("Failed to fetch data.")
    finally:
        driver.quit()
        
import re  # for data cleaning
import datetime
import json
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

online_data_dict = {"Data_Y": [], "Time": []}

def initialize_driver():
    # Setup Chrome options to run in headless mode
    options = Options()
    options.add_argument("--headless")  # set headless mode
    options.add_argument("--disable-gpu")  # disable GPU acceleration
    options.add_argument("--no-sandbox")  # bypass OS security model
    options.add_argument(
        "--disable-dev-shm-usage"
    )  # Overcome limited resource problems
    options.add_argument("--window-size=1920x1080")  # window size 1920*1080
    options.add_argument("--window-position=-1920,-1080") # change window position
    options.add_argument("--log-level=3")  # Suppress warning messages in console
    options.add_argument("start-maximized")  # Start maximized
    options.add_argument(
        "disable-infobars"
    )  # Disables the 'Chrome is being controlled by automated software' info bar
    options.add_argument("--disable-extensions")  # Disable extensions
    options.add_argument(
        "--user-data-dir=/tmp/temporary-profile"
    )  # Use a temporary profile
    options.add_experimental_option(
        "excludeSwitches", ["enable-logging"]
    )  # Suppress logging

    # Use Service to pass the ChromeDriver path
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.implicitly_wait(30)  # Implicit wait for data loading
    return driver


def data_update(driver):
    url = "https://theskylive.com/saturn-info"
    driver.get(url) 

    # Find the element by CLASS_NAME
    try:
        content = driver.find_element(By.CLASS_NAME, "distanceKm.text-flash").text
    except Exception as e:
        print("Error in finding element:", e)
        return None, None

    # Data cleaning
    content = re.split("\n|[' ']", content)
    content = re.split(r"-|\+", content[0])

    data_y = content[0]

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

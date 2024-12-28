
from xpaths import *
import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from selenium.webdriver.common.action_chains import ActionChains


def slow_type(driver, selector, text):
    WebDriverWait(driver, 40).until(
        EC.presence_of_element_located((By.XPATH, selector))
    )
    element = driver.find_element(By.XPATH, selector)
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.1, 0.3))



def create_account(driver,name):
    driver.get("https://studio.youtube.com")
    time.sleep(10)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, name_xpath))
        )
        input_element = driver.find_element(By.XPATH, name_xpath)
        input_element.clear()
        time.sleep(2)
        slow_type(driver, name_xpath, name)
    except Exception as e:
        print("Name Field not found:", e)
        return False
    time.sleep(5)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, create_channel))
        )
        driver.find_element(By.XPATH, create_channel).click()

    except Exception as e:
        print("Channel Button not found", e)
        return False
    time.sleep(5)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, continue_button_channel_creation))
        )
        driver.find_element(By.XPATH, continue_button_channel_creation).click()
        time.sleep(4)
        driver.close()
        time.sleep(3)

    except Exception as e:
        print("countine Channel Button not found", e)
        pass
    
    return True
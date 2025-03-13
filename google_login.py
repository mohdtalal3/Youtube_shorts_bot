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

def not_now(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, not_now_button_xpath))
        )
        driver.find_element(By.XPATH, not_now_button_xpath).click()
        return True
    except Exception as e:
        #print("Not now button not found:", e)
        pass
        return False
    


def slow_type(driver, selector, text):
    WebDriverWait(driver, 40).until(
        EC.presence_of_element_located((By.XPATH, selector))
    )
    element = driver.find_element(By.XPATH, selector)
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.1, 0.3))


def login_google(driver, email, password, recovery_email):
    driver.get("https://accounts.google.com/servicelogin?hl=en-gb")
    driver.maximize_window()
    time.sleep(10)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, email_input_xpath))
        )
        slow_type(driver, email_input_xpath, email)
        driver.find_element(By.XPATH, next_button_xpath).click()
        time.sleep(3)
    except Exception as e:
        print("Email login not found. Returning:", e)
        return False

    time.sleep(4)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, password_input_xpath))
        )
        slow_type(driver, password_input_xpath, password)
        driver.find_element(By.XPATH, next_button_xpath).click()
        time.sleep(3)
    except Exception as e:
        print("Password login not found. Returning:", e)
        return False

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, confirm_recovery_email_xpath))
        )
        driver.find_element(By.XPATH, confirm_recovery_email_xpath).click()
        time.sleep(5)
        slow_type(driver, email_input_xpath, recovery_email)
        driver.find_element(By.XPATH, next_button_xpath).click()
    except Exception as e:
        return True
        print("Recovery email option not found:", e)
        pass

    time.sleep(5)
    not_now(driver)
    time.sleep(5)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, cancel_button))
        )
        driver.find_element(By.XPATH,cancel_button).click()
        time.sleep(5)
    except Exception as e:
        #print("Recovery email", e)
        pass
    time.sleep(5)
    not_now(driver)
    return True
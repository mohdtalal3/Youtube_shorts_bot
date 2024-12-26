
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


def upload_on_youtube(driver,profile_data):
    driver.get("https://studio.youtube.com")
    driver.maximize_window()
    time.sleep(10)
    #continue if exists
    try:
        WebDriverWait(driver, 6).until(
            EC.presence_of_element_located((By.XPATH, continue_button_channel_creation))
        )
        driver.find_element(By.XPATH, continue_button_channel_creation).click()
        time.sleep(3)

    except Exception as e:
        pass
    #Finding Upload Button
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, upload_button))
        )
        driver.find_element(By.XPATH, upload_button).click()
        time.sleep(3)

    except Exception as e:
        print("No upload Button", e)
        return False

    # Uplaoding file
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, send_file))
        )
        file=driver.find_element(By.XPATH, send_file)
        file.send_keys(profile_data['video_path'])
        time.sleep(5)
    except Exception as e:
        print("No upload Button", e)
        return False
    
    #Adding title,description and child button 
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, add_title))
        )
        title=driver.find_elements(By.XPATH, add_title)
        title[0].click()
        time.sleep(2)
        title[0].clear()
        time.sleep(1)
        title[0].send_keys(profile_data['title'])
        time.sleep(3)

        title[1].click()
        title[1].send_keys(profile_data['description'])

        driver.find_element(By.XPATH,video_child_button).click()
        time.sleep(2)

        driver.find_element(By.XPATH,next_button_youtube).click()
        time.sleep(3)
        time.sleep(2)
    except Exception as e:
        print("First page not appear", e)
        return False
    
    #next page 
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, next_button_youtube))
        )
        driver.find_element(By.XPATH,next_button_youtube).click()
        time.sleep(5)
    except Exception as e:
        print("Second page not appears", e)
        return False
    
    # Copy right Checking 
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, next_button_youtube))
        )
        driver.find_element(By.XPATH,next_button_youtube).click()
        time.sleep(5)
    except Exception as e:
        print("Third page not appears", e)
        return False
    
    # Visibility page
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, public_button))
        )
        driver.find_element(By.XPATH,public_button).click()
        time.sleep(3)
        driver.find_element(By.XPATH,done_button_youtube).click()
        time.sleep(3)
    except Exception as e:
        print("Visibility page not appears", e)
        return False
    

    # close button 
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH,close_button))
        )
        driver.find_element(By.XPATH,close_button).click()
        time.sleep(3)
    except Exception as e:
        print("close page not appears")
        pass

    return True
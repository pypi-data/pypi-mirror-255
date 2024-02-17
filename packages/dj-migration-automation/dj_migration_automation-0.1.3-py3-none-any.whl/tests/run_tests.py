import os
from selenium import webdriver
from selenium.webdriver.common.alert import Alert
import time

# get the path of ChromeDriverServer
dir = os.path.dirname(__file__)
chrome_driver_path = os.path.join(dir, "chromedriver.exe")

# create a new Chrome session
driver = webdriver.Chrome(chrome_driver_path)
driver.implicitly_wait(30)
driver.maximize_window()

# navigate to the application home page
driver.get("localhost:10008/web/dosepacker/index.html")

# get the username textbox
search_field = driver.find_element_by_id("username")
search_field.clear()


search_field.send_keys("admin")
search_field.submit()

# get the password field
search_field = driver.find_element_by_id("password")
search_field.clear()


# enter search keyword and submit
search_field.send_keys("admin")
search_field.submit()

# get the password field
# search_field = driver.find_element_by_id("id-signin").submit()
# time.sleep(3)
Alert(driver).accept()

# close the browser window
# driver.quit()

# Python3 script to interface basic Blynk rest API with Raspberry PI
import subprocess
import time
from time import sleep
import webbrowser
import requests

import os

token="eRYh7_N8M5YA_NoPhpH2zViDQzPGr7L3"
#url = "https://blynk.cloud/external/api/logEvent?token=eRYh7_N8M5YA_NoPhpH2zViDQzPGr7L3&code=rubbish_cleared"
rubbish_cleared_url = 'https://blynk.cloud/external/api/logEvent?token=eRYh7_N8M5YA_NoPhpH2zViDQzPGr7L3&code=rubbish_cleared'
e_stop_is_pressed_url = 'https://blynk.cloud/external/api/logEvent?token=eRYh7_N8M5YA_NoPhpH2zViDQzPGr7L3&code=e_stop_is_pressed'
rubbsish_bin_full_url = 'https://blynk.cloud/external/api/logEvent?token=eRYh7_N8M5YA_NoPhpH2zViDQzPGr7L3&code=rubbsish_bin_full'
bin_unavailable_url = 'https://blynk.cloud/external/api/logEvent?token=eRYh7_N8M5YA_NoPhpH2zViDQzPGr7L3&code=bin_unavailable'

#v1 = e_device, v2 = battery, v3 = metal v4 = general waste
def writeIoT(pin,value):
	api_url = "https://blynk.cloud/external/api/update?token="+token+"&"+pin+"="+value
	response = requests.get(api_url)
	if "200" in str(response):
		print("Value successfully updated")
	else:
		print("Could not find the device token or wrong pin format")

def readIoT(pin):
	api_url = "https://blynk.cloud/external/api/get?token="+token+"&"+pin
	response = requests.get(api_url)
	return response.content.decode()

# i = 0;
# while i<12:
	# print(readIoT("v0"))
	# print("reading.")
	# sleep(2)
def writeIoT_Event(event):
	
	if event == "Reset":
		url = rubbish_cleared_url
	elif event == "E-STOP":
		url = e_stop_is_pressed_url
	elif event == "Bin_Full":
		url = rubbish_bin_full_url
	elif event == "Bin_Unavailable":
		url = bin_unavailable_url
	# Run the command using subprocess
	subprocess.Popen([
		'chromium-browser',
		url
	])

	# Wait for 5 seconds
	sleep(5)
	# Kill the oldest chromium process
	subprocess.call(['pkill', '--oldest', 'chromium'])



# import selenium.webdriver as webdriver
# from selenium.webdriver.firefox.service import Service 
# from selenium.webdriver.firefox.options import Options

# user_agent= 'Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0'
# firefox_driver = "/home/msd/geckodriver" # os.path.join(os.getcwd(),'msd','geckodriver')
# firefox_service = Service(firefox_driver)
# firefox_options = Options()
# firefox_options.set_preference('general.useragent.override',user_agent)

# browser = webdriver.Firefox(firefox_driver)
# browser.get('http://google.com')

# webbrowser.open("https://blynk.cloud/external/api/logEvent?token=eRYh7_N8M5YA_NoPhpH2zViDQzPGr7L3&code=rubbish_cleared")
# time.sleep(2)
# webbrowser.close_all()
# from selenium import webdriver
# import time

# driver=webdriver.Chromium()
# driver.get(url)
# driver.execute_script("window.open('');")
# time.sleep(10)
# driver.close()

# nohup chromium-browser 'https://blynk.cloud/external/api/logEvent?token=eRYh7_N8M5YA_NoPhpH2zViDQzPGr7L3&code=rubbish_cleared' >/dev/null 2>&1 &
# sleep (5)
# pkill --oldest chromium

#chromium-browser 'https://blynk.cloud/external/api/logEvent?token=eRYh7_N8M5YA_NoPhpH2zViDQzPGr7L3&code=rubbish_cleared'& sleep "5s"; pkill --oldest chromium



# ####THIS ONE if need to trigger the event manually!!!!!!!!!!!!!!!!!!!
# # Define the command to launch Chromium browser
# command = "chromium-browser 'https://blynk.cloud/external/api/logEvent?token=eRYh7_N8M5YA_NoPhpH2zViDQzPGr7L3&code=rubbish_cleared'"

# # Launch Chromium browser
# process = subprocess.Popen(command, shell=True)

# # Wait for a few seconds
# time.sleep(5)

# # Terminate Chromium process using pkill with the -f option
# subprocess.run(["pkill", "-f", "chromium-browser"])

# metal = 2
# Example: write the virtual PIN v1 to set it to 100:
# writeIoT(token,"v1",str(metal))
# write(token,"v2","2")
# write(token,"v3","7")
# write(token,"v4","2")
# Example: read a virtual PIN and print it on shell
# button=readIoT(token,"v4")
# print(button)



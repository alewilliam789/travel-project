from utils.s3 import upload_file
from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import logging
from zipfile import ZipFile

driver = webdriver.Chrome()
driver.get("https://data.worldbank.org/indicator/ST.INT.ARVL")

elem = driver.find_element(By.LINK_TEXT, "CSV")

elem.click()

driver.close()

try:
    os.chdir("/home/alex/Downloads")
except:
    logging.error(msg="Problem accessing Downloads folder")

files = os.listdir(os.getcwd())

zip_path = ""

for file in files:
    if("API" in file):
        zip_path = file
        break;

csv_file = ""
with ZipFile(zip_path) as my_zip:
    for file in my_zip.filelist:
        if not("Metadata" in file.filename):
            csv_file = file.filename
            my_zip.extract(member=file.filename)
            break

upload_file(csv_file,"UncleanArrival")










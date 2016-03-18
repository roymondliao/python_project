# -*- coding: utf-8 -*-
import sys
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re

def main():
    if len(sys.argv) < 2:
        print """Wrong argument! You don't enter the file path, please enter again!"""
        sys.exit()
    else:
        argument = sys.argv[1]
        return argument
def setUp():
    driver = webdriver.Firefox()
    #driver = webdriver.Chrome(os.path.join(os.getcwd(), "chromedriver.exe"))
    time.sleep(5)
    return driver


def selenium_barcode(folder_path):
    driver = setUp()
    ## navigation the url
    base_url = "https://www.barcoderobot.com/"
    driver.implicitly_wait(5) # seconds
    driver.get(base_url + "/login")
    driver.find_element_by_link_text("Sign In").click()

    ## import the account / password
    driver.implicitly_wait(5) # seconds
    driver.find_element_by_id("email").clear()
    driver.find_element_by_id("email").send_keys("<your email>")
    driver.implicitly_wait(5) # seconds
    driver.find_element_by_id("password").clear()
    driver.find_element_by_id("password").send_keys("<your password>")
    driver.find_element_by_css_selector("button.btn.btn-default").click()

    ## upload files
    time.sleep(5)
    dirs = os.listdir(folder_path)
    for files in dirs:
        upload_files = os.path.join(folder_path, files)
        ## create a new job
        driver.implicitly_wait(5) # seconds
        driver.find_element_by_link_text("Amazon").click()
        driver.find_element_by_link_text("Bulk lookups").click()
        driver.find_element_by_link_text("Add new job").click()
        driver.find_element_by_id("job_file").clear()
        driver.find_element_by_id("job_file").send_keys(upload_files)
        time.sleep(5)

        ## select the "ASIN to EAN / UPC" field
        Select(driver.find_element_by_id("kind")).select_by_visible_text("ASIN to EAN / UPC")
        driver.find_element_by_xpath("//div//button[@class = 'btn btn-primary clicky_log_bulk']").click()

        ## get the first Job name
        time.sleep(5)
        job_name = driver.find_elements_by_xpath("//tbody//tr//td//a")[0].text
        driver.find_element_by_link_text("{}".format(job_name)).click()
        driver.find_element_by_link_text("Download").click()

        ## select the fields
        time.sleep(5)
        driver.find_element_by_xpath("//div//select//option[@value = 'asin']").click()
        driver.find_element_by_xpath("//div//select//option[@value = 'parentasin']").click()
        driver.find_element_by_xpath("//div//select//option[@value = 'mpn']").click()
        driver.find_element_by_xpath("//div//select//option[@value = 'manufacturer']").click()
        driver.find_element_by_xpath("//div//select//option[@value = 'salesrank']").click()
        driver.find_element_by_xpath("//div//select//option[@value = 'title']").click()
        driver.find_element_by_xpath("//div//select//option[@value = 'brand']").click()
        driver.find_element_by_xpath("//div//select//option[@value = 'detailpageurl']").click()
        driver.find_element_by_xpath("//div//select//option[@value = 'ean_list']").click()
        driver.find_element_by_xpath("//div//select//option[@value = 'upc_list']").click()
        driver.find_element_by_xpath("//div//select//option[@value = 'totalnew']").click()
        driver.find_element_by_xpath("//div//select//option[@value = 'new_product_formatted_price']").click()
        driver.find_element_by_xpath("//div//select//option[@value = 'size']").click()
        driver.find_element_by_xpath("//div//select//option[@value = 'package_quantity']").click()

        ## download the file
        driver.find_element_by_xpath("//div//button[@class ='btn btn-primary clicky_log_bulk']").click()
        print "Doing {} to upload.".format(files)

    return driver

def shutdown(driver):
    driver.close()

if __name__=="__main__":
    folder_path = main()
    driver = selenium_barcode(folder_path)
    shutdown(driver)



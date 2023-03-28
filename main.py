import pandas
#import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from os import path as pth
import pandas as pd
import time


limiter = False
global counter

# os.system('pip install pandas')

# os.system('pip install selenium')

# settings #

company_flag = True

custom_limit = 2

word_pages = 10

wait_timeout = 30


# get list of the pages to scrap
def get_addresslist():
    # Load the data #


    input_file = pandas.read_excel('input.xlsx')
    # replaces line breaks with spaces
    input_file = input_file.replace(r'\n', ' ', regex=True)

    input_file.to_excel('input_mod.xlsx')

    try:

        try:
            input_file['address'] = input_file['company'] + ";" + input_file["address"]
        except:
            # In case of wrong spelling od address by the Germans #
            input_file['address'] = input_file['company'] + ";" + input_file["adress"]
    except:
        print("No company names provided. Accuracy of the search will be diminished. Use double column input with 'company' and 'address' fields for best results")
        global company_flag
        company_flag=False
    return (input_file['address'])


def get_address_text(address,cf=company_flag):
    print(f'trying address {address}')
    driver.get(url)

    wait.until(EC.visibility_of_element_located((By.ID, searchbox_ID))).send_keys(address)
    #time.sleep(2)
    driver.find_element(By.ID, searchbutton_ID).click()
    #time.sleep(2)

    # This line is different depending on whether we use company name or not. Why? Go ask Google"

    # It searches the element of the page source code based on id or xpath.
    # If the data contain company names it tries for the component most likely to be found
    # If there are no company names it searches for the components with different id and xpaths
    # If it does not find anything it searches the other one just to be sure

    if cf==False:
        try:
            txt_ = wait.until(EC.visibility_of_element_located((By.XPATH, copybutton_xpath))).get_attribute('aria-label')
        except:
            txt_ = wait.until(EC.visibility_of_element_located((By.XPATH, copybutton_xpath_alt))).get_attribute('aria-label')
            txt_ = txt_.replace("Address:", "Address,")
    else:
        try:
            txt_ = wait.until(EC.visibility_of_element_located((By.XPATH, copybutton_xpath_alt))).get_attribute(
                'aria-label')
            txt_ = txt_.replace("Address:", "Address,")
        except:
            txt_ = wait.until(EC.visibility_of_element_located((By.XPATH, copybutton_xpath))).get_attribute('aria-label')
    return txt_


def convert_string_to_df(adr,txt):
    try:
        #print(f'Txt is {txt}')
        # split the string into list on comma
        txt_list=txt.split(',')
        # remove first element which is "Address,"
        txt_list=txt_list[1:]
        txt_list=[txt_.lstrip() for txt_ in txt_list]

        # find space in first element of the list to separate street and street number
        street_space=txt_list[0].rfind(" ")
        # find space in the second element of the list to separate postal number and city
        city_space=txt_list[1].find(" ")
        # separate list elements on found positions to receive address values in separate variables
        street, number=txt_list[0][:street_space],txt_list[0][street_space+1:]
        city, postal = txt_list[1][city_space+1:],txt_list[1][:city_space]

        # get country from last element of the list
        country=txt_list[2]

        # create dataframe with named columns to append it later to the whole output table
        address_row=pd.DataFrame({'Address': [adr], 'Street': [street],'Number': [number], 'Postal': [postal], 'City': [city], 'Country': [country]})
        #print(f' address row is: {address_row}')
    except:
        print(f"Something went wrong on line {counter}. Check input data. Frame filled as 'N/A'")
        address_row = pd.DataFrame({'Address': [adr], 'Street': ["N/A"], 'Number': ["N/A"], 'Postal': ["N/A"], 'City': ["[N/A"],'Country': ["N/A"]})
    return (address_row)


# setup driver #

dname = pth.dirname(__file__)
lpath = '/geckodriver/geckodriver.exe'

gecko_path = dname + lpath
#print(gecko_path)
ser = Service(gecko_path)

options = webdriver.firefox.options.Options()
options.set_preference('intl.accept_languages', 'en-GB')


#options.add_argument("-headless") # headles option can be disabled for tracking and debugging

driver = webdriver.Firefox(options=options, service=ser)

url = 'https://www.google.com/maps'



# Timeout conditions when waiting for a field #
wait = WebDriverWait(driver, 10)

# starting value of page counter #
counter = 1

# save output before every n iterations #
autosave=5

# Create List of addresses to check #
addresslist = get_addresslist()
prog_len=len(addresslist)

# create output dataframe #
output_frame = pd.DataFrame({'Address': [],'Street': [],'Number': [], 'Postal': [], 'City': [], 'Country': []})

driver.get(url)


# search parameters for the parser

button_xpath="//button[@aria-label='Accept all']"
searchbox_ID = 'searchboxinput'
searchbutton_ID = "searchbox-searchbutton"
copybutton_xpath="//div[@data-tooltip='Copy address']"
copybutton_xpath_alt="//button[@data-item-id='address']"

# get number of the last page, or return None if there isn't one #
try:
    button=wait.until(EC.visibility_of_element_located((By.XPATH,  button_xpath)))
    driver.execute_script("arguments[0].click();", button)
    time.sleep(10)
except:
    print("NO BUTTON FOUND")

# go through link of every word from the main page #
for address in addresslist:

    # save every 5 addresses #

    if counter%autosave==0:
        print('autosaving')
        output_frame.to_csv("output.csv")

    try:

        print(f'Comparing Addresses with Google Maps. Current progress: {counter} out of {prog_len}')

        try:
            txt=get_address_text(address)
        except:
            if company_flag==True:
                # for some addresses the results might be better without company name. This exception is for them
                brk=address.find(";")
                address2=address[brk+1:]
                txt=get_address_text(address2,False)


        output_frame=pd.concat([output_frame,convert_string_to_df(address,txt)])
        counter=counter+1
    except:

        # if all fails and nothing is found the wrong value is forced and line to receive N/A
        output_frame.to_csv("output.csv")
        output_frame = pd.concat([output_frame, convert_string_to_df(address, "ENFORCE_ERROR")])
        print(f"there was an error on line: {counter+1}. Skipping the conversion for address {address}")
        counter = counter + 1
        driver.get(url)
        pass

output_frame.to_csv("output.csv")
# close connection #
driver.close()
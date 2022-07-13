#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul  9 16:07:46 2022

@author: sohanjs
"""

# Import the libraries

from PyPDF2 import PdfFileReader
import urllib.request
import openai
import glob
import re

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# Set inital Parameters
## Enter your OpenAI API keys to run GPT-3 model
## Remember to authorize the key before using it.
openai.api_key = "YOUR_APP_KEY"

## Charater_limit is set in order to avoid the maxing token request
CHARACTER_LIMIT = 3000

## search variable in the search field
search_for = "game theory"

## how many number of pdf downloads are needed ?
number_of_pdf_downloads = 5

#
# ---------------------- PART 1 ----------------------
# Comment from here
#
#
#
#
#
# Webscrapping
## Webdriver for selenium
## Using chrome webdriver,
driver = webdriver.Chrome(executable_path='driver/chromedriver.exe')
driver.implicitly_wait(0.5)
driver.maximize_window()
## url in use
driver.get('https://arxiv.org/')

## search for the text and click the search button
WebDriverWait(driver, 20).until(
    EC.element_to_be_clickable((By.XPATH, '//*[@id="header"]/div[2]/form/div/div[1]/input'))).send_keys(search_for)

search_button = driver.find_element_by_xpath('//*[@id="header"]/div[2]/form/div/button')
search_button.click()

# Implement no search found reply if search not found
#
# if not found, ask the user to what to do?
#


links = []
elems = driver.find_elements_by_tag_name('a')
for elem in elems:
    href = elem.get_attribute('href')
    if href is not None:
        if bool(re.search("https:\/\/arxiv.org\/pdf\/.*", href)):
            links.append(href)

titles = []
for i in range(len(links)):
    content_link = '//*[@id="main-container"]/div[2]/ol/li[{}]/p[1]'.format(i + 1)
    title = driver.find_element_by_xpath(content_link).text
    titles.append(title)


def download_file(download_url, filename):
    response = urllib.request.urlopen(download_url)
    file = open(filename + ".pdf", 'wb')
    file.write(response.read())
    file.close()


# Download the first 5 pdf from the site
for i in range(number_of_pdf_downloads):
    download_file(links[i], titles[i])

print("Successfully downloaded all the files as requested")

##  Stop commenting to test the part 2 of the progam
#
#
# ------------ Webscrapping is done here -------------
#
#
#
# ---------------------- PART 2 ----------------------
#

# Reads all the pdf in the current directory
files = glob.glob("*.pdf")


# displays the paper Content
def displayPaperContent(paperContent, page_start=0, page_end=5):
    for page in paperContent[page_start:page_end]:
        print(page.extract_text())


# Shows the Paper Summary from GPT-3
def showPaperSummary(paperContent):
    tldr_tag = "\n Tl;dr"
    text = ""

    numberPages = paperContent.pages
    ##Loop through all the pages of the paper and concatenate the text
    for page in numberPages:
        text += page.extract_text()

    # print("The full text of the paper is : ", text)
    try:
        textBegin = re.search("[\s\S]*?(?=INTRODUCTION|INTRODUCTIONS)", text).group()
    except AttributeError:
        textBegin = re.search("[\s\S]*?(?=INTRODUCTION|INTRODUCTIONS)", text)
    # print("The text before Introduction is : ", textBegin)
    # select the text after the conclusion
    try:
        textEnd = re.search("(?=CONCLUSION\n|CONCLUSIONS\n)[\s\S]*", text).group()
    except AttributeError:
        textEnd = re.search("(?=CONCLUSION\n|CONCLUSIONS\n)[\s\S]*", text)
    # print("The text after Conclusion is : ", textEnd)
    if textBegin is not None and textEnd is not None:
        text = textBegin + textEnd
    if text is not None:
        text = cut(text)
        text += tldr_tag
    print("The AI will summarize the text below:", text)
    response = openai.Completion.create(model="text-davinci-002",
                                        prompt=text,
                                        temperature=0,
                                        max_tokens=300,
                                        top_p=1,
                                        frequency_penalty=0,
                                        presence_penalty=0
                                        )
    print("The response is:")
    print(response["choices"][0]["text"])


##Make sure the numbers of characters in text is under or equals the limited charater
def cut(text):
    ###If it is, then we return the text
    ###If it is not, then we cut the text and return the text
    if len(text) <= CHARACTER_LIMIT:
        # print("Length text : , good", len(text))
        return text
    else:
        # print("Length text : , bad", len(text))
        return text[:CHARACTER_LIMIT]


print('Files are now loading')
# reads all the pdf files in the folder
for f in files:
    print()
    print(f)
    paperContent = PdfFileReader(f)
    showPaperSummary(paperContent)


def main(topic):
    print("Topic is: ", topic)
    print("Main launched")

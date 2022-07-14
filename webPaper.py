#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul  9 16:07:46 2022

@author: sohanjs
"""

# Import the libraries
import requests
from PyPDF2 import PdfFileReader
import openai
import glob
import re
import json

api_key = "wuQ7GVHRhe1qCJljF8TPOyxnmbtSDdIL"
api_endpoint = "https://api.core.ac.uk/v3"

# Set initial Parameters
# Enter your OpenAI API keys to run GPT-3 model
# Remember to authorize the key before using it.
openai.api_key = "YOUR_APP_KEY"

## Charater_limit is set in order to avoid the maxing token request
CHARACTER_LIMIT = 3000

## how many number of pdf downloads are needed ?
NUMBER_OF_PDF_DOWNLOADS = 5


def pretty_json(obj):
    print(json.dumps(obj, indent=4))


# ---------------------- PART 1 ----------------------
# This function receive a topic and search for the papers in the topic
# It will download the papers and save them in the folder named "papers"
# The files will be download for the CORE API that is an API that is used to search for research papers

def get_papers(topic):
    results, elapsed = query_core_api("/search/outputs", topic)
    print(f"The search took {elapsed} seconds")
    print(f"The results are: ")
    pretty_json(results)
    for result in results["results"]:
        print(f"Result is : {result}")
        download_pdf(result.sourceFulltextUrls[0])


def download_pdf(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Error code {response.status_code}, {response.content}")
        handle_error(response.status_code)


def query_core_api(url_fragment, query, limit=NUMBER_OF_PDF_DOWNLOADS):
    headers = {"Authorization": "Bearer " + api_key}
    query = {"q": query, "limit": limit}
    response = requests.post(f"{api_endpoint}{url_fragment}", data=json.dumps(query), headers=headers)
    if response.status_code == 200:
        return response.json(), response.elapsed.total_seconds()
    else:
        print(f"Error code {response.status_code}, {response.content}")
        handle_error(response.status_code)


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


# reads all the pdf files in the folder
for f in files:
    print()
    print(f)
    paperContent = PdfFileReader(f)
    showPaperSummary(paperContent)


def main():
    get_papers("Machine Learning")
    return None


def handle_error(status_code):
    pass


main()

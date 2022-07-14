#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul  9 16:07:46 2022

@author: sohanjs, Mahdjoubi Bilal
"""

# Import the libraries
import requests
from PyPDF2 import PdfFileReader
import openai
import glob
import re
import json
import os

API_KEY_CORE_API = "wuQ7GVHRhe1qCJljF8TPOyxnmbtSDdIL"
API_ENDPOINT_CORE_API = "https://api.core.ac.uk/v3"
OUTPUT_PDF = '.\pdfs'

# Set initial Parameters
# Enter your OpenAI API keys to run GPT-3 model
# Remember to authorize the key before using it.
openai.api_key = "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"

# Character_limit is set in order to avoid the maxing token request
CHARACTER_LIMIT = 3000

# how many number of pdf downloads are needed ?
NUMBER_OF_PDF_DOWNLOADS = 5


def pretty_json(obj):
    print(json.dumps(obj, indent=4))


# ---------------------- PART 1 ----------------------
# This function receive a topic and search for the papers in the topic
# It will download the papers and save them in the folder named "papers"
# The files will be downloaded for the CORE API that is an API that is used to get research papers

def get_papers(topic):
    results, elapsed = query_core_api("/search/works", topic)
    print(f"The search took {elapsed} seconds")
    print(f"The results are: ")
    pretty_json(results)
    for result in results["results"]:
        download_pdf(result["downloadUrl"], result["title"])


def download_pdf(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        file_path = os.path.join(OUTPUT_PDF, os.path.basename(filename))
        with open(file_path, "wb") as file:
            file.write(response.content)
    else:
        print(f"Error code {response.status_code}, {response.content}")
        handle_error(response.status_code)


def query_core_api(url_fragment, query, limit=NUMBER_OF_PDF_DOWNLOADS):
    headers = {"Authorization": "Bearer " + API_KEY_CORE_API}
    query = {"q": query, "limit": limit}
    response = requests.post(f"{API_ENDPOINT_CORE_API}{url_fragment}", data=json.dumps(query), headers=headers)
    if response.status_code == 200:
        return response.json(), response.elapsed.total_seconds()
    else:
        print(f"Error code {response.status_code}, {response.content}")
        handle_error(response.status_code)


# ---------------------- PART 2 ----------------------
#


# Shows the Paper Summary from GPT-3
def getPaperSummary(paperContent):
    tldr_tag = "\n Tl;dr"
    text = ""

    numberPages = paperContent.pages
    # Loop through all the pages of the paper and concatenate the text
    for page in numberPages:
        text += page.extract_text()

    try:
        textBegin = re.search("[\s\S]*?(?=INTRODUCTION|INTRODUCTIONS)", text).group()
    except AttributeError:
        textBegin = re.search("[\s\S]*?(?=INTRODUCTION|INTRODUCTIONS)", text)

    textEnd = text[-CHARACTER_LIMIT:]

    if textBegin is not None and textEnd is not None:
        text = textBegin + textEnd
    else:
        textBegin = text[0:CHARACTER_LIMIT]
        textEnd = text[-CHARACTER_LIMIT:]
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
    return response["choices"][0]["text"]


def cut(text):
    # Make sure the numbers of characters in text is under or equals the limited character
    if len(text) <= CHARACTER_LIMIT:
        # If it is, then we return the text
        return text
    else:
        # If it is not, then we cut the text and return the text
        return text[:CHARACTER_LIMIT]


def main():
    get_papers("Machine Learning")

    # Reads all the pdf in the pdfs directory
    files = glob.glob(OUTPUT_PDF + "/*.pdf")

    # reads all the pdf files in the folder
    for f in files:
        print(f)
        paperContent = PdfFileReader(f)
        summaryOfPaper = getPaperSummary(paperContent)


def handle_error(status_code):
    pass


main()

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
from pathlib import Path

API_KEY_CORE_API = "wuQ7GVHRhe1qCJljF8TPOyxnmbtSDdIL"
API_ENDPOINT_CORE_API = "https://api.core.ac.uk/v3"
OUTPUT_PDF = "pdfs"

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
    papersInfo = []

    for result in results["results"]:
        filename = generate_filename(result["title"])
        download_success = download_pdf(result["downloadUrl"], filename)
        if download_success:
            paper_info = "Title : " + result["title"] + ", Url : " + result["downloadUrl"]
            papersInfo.append(paper_info)

    return papersInfo


def generate_filename(filename):
    good_filename = ''.join(e for e in filename if e.isalnum())
    return good_filename + ".pdf"


def download_pdf(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        file_path = os.path.join(os.getcwd(), OUTPUT_PDF, os.path.basename(filename))
        file_path = Path(file_path)
        print(file_path)
        with open(file_path, "wb") as file:
            file.write(response.content)
            return True
    else:
        print(f"Error code {response.status_code}, {response.content}")
        handle_error(response.status_code)
        return False


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


def main(topic):
    # Get the papers from the topic
    papersInfo = get_papers(topic)
    print("The papers are:")
    print(papersInfo)

    # Reads all the pdf in the pdfs directory
    files = glob.glob(OUTPUT_PDF + "/*")

    summaries = []

    # reads all the pdf files in the folder
    for f in files:
        print(f)
        paperContent = PdfFileReader(f)
        summaryOfPaper = getPaperSummary(paperContent)
        summaries.append(summaryOfPaper)
        delete_file(f)

    # Merge the papersInfo array and the summaries array into one key value pair
    papersInfoAndSummaries = []
    for i in range(len(papersInfo)):
        papersInfoAndSummaries.append({"paperInfo": papersInfo[i], "summary": summaries[i]})
    return papersInfoAndSummaries


def handle_error(status_code):
    pass


def delete_file(file):
    os.remove(file)


files = [f for f in os.listdir('.') if os.path.isfile(f)]
for f in files:
    print(f)

resultOfMain = main("Machine Learning")
print(resultOfMain)

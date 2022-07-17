#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul  9 16:07:46 2022

@author: sohanjs, Mahdjoubi Bilal
"""

# Import the libraries
import requests
import openai
import re
import json
import os
from dotenv import load_dotenv
import reprlib

load_dotenv()  # take environment variables from .env.

API_KEY_CORE_API = os.environ.get('CORE_API_KEY')
API_ENDPOINT_CORE_API = "https://api.core.ac.uk/v3"

# Set initial Parameters
# Enter your OpenAI API keys to run GPT-3 model
# Remember to authorize the key before using it.
openai.api_key = os.environ.get('OPEN_AI_API_KEY')

# Character_limit is set in order to avoid the maxing token request
CHARACTER_LIMIT = 3000

# how many number of pdf downloads are needed ?
NUMBER_OF_PDF_DOWNLOADS = 3

MAX_NUMBER_OF_CHARACTERS_IN_PAPERS = 100000


def pretty_json(obj):
    return json.dumps(obj, indent=4)


# ---------------------- PART 1 ----------------------
# This function receive a topic and search for the papers in the topic
# It will download the papers and save them in the folder named "papers"
# The files will be downloaded for the CORE API that is an API that is used to get research papers


def get_papers(topic):
    results, elapsed = query_core_api("/search/works", topic)
    print(f"The search took {elapsed} seconds")
    print(f"The results are: ")
    print(reprlib.repr(results))
    papersInfo = []
    papersText = []

    for result in results["results"]:
        print(len(result["fullText"]))
        if "fullText" in result is not None and len(result["fullText"]) <= MAX_NUMBER_OF_CHARACTERS_IN_PAPERS:
            # filename = generate_filename(result["title"])
            # download_success = download_pdf(result["downloadUrl"], filename)
            # if download_success:
            paper_info = "Title : " + result["title"] + ", Url : " + result["downloadUrl"]
            papersInfo.append(paper_info)
            papersText.append(result["fullText"])

    return papersInfo, papersText


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


# Shows the Paper Summary from GPT-3
def getPaperSummary(paperContent):
    tldr_tag = "\n Tl;dr"
    text = ""

    print("The paper content is:")
    print(reprlib.repr(paperContent))

    # For loop to read all the text from the array paperContent
    for page in paperContent:
        text += page

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
    papersInfo, papersTexts = get_papers(topic)
    print("The papers infos are:")
    print(papersInfo)
    print("The papers text are:")
    print(papersTexts)

    summaries = []
    for paper in papersTexts:
        summaryOfPaper = getPaperSummary(paper)
        summaries.append(summaryOfPaper)

    # Merge the papersInfo array and the summaries array into one key value pair
    papersInfoAndSummaries = []
    for i in range(len(papersInfo) & len(summaries)):
        papersInfoAndSummaries.append({"paperInfo": papersInfo[i], "summary": summaries[i]})

    # Transform the papersInfoAndSummaries array into a json for html return
    return papersInfoAndSummaries


def handle_error(status_code):
    pass

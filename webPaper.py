#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jul  9 16:07:46 2022

@author: sohanjs
"""

import openai
import wget
import pathlib
from selenium import webdriver


browser = webdriver.Chrome('/Users/sohanjs/Downloads/software_setup_file/chromedriver')
browser.get('https://link.springer.com/')


def getPaper(paper_url, filename="random_paper.pdf"):
    """
    Downloads a paper from it's arxiv page and returns
    the local path to that file.
    """
    downloadedPaper = wget.download(paper_url, filename)
    downloadedPaperFilePath = pathlib.Path(downloadedPaper)

    return downloadedPaperFilePath


def showPaperSummary(paperContent):
    tldr_tag = "\n tl;dr:"
    # openai.organization = 'API KEY org'
    openai.api_key = "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"
    #    engine_list = openai.Engine.list()

    for page in paperContent:
        text = page.extract_text() + tldr_tag
        response = openai.Completion.create(engine="davinci", prompt=text, temperature=0.3,
                                            max_tokens=140,
                                            top_p=1,
                                            frequency_penalty=0,
                                            presence_penalty=0,
                                            stop=["\n"]
                                            )
        print(response["choices"][0]["text"])


paperContent = pdfplumber.open(paperFilePath).pages
showPaperSummary(paperContent)
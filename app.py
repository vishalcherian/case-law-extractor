import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

import PyPDF2
import requests
from flask import Flask, request

app = Flask(__name__)

@app.route("/api/ping")
def renderForm():
    return "<p>Hello World<p>"

@app.post("/api/upload")
def processFile():
    try:
        fileObject = request.files['the_file']
        pdfReader = PyPDF2.PdfFileReader(fileObject)
        cases = []
        for i in range(pdfReader.numPages):
            pageObject = pdfReader.getPage(i)
            casesOnPage = re.findall(r'[\w]+\n?\s+\n?v\.\n?\s+\n?[\w\n]+', pageObject.extractText())
            cases.extend(casesOnPage)
        
        processedCaseNames = processExtractedCases(cases)
        fullCases = getCases(processedCaseNames)
        fileObject.close()

        return (fullCases, 200)
    except Exception as e:
        print(e)
        return ('failure', 400)

def processExtractedCases(cases):
    for i in range(len(cases)):
        case = cases[i]
        cases[i] = ' '.join(cases[i].split())
    return list(set(cases))

def getCases(caseNames):
    results = []
    baseUrl = f"{os.getenv('CASE_LAW_URL')}/cases"
    
    def getFullCaseInformation(caseName):
        result = requests.get(
            url=f'{baseUrl}/?name_abbreviation={caseName}&full_case=true',
            headers={f"Authorization": f"Token {os.getenv('CASE_LAW_API_KEY')}"}
        )
        return result.json()
    
    threads = []
    with ThreadPoolExecutor(max_workers=20) as executor:
        for caseName in caseNames:
            threads.append(executor.submit(getFullCaseInformation, caseName))

        for task in as_completed(threads):
            results.append(task.result())

    return results
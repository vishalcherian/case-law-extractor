from flask import Flask, request
import PyPDF2
import re


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
        
        processedCases = processExtractedCases(cases)
        fileObject.close()
        return (processedCases, 200)
    except Exception as e:
        print(e)
        return ('failure', 400)

def processExtractedCases(cases):
    for i in range(len(cases)):
        case = cases[i]
        cases[i] = ' '.join(cases[i].split())
    return list(set(cases))

# # [\w]+\n?\s+\n?v\.\n?\s+\n?[\w\n]+

# from flask import Flask

# app = Flask(__name__)

# @app.route("/")
# def hello_world():
#     return "<p>Hello, World!</p>"
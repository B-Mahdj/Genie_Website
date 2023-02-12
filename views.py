import os

from PyPDF2 import PdfReader
from flask import Blueprint, render_template, request

from webPaper import getSummariesForTopic, store_mail, getSummariesForFile

views = Blueprint(__name__, "views")
UPLOAD_FOLDER = os.path.abspath("./pdfs")
ALLOWED_EXTENSIONS = {'pdf'}


def pretty_return(return_value):
    string_to_return = ""
    print("The return is :")
    print(return_value)
    for i in return_value:
        string_to_return += "<h3>" + i["paperInfo"] + "</h3>"
        string_to_return += "<p>" + i["summary"] + "</p>"

    return string_to_return


@views.route('/')
def home():
    return render_template('homePage.html')


@views.route('/data/', methods=['POST', 'GET'])
def data():
    if request.method == 'GET':
        return render_template('homePage.html')
    if request.method == 'POST':
        form_data = request.form.get("topic")
        if form_data is not None and form_data != "":
            return render_template('returnPage.html', datas=(getSummariesForTopic(form_data)))
        else:
            return "Please enter a topic"


@views.route('/mail/', methods=['POST', 'GET'])
def mail_storing():
    if request.method == 'GET':
        return render_template('homePage.html')
    if request.method == 'POST':
        mail_data = request.form.get("mail")
        print("Mail_data is : " + "'" + mail_data + "'")
        if mail_data is not None:
            print("Mail_data is not None")
            store_mail(mail_data)
            return render_template('thanksPage.html')
        else:
            return "Please enter a topic"


@views.route('/tutorial')
def tutorial():
    return render_template('tutorial.html')


@views.route('/info')
def info():
    return render_template('infoPage.html')


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@views.route('/upload', methods=['POST', 'GET'])
def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'filename' not in request.files:
            print('No file part')
            return render_template('homePage.html')
        file = request.files['filename']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            print('No selected file')
            return render_template('homePage.html')
        if file and allowed_file(file.filename):
            reader = PdfReader(file)
            # While loop len reader.pages
            fileTextContent = ""
            for i in range(len(reader.pages)):
                fileTextContent += reader.pages[i].extract_text()
            return render_template('returnPage.html', datas=(getSummariesForFile(fileTextContent)))
    else:
        return render_template('homePage.html')

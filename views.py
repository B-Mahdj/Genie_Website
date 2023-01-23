from flask import Blueprint, render_template, request
from webPaper import main

views = Blueprint(__name__, "views")


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
        return f"The URL /data is accessed directly. Try going to '/form' to submit form"
    if request.method == 'POST':
        form_data = request.form.get("topic")
        if form_data is not None:
            return render_template('returnPage.html', datas=(main(form_data)))
        else:
            return "Please enter a topic"


@views.route('/tutorial')
def tutorial():
    return render_template('tutorial.html')


@views.route('/info')
def info():
    return render_template('infoPage.html')

from flask import Blueprint, render_template, request
from webPaper import main, store_mail

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
        return render_template('homePage.html')
    if request.method == 'POST':
        form_data = request.form.get("topic")
        if form_data is not None and form_data != "":
            return render_template('returnPage.html', datas=(main(form_data)))
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

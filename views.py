from flask import Blueprint, render_template, request
import main from webPaper.py

views = Blueprint(__name__, "views")


@views.route('/')
def home():
    return render_template('index.html')


@views.route('/data/', methods=['POST', 'GET'])
def data():
    if request.method == 'GET':
        return f"The URL /data is accessed directly. Try going to '/form' to submit form"
    if request.method == 'POST':
        form_data = request.form
        return f"The form data is: {form_data}"

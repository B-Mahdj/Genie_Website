from flask import Flask
from flask_bootstrap import Bootstrap
from views import views

app = Flask(__name__)
Bootstrap(app)
app.register_blueprint(views, url_prefix='/')

if __name__ == '__main__':
    app.run(debug=True, port=8000)

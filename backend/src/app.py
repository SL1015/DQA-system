from flask import Flask
from flask import Flask, request, jsonify, Blueprint, current_app
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "Hello world from Flask!"

from apis.assessment import assessment_blueprint
app.register_blueprint(assessment_blueprint)
#app.register_blueprint(upload_blueprint)
app.config['UPLOAD_FOLDER'] = r'c:\UZH\datasets\save'


if __name__ == '__main__':
    app.run(debug=True)
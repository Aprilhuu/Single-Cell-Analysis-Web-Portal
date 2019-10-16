from flask import Flask


app = Flask(__name__)

import simlrportal.dataset

app.config['JSON_AS_ASCII'] = False
UPLOAD_FOLDER = './datasets/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

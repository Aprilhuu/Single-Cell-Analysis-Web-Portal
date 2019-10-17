from flask import render_template, request
from werkzeug.utils import secure_filename
from simlrportal import app
import os
import json
from datetime import datetime
from .models import DataFile


ALLOWED_EXTENSIONS = set(['h5ad', 'csv', 'h5', 'loom', 'mtx', 'txt', 'zip', 'rar', '7z'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/dataupload.html')
def render_dataupload():
    return render_template("dataupload.html", allowed_file=", ".join(ALLOWED_EXTENSIONS))

@app.route('/dataupload', methods=['POST'])
def dataupload():
    if not os.path.isdir(app.config['UPLOAD_FOLDER']):
        os.mkdir(app.config['UPLOAD_FOLDER'])
    if 'file' not in request.files:
        return 'No file part'
    if file.filename == '':
        return 'No file part'

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        file = request.files['file']
        form = request.form.to_dict()

        datafile = DataFile(filename=filename,
                            name=form.get("name", ""),
                            owner=form.get("owner", "update"),
                            description=form.get("description", ""),
                            created=datetime.now(),
                            modified=datetime.now())

        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return "success"

@app.route('/datasets.html')
def render_datasets():
    return render_template("datasets.html")

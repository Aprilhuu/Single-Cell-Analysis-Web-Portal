from flask import render_template, request, jsonify
from werkzeug.utils import secure_filename
from simlrportal import app, db
import os
import json
from datetime import datetime
from time import time
from .models import DataFile



ALLOWED_EXTENSIONS = set(['h5ad', 'csv', 'h5', 'loom', 'mtx', 'txt', 'zip', 'rar', '7z'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/dataupload.html')
def render_dataupload():
    return render_template("dataupload.html", allowed_file=", ".join(ALLOWED_EXTENSIONS))

@app.route('/datasets.html')
def render_datasets():
    return render_template("datasets.html")


@app.route('/dataupload', methods=['POST'])
def dataupload():
    if not os.path.isdir(app.config['UPLOAD_FOLDER']):
        os.mkdir(app.config['UPLOAD_FOLDER'])
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']
    form = request.form.to_dict()

    if file.filename == '':
        return 'No file part'

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        hashname = form.get("name", "") + "_" + hex(int(time()))
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], hashname + "." +ext))
        datafile = DataFile(id=hashname,
                            source="local",
                            name=form.get("name", ""),
                            owner=form.get("owner", "update"),
                            description=form.get("description", ""),
                            modified=datetime.now())
        db.session.add(datafile)
        db.session.commit()
        return "success"


@app.route('/datasets/', methods=['GET'])
def get_all_datasets():
    limit = request.args.get("limit")
    offset = request.args.get("offset")
    result = DataFile.query.limit(limit).offset(offset).all()
    return jsonify([d.to_dict() for d in result])

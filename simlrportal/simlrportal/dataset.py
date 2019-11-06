from flask import render_template, request, jsonify
from werkzeug.utils import secure_filename
from simlrportal import app, db
import os
import json
from datetime import datetime
from time import time
from .models import DataFile
from shutil import unpack_archive, get_archive_formats, rmtree


ALLOWED_EXTENSIONS = set(['h5ad', 'csv', 'h5', 'loom', 'mtx', 'txt'] + [x[0] for x in get_archive_formats()])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS






@app.route('/dataupload.html', methods=['GET'])
def render_dataupload():
    return render_template("dataupload.html", allowed_file=", ".join(ALLOWED_EXTENSIONS))

@app.route('/datasets.html', methods=['GET'])
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
        file_ori, ext = filename.rsplit('.', 1)
        ext = ext.lower()
        hashname = form.get("name", "") + "_" + hex(int(time()))
        path = os.path.join(app.config['UPLOAD_FOLDER'], hashname + "." +ext)
        file.save(path)
        if ext in [x[0] for x in get_archive_formats()]:
            unpack_archive(path, os.path.join(app.config['UPLOAD_FOLDER']))
            os.rename(os.path.join(app.config['UPLOAD_FOLDER'] + file_ori),
                      os.path.join(app.config['UPLOAD_FOLDER'] + hashname))
            os.remove(path)
            path = os.path.join(app.config['UPLOAD_FOLDER'], hashname)
        try:
            datafile = DataFile(id=hashname,
                                source="local",
                                name=form.get("name", ""),
                                path=path,
                                description=form.get("description", ""),
                                modified=datetime.now())
            db.session.add(datafile)
            db.session.commit()
        except Exception as e:
            print(e)
            return "failed"
        return "success"



@app.route('/datasets', methods=['GET', 'DELETE'])
def get_all_datasets():
    if request.method == 'GET':
        limit = request.args.get("limit")
        offset = request.args.get("offset")
        result = DataFile.query.limit(limit).offset(offset).all()
        return jsonify([d.to_dict() for d in result])
    if request.method == "DELETE":
        id = request.form.to_dict().get("id", None)
        result = DataFile.query.filter(DataFile.id == id).first()
        if os.path.isfile(result.path):
            os.remove(result.path)
        if os.path.isdir(result.path):
            rmtree(result.path)
        db.session.delete(result)
        db.session.commit()
        return {'id': result.id, 'path': result.path}

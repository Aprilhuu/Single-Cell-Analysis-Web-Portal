from flask import render_template, request, jsonify
from simlrportal import app, db
import os
from simlrportal.src.worker import Worker
from simlrportal.models.models import *

@app.route('/newprocess.html', methods=['GET'])
def render_newprocess():
    return render_template("newprocess.html")

@app.route('/process.html', methods=['GET'])
def render_process():
    worker = WorkerRecord.query.filter_by(id=request.args.get("name", "")).first()
    if worker is None:
        return 404
    worker = worker.to_dict()
    return render_template("process.html", worker=worker)

@app.route('/process-history.html', methods=['GET'])
def render_process_history():
    return render_template("process-history.html")

@app.route('/installed-methods', methods=['GET', 'POST'])
def get_installed_methods():
    if request.method == "GET":
        type = request.args.get("type", "")
        name = request.args.get("name", "")
        package = request.args.get("name", "")
        if name == "_all":
            f = open(os.path.join("./simlrportal/installed-methods/" + type + ".json"), "r")
            read_json = f.read()
            f.close()
            return read_json
    return "failed", 404


@app.route("/new-process", methods=['GET', 'POST'])
def post_new_process():
    data = request.get_json()
    worker = Worker(data['process'], data['name'])
    integrity = worker.check_integrity()
    if integrity['status']:
        worker.start()
    return jsonify(integrity)

@app.route("/process-history", methods=['GET'])
def get_process_history():
    if request.method == 'GET':
        name = request.args.get("name", "")
        if name == "_all":
            result = WorkerRecord.query.all()
        else:
            result = Process.query.filter_by(id = name)
        return jsonify([d.to_dict() for d in result])

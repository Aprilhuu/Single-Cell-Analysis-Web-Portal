from flask import render_template, request, jsonify
from simlrportal import app, db
import os
from simlrportal.src.worker import Worker
from simlrportal.models.models import *

@app.route('/newprocess.html', methods=['GET'])
def render_newprocess():
    return render_template("newprocess.html")

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
    worker = Worker(data)
    integrity = worker.check_integrity()
    if integrity['status']:
        worker.start()
    return jsonify(integrity)

@app.route("/process-history", methods=['GET'])
def get_process_history():
    if request.method == 'GET':
        result = Process.query.all()
        return jsonify([d.to_dict() for d in result])

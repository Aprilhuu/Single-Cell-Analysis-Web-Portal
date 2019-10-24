from flask import render_template, request, jsonify
from simlrportal import app, db
import os
import json

@app.route('/newprocess.html', methods=['GET'])
def render_newprocess():
    return render_template("newprocess.html")

from flask import Flask, redirect
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

db.create_all()

import simlrportal.dataset
import simlrportal.process

@app.route("/")
def render_index():
    return redirect("/newprocess.html")

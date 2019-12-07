from simlrportal import app, db
import os


if not os.path.exists(app.config['CACHE_FOLDER']):
    os.makedirs(app.config['CACHE_FOLDER'])
if not os.path.exists(app.config['TEMP_FOLDER']):
    os.makedirs(app.config['TEMP_FOLDER'])
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db.create_all()

if __name__ == "__main__":
    app.run(debug=True)

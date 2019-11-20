call conda activate simlr
set FLASK_APP=simlrportal
set FLASK_ENV=development
start flask run
start chrome http://localhost:5000/
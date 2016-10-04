from splinetools import app
from flask import render_template

ABOUT_ROOT_URL = "/about"

@app.route(ABOUT_ROOT_URL)
def about():
	return render_template("about.html")
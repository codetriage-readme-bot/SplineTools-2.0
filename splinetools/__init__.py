from flask import Flask, render_template
from flask.ext.googlemaps import GoogleMaps
app = Flask(__name__)
app.secret_key = "9qr9Sq6ZzTWwW8fc8RxQbnXBChWfhXycLhAJ6Y5K"
GoogleMaps(app)

@app.route("/")
def home():
	return render_template("about.html")

import splinetools.whois
import splinetools.about
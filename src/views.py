from flask import Blueprint, render_template, request, flash, jsonify


views = Blueprint('views', __name__)


@views.route('/')
def home():
    data = [
        ("01-01-2020", 1234),
        ("02-01-2020", 1235),
        ("03-01-2020", 1236),
        ("04-01-2020", 1237),
        ("05-01-2020", 1238),
        ("06-01-2020", 1239)
    ]
    labels = [row[0] for row in data]
    values = [row[1] for row in data]
    return render_template("base.html", labels=labels, values=values)
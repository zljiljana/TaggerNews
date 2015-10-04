from flask import render_template, request
from app import app
from filter import filter

@app.route('/')
@app.route('/input')
def render_input():
	return render_template("hn_tag.html")

@app.route('/filter')
def render_filter():
    userTag = request.args.get('ID')
    filter_snippet = filter(userTag)
    return render_template("output.html", snippet = filter_snippet)
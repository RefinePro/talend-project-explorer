from flask import Flask
from flask import render_template
from flask import request
from talend import TalendDoc
import pprint
from beeprint import pp

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


@app.route('/talend-project/')
def project():
    path = request.args.get('path')
    if path is not None:
        parser = TalendDoc.TalendDoc(path)
        doc = parser.parse()
        # pp(doc)
    else:
        doc = None
    return render_template('talend-project.html', doc=doc, path=path)

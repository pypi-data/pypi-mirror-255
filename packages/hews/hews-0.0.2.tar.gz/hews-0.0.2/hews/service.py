from .core import x

from flask import Flask

app = Flask(__name__)


@app.route('/')
def root():
    return x.service()



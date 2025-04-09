from flask import Flask

app: Flask = None

def create_app(name):
    global app
    app = Flask(name)
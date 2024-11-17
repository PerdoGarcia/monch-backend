from flask import Flask
import requests
import os

app = Flask(__name__)
app.config.from_pyfile('settings.py')


@app.route('/')
def main():
    return 'Hello, World!'


@app.route('/test')
def test():
    secret_key = os.environ.get('PINATA_JWT', '')
    url = "https://api.pinata.cloud/data/testAuthentication"
    headers = {"Authorization": "Bearer " + secret_key}
    response = requests.get(url, headers=headers)
    return response.text

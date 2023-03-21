from flask import Flask, render_template
from forms_wtf.file import FileForm
import os
import json
from werkzeug.utils import secure_filename
import requests
import random


app = Flask(__name__)


@app.route('/statistics')
def statistics():
    response = requests.get(f"http://minecraft2d.pythonanywhere.com/player/?player=Subvius")
    json1 = response.json()
    photo = random.choice(get_all_image_name(path='static/background'))
    if json1["success"]:
        return render_template('stat.html', json=json1, photo=photo)


def get_all_image_name(path='static/cloak'):
    images = list()
    for f in os.listdir(path):
        if os.path.isfile(os.path.join(path, f)):
            images.append(f)
    return images


@app.route('/')
def index():
    images = get_all_image_name()
    return render_template('shop.html', images=images, len=len(images))


if __name__ == '__main__':
    app.run(host='localhost', port=8080)

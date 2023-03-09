from flask import Flask, render_template
from forms_wtf.file import FileForm
import os
import json
from werkzeug.utils import secure_filename
import random


app = Flask(__name__)
app.config['SECRET_KEY'] = 'ladjghkdhfglkjdhglkjhdslfkgjhldkfjh'


def get_all_image_name(path='static/img'):
    images = list()
    for f in os.listdir(path):
        if os.path.isfile(os.path.join(path, f)):
            images.append(f)
    return images


@app.route('/', methods=['GET', 'POST'])
def index():
    form = FileForm()
    if form.validate_on_submit():
        f = form.file.data
        filename = secure_filename(f.filename)
        f.save(os.path.join('static', 'img', filename))
    images = get_all_image_name()
    return render_template('carousel.html', form=form, images=images)


@app.route('/members')
def news():
    name = random.choice(['Алексей', "Елисей", "Николай"])
    with open("templates/members.json", "rt", encoding="utf8") as f:
        news_list = json.loads(f.read())
    return render_template('members.html', news=news_list, name=name)


if __name__ == '__main__':
    app.run(host='localhost', port=8080)

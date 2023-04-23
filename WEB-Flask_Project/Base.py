from flask import Flask, render_template, redirect, request
import os
import requests
import random
from login import LoginForm
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/statistics/<nickname>')
def statistics(nickname):
    response = requests.get(f"http://minecraft2d.pythonanywhere.com/player/?player={nickname}")
    json1 = response.json()
    date = datetime.datetime.fromtimestamp(json1["player"]["first_login"]).strftime("%d/%m/%Y, %H:%M")
    photo = random.choice(get_all_image_name(path='static/background'))
    if json1["success"]:
        return render_template('stat.html', json=json1, photo=photo, date=date)


def get_all_image_name(path='static/cloak'):
    images = list()
    for f in os.listdir(path):
        if os.path.isfile(os.path.join(path, f)):
            images.append(f)
    return images


@app.route('/shop/<nickname>', methods=['GET', 'POST'])
def shop(nickname):
    images = get_all_image_name()
    if request.method == 'GET':
        for elem in images:
            if request.values.get(elem) == elem:
                print(elem)
        else:
            return render_template('shop.html', images=images, len=len(images), name=nickname)
    elif request.method == 'POST':
        return render_template('shop.html', images=images, len=len(images), name=nickname)
    return render_template('shop.html', images=images, len=len(images), name=nickname)


@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        name = form.username.data
        password = form.password.data
        response = requests.get(f"https://minecraft2d.pythonanywhere.com/auth/?nickname={name}&password={password}")
        json1 = response.json()
        if not json1["success"]:
            if json1["E"] != "incorrect password":
                requests.get(
                    f"https://minecraft2d.pythonanywhere.com/auth/?nickname={name}&password={password}&create=True")
                return redirect(f"/statistics/{name}")
        else:
            return redirect(f"/statistics/{name}")

    return render_template('registration.html', title='Авторизация', form=form)


if __name__ == '__main__':
    app.run(host='localhost', port=8080)

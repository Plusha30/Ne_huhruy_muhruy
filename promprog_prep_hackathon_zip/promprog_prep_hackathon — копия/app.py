from flask import Flask, render_template, request, redirect, url_for
from ivan_db import *
import pathlib
import json

app = Flask(__name__)
app.secret_key = 'hackathon_key'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

@app.route('/')
def landing():
    return render_template('landing.html', **commonkwargs({}))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', **commonkwargs({}))

@app.route('/object/<int:id>')
def object_detail(id):
    # ИСПРАВЛЕНО: добавлены скобки ({}), теперь функция вернет словарь
    return render_template('object.html', id=id, **commonkwargs({}))

@app.route('/login')
def login():
    return render_template('login.html', **commonkwargs({}))

@app.route('/register', methods=["GET", "POST"])
def register():
    #print("a")
    #if (request.method == 'POST'):
    #    data = request.form.to_dict(flat=False) 
    #    users_base[data['email'][0]] = [data['password'][0], data['name'][0]]
    #    with open(f"{pathlib.Path(__file__).parent.resolve()}/users_base.txt", 'w', encoding='utf-8') as f:
    #        f.write(json.dumps(users_base, indent=4))
    #    return redirect(url_for('profile'), 301)
    return render_template('register.html', **commonkwargs({}))

@app.route('/profile')
def profile():
    return render_template('profile.html', **commonkwargs({}))

@app.route('/pricing')
def pricing():
    return render_template('pricing.html', **commonkwargs({}))

if __name__ == '__main__':
    tovars_data = getTovarsData(f"{pathlib.Path(__file__).parent.resolve()}/categories")
    with open(f"{pathlib.Path(__file__).parent.resolve()}/users_base.json", 'r', encoding='utf-8') as f:
        info = f.read()
        users_base = json.loads(info)
    app.run(port=5237, host="127.0.0.1", debug=True)
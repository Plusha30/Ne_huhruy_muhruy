from flask import Flask, render_template, request, redirect, url_for
import os
import json
import pathlib
import shutil

global tovars_data
global users_base
tovars_data = {}
users_base = {}
email = 'placeholder'

def return_image(path, placeholder):
    if os.path.exists(f"{pathlib.Path(__file__).parent.resolve()}/static/images/{path}.jpg"):
        return f'images/{path}.jpg'
    else:
        return f'images/common/{placeholder}.jpg'

def commonkwargs(kwargs):
    if (email in users_base):
        return kwargs | {'username': users_base[email][1], 'userimg': return_image(f'users/{email}', 'user_placeholder')}
    else:
        return kwargs | {'username': 'Log in', 'userimg': return_image(f'users/{email}', 'user_placeholder')}

def getTovarsData(folder_path):
    total = dict()
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            d = json.loads(content)
            total |= d
            for i in d:
                d[i] |= {"tovars": {}}
            way = f"{pathlib.Path(__file__).parent.resolve()}/tovars/{filename[:-5]}"
            for tovar in os.listdir(way):
                tovar_path = os.path.join(way, tovar)
                with open(tovar_path, 'r', encoding='utf-8') as f1:
                    info = f1.read()
                    tov = json.loads(info)
                    for i in d:
                        d[i]["tovars"] |= tov
    return total

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
    if (request.method == 'POST'):
        print("a")
        data = request.form.to_dict(flat=False) 
        users_base[data['email'][0]] = [data['password'][0], data['name'][0]]
        with open(f"{pathlib.Path(__file__).parent.resolve()}/users_base.json", 'w', encoding='utf-8') as f:
            f.write(json.dumps(users_base, indent=4))
        global email
        email = data['email'][0]
        return redirect(url_for('profile'), 301)
    return render_template('register.html', **commonkwargs({}))

@app.route('/profile')
def profile():
    return render_template('profile.html', **commonkwargs({}))

@app.route('/pricing')
def pricing():
    return render_template('pricing.html', **commonkwargs({}))

@app.route('/<name>')
def four04(name):
    return render_template('404.html')

def readfiles():
    global tovars_data
    global users_base
    tovars_data = getTovarsData(f"{pathlib.Path(__file__).parent.resolve()}/categories")
    with open(f"{pathlib.Path(__file__).parent.resolve()}/users_base.json", 'r', encoding='utf-8') as f:
        info = f.read()
        users_base = json.loads(info)
    
if __name__ == '__main__':
    readfiles()
    app.run(port=5237, host="127.0.0.1", debug=True)
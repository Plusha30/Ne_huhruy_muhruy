from flask import Flask, render_template, request, redirect, url_for
import os
import json
import pathlib
import shutil

# some global variables

global tovars_data
global users_base
global products_db
tovars_data = {} 
users_base = {}
products_db = {}
email = 'placeholder'
base_path = pathlib.Path(__file__).parent.resolve()

# basic functions for site render

def return_image(path, placeholder):
    full_path = f"{base_path}/static/images/{path}.jpg"
    if os.path.exists(full_path):
        return f'images/{path}.jpg'
    else:
        return f'images/common/{placeholder}.jpg'

def commonkwargs(kwargs):
    if (email in users_base):
        return kwargs | {'username': users_base[email][1], 'userimg': return_image(f'users/{email}', 'user_placeholder')}
    else:
        return kwargs | {'username': 'Log in', 'userimg': return_image(f'users/{email}', 'user_placeholder')}

#read data about tovars i think (maybe delete)

def getTovarsData(folder_path):
    total = dict()
    if not os.path.exists(folder_path):
        return {}
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            d = json.loads(content)
            total |= d
            for i in d:
                d[i] |= {"tovars": {}}
            way = f"{base_path}/tovars/{filename[:-5]}"
            if os.path.exists(way):
                for tovar in os.listdir(way):
                    tovar_path = os.path.join(way, tovar)
                    with open(tovar_path, 'r', encoding='utf-8') as f1:
                        info = f1.read()
                        tov = json.loads(info)
                        for i in d:
                            d[i]["tovars"] |= tov
    return total

#app

app = Flask(__name__)
app.secret_key = 'hackathon_key'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

#routes

@app.route('/')
def landing():
    return render_template('landing.html', **commonkwargs({}))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', **commonkwargs({}))

@app.route('/object/<int:id>')
def object_detail(id):
    return render_template('object.html', id=id, **commonkwargs({}))

# --- ИЗМЕНЕННЫЙ МАРШРУТ (ДИНАМИЧЕСКИЕ ТОВАРЫ) ---
@app.route('/product/<id>')
def product_detail(id):
    # Берем данные из словаря products_db
    product_data = products_db.get(id)

    # Если товара нет (например, id=999), показываем ошибку
    if not product_data:
        return render_template('404.html', **commonkwargs({}))

    # Передаем данные в шаблон как переменную product
    return render_template('product.html', id=id, product=product_data, **commonkwargs({}))
# -----------------------------------------------

@app.route('/login', methods=["GET", "POST"])
def login():
    if (request.method == 'POST'):
        data = request.form.to_dict(flat=False)
        input_email = data['email'][0]
        if len(data['email']) > 0 and data['email'][0] in users_base:
            global email
            email = input_email
            return redirect(url_for('profile'), 301)
        else:
            pass
    return render_template('login.html', **commonkwargs({}))

@app.route('/register', methods=["GET", "POST"])
def register():
    if (request.method == 'POST'):
        data = request.form.to_dict(flat=False)
        users_base[data['email'][0]] = [data['password'][0], data['name'][0]]
        with open(f"{base_path}/users_base.json", 'w', encoding='utf-8') as f:
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

@app.route('/ultimate-dashboard')
def ultimate_dashboard():
    return render_template('super_dashboard.html', **commonkwargs({}))

@app.errorhandler(404)
def four04(name):
    return render_template('404.html', **commonkwargs({}))

def readfiles():
    global tovars_data
    global users_base
    global base_path
    global products_db
    users_path = f"{base_path}/users_base.json"
    if not os.path.exists(users_path):
        with open(users_path, 'w', encoding='utf-8') as f:
            f.write("{}")
    products_path = f"{base_path}/tovars.json"
    if not os.path.exists(products_path):
        with open(products_path, 'w', encoding='utf-8') as f:
            f.write("{}")
    tovars_data = getTovarsData(f"{base_path}/categories")
    with open(users_path, 'r', encoding='utf-8') as f:
        info = f.read()
        if info:
            users_base = json.loads(info)
        else:
            users_base = {}
    with open(products_path, 'r', encoding='utf-8') as f:
        info = f.read()
        if info:
            products_db = json.loads(info)
        else:
            products_db = {}

if __name__ == '__main__':
    readfiles()
    app.run(port=5237, host="127.0.0.1", debug=True)
from flask import Flask, render_template, request, redirect, url_for
import os
import json
import pathlib

#global variables
global users_base
global products_db
users_base = {}
products_db = {}
email = 'placeholder'
base_path = pathlib.Path(__file__).parent.resolve()
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

#useful function for filework and etc
def return_image(path, placeholder):
    full_path = f"{base_path}/static/images/{path}.jpg"
    if os.path.exists(full_path):
        return f'images/{path}.jpg'
    else:
        return f'images/common/{placeholder}.jpg'

def commonkwargs():
    if (email in users_base):
        return {'username': users_base[email][1], 'userimg': return_image(f'users/{email}', 'user_placeholder'), 'desc': users_base[email][2], 'phone': users_base[email][3]}
    else:
        return {'username': 'Log in', 'userimg': return_image(f'users/{email}', 'user_placeholder'), 'desc': 'empty', 'phone': 'N/A'}

#basic routes
@app.route('/')
def landing():
    return render_template('landing.html', **commonkwargs())

@app.route('/pricing')
def pricing():
    return render_template('pricing.html', **commonkwargs())

@app.route('/ultimate_dashboard')
def ultimate_dashboard():
    return render_template('super_dashboard.html', **commonkwargs())

@app.errorhandler(404)
def four04(name):
    return render_template('404.html', **commonkwargs())

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', **commonkwargs())

@app.route('/object/<int:id>')
def object_detail(id):
    return render_template('object.html', id=id, **commonkwargs())

@app.route('/product/<id>')
def product_detail(id):
    product_data = products_db.get(id)
    if not product_data:
        return render_template('404.html', **commonkwargs())
    return render_template('product.html', id=id, product=product_data, **commonkwargs())

#login-register-profile
@app.route('/login', methods=["GET", "POST"])
def login():
    global email
    if (email != 'placeholder'):
        return redirect(url_for('profile'), 302)
    if (request.method == 'POST'):
        data = request.form.to_dict(flat=False)
        input_email = data['email'][0]
        if len(data['email']) > 0 and data['email'][0] in users_base and data['password'][0] == users_base[input_email][0]:
            email = input_email
            return redirect(url_for('profile'), 302)
        else:
            pass
    return render_template('login.html', **commonkwargs())

@app.route('/register', methods=["GET", "POST"])
def register():
    global email
    if (email != 'placeholder'):
        return redirect(url_for('profile'), 302)
    if (request.method == 'POST'):
        data = request.form.to_dict(flat=False)
        users_base[data['email'][0]] = [data['password'][0], data['name'][0], "empty", "N/A"]
        with open(f"{base_path}/users_base.json", 'w', encoding='utf-8') as f:
            f.write(json.dumps(users_base, indent=4))
        email = data['email'][0]
        return redirect(url_for('profile'), 302)
    return render_template('register.html', **commonkwargs())

@app.route('/profile', methods=["GET", "POST"])
def profile():
    global email
    if (email == 'placeholder'):
        return redirect(url_for('login'), 302)
    if (request.method == 'POST'):
        data = request.form.to_dict(flat=False)
        if (data['commit_type'][0] == 'logout'):
            email = 'placeholder'
            return redirect(url_for('landing'), 302)
        if (data['commit_type'][0] == 'update_data'):
            if (len(data['name']) > 0):
                users_base[email][1] = data['name'][0]
            if (len(data['phone']) > 0):
                users_base[email][3] = data['phone'][0]
            if (len(data['desc']) > 0):
                users_base[email][2] = data['desc'][0]
            with open(f"{base_path}/users_base.json", 'w', encoding='utf-8') as f:
                f.write(json.dumps(users_base, indent=4))
        if (data['commit_type'][0] == 'update_photo'):
            if (request.files['avatar'].filename == ''):
                if (os.path.exists(f"{base_path}/static/images/users/{email}.jpg")):
                    os.remove(f"{base_path}/static/images/users/{email}.jpg")
            else:
                photo = request.files['avatar']
                if (photo.filename != ''):
                    path = f"{base_path}/static/images/users/{email}.jpg"
                    photo.save(path)
    return render_template('profile.html', **commonkwargs())

#collect data from files function
def readfiles():
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

#start
if __name__ == '__main__':
    readfiles()
    app.run(port=5237, host="127.0.0.1", debug=True)
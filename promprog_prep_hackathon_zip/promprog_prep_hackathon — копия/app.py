from flask import Flask, render_template, request, redirect, url_for, make_response
from subscript.filework import *
from subscript.reports import *
import os

#global variables
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

#cookie work
def getlogin(rq):
    if (rq.get('account')):
        return rq.get('account')
    return "placeholder"

#basic routes
@app.route('/')
def landing():
    return render_template('landing.html', **commonkwargs(getlogin(request.cookies)))

@app.route('/pricing')
def pricing():
    return render_template('pricing.html', **commonkwargs(getlogin(request.cookies)))

@app.route('/ultimate_dashboard')
def ultimate_dashboard():
    return render_template('super_dashboard.html', **commonkwargs(getlogin(request.cookies)))

@app.errorhandler(404)
def four04(name):
    return render_template('404.html', **commonkwargs(getlogin(request.cookies)))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', tovarlist=gettovarlist(), **commonkwargs(getlogin(request.cookies)))

@app.route('/object/<int:id>')
def object_detail(id):
    return render_template('object.html', id=id, **commonkwargs(getlogin(request.cookies)))

@app.route('/product/<id>', methods=['GET', 'POST'])
def product_detail(id):
    product_data = gettovar(id)
    if not product_data:
        return render_template('404.html', **commonkwargs(getlogin(request.cookies)))
    if (request.method == 'POST'):
        data = request.form.to_dict(flat=False)
        product_data['reviews'].append({'user': getuser(getlogin(request.cookies))["username"], "text": data['commentary'][0]})
        settovar(id, product_data)
        return render_template('product.html', id=id, product=product_data, **commonkwargs(getlogin(request.cookies)))
    return render_template('product.html', id=id, product=product_data, **commonkwargs(getlogin(request.cookies)))

#login-register-profile
@app.route('/login', methods=["GET", "POST"])
def login():
    email = getlogin(request.cookies)
    if (email != 'placeholder'):
        return redirect(url_for('profile'), 302)
    if (request.method == 'POST'):
        data = request.form.to_dict(flat=False)
        input_email = data['email'][0]
        if len(data['email']) > 0 and getuser(data['email'][0]) != False and data['password'][0] == getuser(data['email'][0])['password']:
            response = make_response(redirect(url_for('profile'), 302))
            response.set_cookie('account', input_email)
            return response
        else:
            pass
    return render_template('login.html', **commonkwargs(email))

@app.route('/register', methods=["GET", "POST"])
def register():
    email = getlogin(request.cookies)
    if (email != 'placeholder'):
        return redirect(url_for('profile'), 302)
    if (request.method == 'POST'):
        data = request.form.to_dict(flat=False)
        setuser(data['email'][0], {'password': data['password'][0], 'username': data['name'][0], 'description': "empty", \
                                   'phone': "N/A", 'rights': int(data['rights'][0]), 'money': 0})
        email = data['email'][0]
        response = make_response(redirect(url_for('profile'), 302))
        response.set_cookie('account', email)
        return response
    return render_template('register.html', **commonkwargs(email))

@app.route('/profile', methods=["GET", "POST"])
def profile():
    email = getlogin(request.cookies)
    if (email == 'placeholder'):
        return redirect(url_for('login'), 302)

    if (request.method == 'POST'):
        data = request.form.to_dict(flat=False)

        # 1. Выход
        if (data['commit_type'][0] == 'logout'):
            email = 'placeholder'
            response = make_response(redirect(url_for('landing'), 302))
            response.set_cookie('account', email)
            return response

        # 2. Обновление текстовых данных
        if (data['commit_type'][0] == 'update_data'):
            changes = getuser(email)
            if (len(data['name']) > 0):
                changes['username'] = data['name'][0]
            if (len(data['phone']) > 0):
                changes['phone'] = data['phone'][0]
            if (len(data['description']) > 0):
                changes['description'] = data['description'][0]
            setuser(email, changes)

        # 3. Обновление фото
        if (data['commit_type'][0] == 'update_photo'):
            if (request.files['avatar'].filename == ''):
                if (os.path.exists(f"{base_path}/static/images/users/{email}.jpg")):
                    os.remove(f"{base_path}/static/images/users/{email}.jpg")
            else:
                photo = request.files['avatar']
                if (photo.filename != ''):
                    path = f"{base_path}/static/images/users/{email}.jpg"
                    photo.save(path)

        # 4. Обновление аллергии (НОВОЕ)
        if (data['commit_type'][0] == 'update_health'):
            changes = getuser(email)
            # data.get('allergies', []) вернет список выбранных чекбоксов или пустой список
            changes['allergies'] = data.get('allergies', [])
            setuser(email, changes)

    return render_template('profile.html', **commonkwargs(email))

#start
if __name__ == '__main__':
    app.run(port=5237, host="127.0.0.1", debug=True)
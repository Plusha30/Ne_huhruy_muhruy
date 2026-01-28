#Выделенный файл для всех путей, связанных с аккаунтами

from flask import render_template, request, redirect, url_for, send_file, session
from subscript.filework import *
from subscript.account_system import *
from random import randint

def login():
    email = getlogin()
    if (email != 'placeholder'):
        return redirect(url_for('profile'), 302)
    if (request.method == 'POST'):
        data = request.form.to_dict(flat=False)
        input_email = data['email'][0]
        if len(data['email']) > 0 and getuser(data['email'][0]) != False and data['password'][0] == getuser(data['email'][0])['password']:
            setlogin(input_email)
            return redirect(url_for('profile'), 302)
        else:
            pass
    return render_template('login.html', **commonkwargs(email))

def register():
    email = getlogin()
    if (email != 'placeholder'):
        return redirect(url_for('profile'), 302)
    if (request.method == 'POST'):
        data = request.form.to_dict(flat=False)
        # Добавляем поле 'cart': [] при регистрации
        session['temp_email'] = data['email'][0]
        session['temp_password'] = data['password'][0]
        session['temp_name'] = data['name'][0]
        session['temp_rights'] = data['rights'][0]
        session['auth'] = True
        return redirect(url_for('confirm_mail'), 302)
    return render_template('register.html', **commonkwargs(email))

def confirm_mail():
    email = getlogin(reset_auth=False)
    if (email != 'placeholder' or session['auth'] == False):
        return redirect(url_for('profile'), 302)
    if (request.method == 'GET'):
        code = []
        scode = ""
        for i in range(4):
            code.append(randint(0, 9))
            scode += str(code[i])
        session['auth_code'] = code
        if (Debug_mode):
            print(f'Ваш код: {scode}')
        else:
            sendmail(session['temp_email'], scode)
        return render_template('confirm_mail.html', **commonkwargs(email))
    if (request.method == 'POST'):
        data = request.form.to_dict(flat=False)
        for i in range(4):
            if session['auth_code'][i] != int(data[f'code{i}'][0]):
                return redirect(url_for('confirm_mail'), 302)
        setuser(session['temp_email'], {
            'password': session['temp_password'],
            'username': session['temp_name'],
            'description': "empty",
            'phone': "N/A",
            'rights': int(session['temp_rights']),
            'money': 0,
            'cart': [],
            'to_take': []
        })
        email = session['temp_email']
        setlogin(email)
        return redirect(url_for('profile'), 302)
    return redirect(url_for('register'), 302)

def profile():
    email = getlogin()
    if (email == 'placeholder'):
        return redirect(url_for('login'), 302)
    if (request.method == 'POST'):
        data = request.form.to_dict(flat=False)

        # 1. Выход
        if (data['commit_type'][0] == 'logout'):
            setlogin('')
            return redirect(url_for('landing'), 302)

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

        # 4. Обновление аллергии
        if (data['commit_type'][0] == 'update_health'):
            changes = getuser(email)
            changes['allergies'] = data.get('allergies', [])
            setuser(email, changes)

    return render_template('profile.html', **commonkwargs(email))
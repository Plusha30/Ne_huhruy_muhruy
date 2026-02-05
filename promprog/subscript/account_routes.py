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
        session['temp_last_name'] = data.get('last_name', [''])[0].strip()
        session['temp_first_name'] = data.get('first_name', [''])[0].strip()
        session['temp_middle_name'] = data.get('middle_name', [''])[0].strip()
        session['temp_name'] = f"{session['temp_last_name']} {session['temp_first_name']} {session['temp_middle_name']}".strip()
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

            # старое поле для совместимости
            'username': session.get('temp_name', ''),

            # новые поля
            'last_name': session.get('temp_last_name', ''),
            'first_name': session.get('temp_first_name', ''),
            'middle_name': session.get('temp_middle_name', ''),

            'description': "",
            'phone': "",
            'rights': int(session['temp_rights']),
            'money': 0,
            'cart': [],
            'to_take': [],
            'abonement': 'null',
            'last_used_hour': -1,
            'last_used_day': -1
        })
        session['temp_password'] = False
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

            # новые поля ФИО
            if 'last_name' in data and len(data['last_name']) > 0:
                changes['last_name'] = data['last_name'][0].strip()
            if 'first_name' in data and len(data['first_name']) > 0:
                changes['first_name'] = data['first_name'][0].strip()
            if 'middle_name' in data and len(data['middle_name']) > 0:
                changes['middle_name'] = data['middle_name'][0].strip()

            # поддержка старого username (склеиваем из новых)
            ln = changes.get('last_name', '').strip()
            fn = changes.get('first_name', '').strip()
            mn = changes.get('middle_name', '').strip()
            changes['username'] = f"{ln} {fn} {mn}".strip()

            # телефон/описание/класс — как было, но безопасно по ключам
            if 'phone' in data and len(data['phone']) > 0:
                changes['phone'] = data['phone'][0]
            if 'description' in data and len(data['description']) > 0:
                changes['description'] = data['description'][0]
            if 'class' in data and len(data['class']) > 0:
                changes['class'] = data['class'][0]

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

    user = getuser(email)  # или как у тебя принято
    kwargs = commonkwargs(email)

    kwargs['last_name'] = user.get('last_name', '')
    kwargs['first_name'] = user.get('first_name', '')
    kwargs['middle_name'] = user.get('middle_name', '')

    return render_template('profile.html', **kwargs)

from flask import Flask, render_template, request, redirect, url_for, send_file, session
from flask_session import Session
from subscript.filework import *
from subscript.reports import generate_users_report
from subscript.email import sendmail
from random import randint
import os
import secrets
from datetime import datetime

#global variables
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['SESSION_TYPE'] = 'filesystem'  # or 'redis', 'mongodb', etc.
app.config['SESSION_PERMANENT'] = False
app.config.update(
    SESSION_COOKIE_SECURE=True,    # HTTPS only
    SESSION_COOKIE_HTTPONLY=True,  # No JavaScript access
    SESSION_COOKIE_SAMESITE='Lax'  # CSRF protection
)
Session(app)
Debug_mode = True #эта переменная при состоянии True вместо отправки кода на почту выводит его в print()
                   #вызвано тем, что слишком много писем с mail.ru почты приводит к блокировке почты из-за спама
                   #(может уже нет, так как я написал в поддержку, но это не факт)

#session work
def getlogin(reset_auth = True):
    if session.get('user', '') == '':
        session['user'] = 'placeholder'
    if (reset_auth):
        session['auth'] = False
    return session['user']

def setlogin(email):
    session['user'] = email

# --- НОВАЯ ФУНКЦИЯ: ПОЛУЧЕНИЕ ОБЪЕКТОВ КОРЗИНЫ ---
def get_cart_objects(email):
    user = getuser(email)
    # Если пользователя нет или у него нет поля cart
    if not user or 'cart' not in user:
        return [], 0

    cart_ids = user['cart'] # Список ID, например ["1", "1", "3"]
    all_tovars = gettovarlist()

    cart_items = []
    total_price = 0

    for item_id in cart_ids:
        # Проверяем, существует ли такой товар в базе (на случай удаления)
        if item_id in all_tovars:
            item = all_tovars[item_id]
            cart_items.append(item)
            try:
                total_price += int(item['price'])
            except:
                pass

    return cart_items, total_price

#basic routes
@app.route('/')
def landing():
    return render_template('landing.html', **commonkwargs(getlogin()))

@app.route('/pricing')
def pricing():
    return render_template('pricing.html', **commonkwargs(getlogin()))

@app.route('/ultimate_dashboard')
def ultimate_dashboard():
    return render_template('super_dashboard.html', **commonkwargs(getlogin()))

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    email = getlogin()
    kwargs = commonkwargs(email)
    if (kwargs['rights'] != 1):
        return redirect(url_for('dashboard'))
    if (request.method == 'POST'):
        usernow = getuser(email)
        data = request.form.to_dict(flat=False)
        usernow['money'] += int(data['money'][0])
        setuser(email, usernow)
        return redirect(url_for('dashboard'))
    return render_template('payment.html', **kwargs)

@app.errorhandler(404)
def four04(name):
    return render_template('404.html', **commonkwargs(getlogin(reset_auth=False)))

# --- ОБНОВЛЕННЫЙ DASHBOARD С КОРЗИНОЙ ---
@app.route('/dashboard')
def dashboard():
    email = getlogin()
    kwargs = commonkwargs(email)
    if (kwargs['rights'] == 0):
        return render_template('dashboard.html', tovarlist=gettovarlist(), **kwargs)
    elif (kwargs['rights'] == 1):
        # Загружаем товары корзины и сумму для отображения
        cart_items, cart_total = get_cart_objects(email)
        kwargs['cart_items'] = cart_items
        kwargs['cart_total'] = cart_total
        return render_template('dashboard.html', tovarlist=gettovarlist(), takequeries=getuser(email)['to_take'], **kwargs)
    elif (kwargs['rights'] == 2):
        return render_template('dashboard.html', querylist=getquerylist("student_to_povar.json"), productlist=getquerylist("povar.json"), **kwargs) 
    elif (kwargs['rights'] == 3):
        return render_template('dashboard.html', **kwargs)

@app.route("/send_food/<id>")
def sendfood(id):
    email = getlogin()
    kwargs = commonkwargs(email)
    id = int(id)
    if (kwargs['rights'] != 2):
        return redirect(url_for('dashboard'))
    older = getquerylist("student_to_povar.json")
    for i in older:
        if (i['id'] == id):
            thatmail = i['userid']
            user = getuser(thatmail)
            user['to_take'].append(i)
            older = getquerylist("student_to_povar.json")
            newer = []
            for j in older:
                if j['id'] != id:
                    newer.append(j)
            setquerylist(name="student_to_povar.json", to=newer)
            setuser(thatmail, user)
            return redirect(url_for('dashboard'))
    return redirect(url_for('dashboard'))

@app.route("/got_food/<id>", methods=['POST'])
def gotfood(id):
    email = getlogin()
    kwargs = commonkwargs(email)
    id = int(id)
    if (kwargs['rights'] != 1):
        return redirect(url_for('dashboard'))
    user = getuser(email)
    new_to_take = []
    for i in user['to_take']:
        if (i['id'] != id):
            new_to_take.append(i)
    user['to_take'] = new_to_take
    setuser(email, user)
    return redirect(url_for('dashboard'))

@app.route("/update_inventory", methods=['POST'])
def updateinventory():
    email = getlogin()
    kwargs = commonkwargs(email)
    if (kwargs['rights'] != 2):
        return redirect(url_for('dashboard'))
    data = request.form.to_dict(flat=False)
    nowhave = getquerylist('povar.json')
    nowhave[data['product_name'][0]]['cnt'] = int(data['current_count'][0])
    setquerylist(name='povar.json', to=nowhave)
    return redirect(url_for('dashboard'))

# --- НОВЫЕ МАРШРУТЫ ДЛЯ КОРЗИНЫ ---
@app.route('/add_to_cart/<id>')
def add_to_cart(id):
    email = getlogin()
    if email == 'placeholder':
        return redirect(url_for('login'))

    user = getuser(email)
    # Если корзины нет (старый юзер), создаем список
    if 'cart' not in user:
        user['cart'] = []

    user['cart'].append(str(id)) # Добавляем ID товара в список
    setuser(email, user)

    return redirect(url_for('dashboard'))

@app.route('/buy_from_cart')
def buy_from_cart():
    email = getlogin()
    if email == 'placeholder':
        return redirect(url_for('login'))
    user = getuser(email)
    sum = 0
    for i in user['cart']:
        sum += gettovar(int(i))['price']
    if (sum > user['money']):
        return redirect(url_for('dashboard'))
    user['money'] -= sum
    dt = getquerylist("global.json")
    nowid = dt['total_queries']
    dt['total_queries'] += 1
    setquerylist(name="global.json", to=dt)
    tovarlist = gettovarlist()
    names = []
    for i in user['cart']:
        names.append(tovarlist[i]['name'])
    qu = getquerylist("student_to_povar.json")
    qu.append({
        "id": nowid,
        "products": names,
        "name": user['username'],
        "userid": email,
        "time": f'{datetime.now().hour}:{datetime.now().minute}'
    })
    setquerylist(name="student_to_povar.json", to=qu)
    setuser(email, user)
    return redirect(url_for('clear_cart'))

@app.route('/clear_cart')
def clear_cart():
    email = getlogin()
    if email != 'placeholder':
        user = getuser(email)
        user['cart'] = [] # Очищаем список
        setuser(email, user)
    return redirect(url_for('dashboard'))

@app.route('/object/<int:id>')
def object_detail(id):
    return render_template('object.html', id=id, **commonkwargs(getlogin()))

@app.route('/product/setcommentary/<id>', methods=['POST'])
def sendcommentary(id):
    product_data = gettovar(id)
    data = request.form.to_dict(flat=False)
    # Сохраняем отзыв вместе со звездами
    product_data['reviews'].append({'user': getuser(getlogin())["username"], "text": data['commentary'][0], "stars": int(data['stars'][0])})
    settovar(id, product_data)
    return redirect(f'/product/{id}', 302)

@app.route('/product/<id>', methods=['GET'])
def product_detail(id):
    product_data = gettovar(id)
    if not product_data:
        return render_template('404.html', **commonkwargs(getlogin()))
    return render_template('product.html', id=id, product=product_data, **commonkwargs(getlogin()))

#account system
@app.route('/login', methods=["GET", "POST"])
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

@app.route('/register', methods=["GET", "POST"])
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

@app.route('/confirm_mail', methods=['GET', 'POST'])
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

@app.route('/profile', methods=["GET", "POST"])
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
            # data.get('allergies', []) вернет список выбранных чекбоксов или пустой список
            changes['allergies'] = data.get('allergies', [])
            setuser(email, changes)

    return render_template('profile.html', **commonkwargs(email))

@app.route('/download_report')
def download_report():
    """
    Маршрут для скачивания отчета по пользователям
    """
    # Проверяем авторизацию
    email = getlogin()
    if email == 'placeholder':
        return redirect(url_for('login'), 302)
    
    # Проверяем права (только администраторы могут скачивать отчеты)
    user_data = getuser(email)
    if not user_data or user_data.get('rights', 0) < 2:
        return "Доступ запрещен. Требуются права модератора или администратора.", 403
    
    # Генерируем отчет
    users_dir = os.path.join(base_path, 'users')  # Путь к папке с пользователями
    excel_file = generate_users_report(users_dir)
    
    # Создаем имя файла с текущей датой и временем
    filename = f"отчет_пользователи_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.xlsx"
    
    # Отправляем файл
    return send_file(
        excel_file,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
#start
if __name__ == '__main__':
    app.run(port=5237, host="127.0.0.1", debug=True)
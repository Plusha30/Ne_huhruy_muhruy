from flask import Flask, render_template, request, redirect, url_for, make_response, send_file
from subscript.filework import *
from subscript.reports import generate_users_report  # Импортируем нашу функцию
import os
from datetime import datetime

#global variables
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

#cookie work
def getlogin(rq):
    if (rq.get('account')):
        return rq.get('account')
    return "placeholder"

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
    return render_template('landing.html', **commonkwargs(getlogin(request.cookies)))

@app.route('/pricing')
def pricing():
    return render_template('pricing.html', **commonkwargs(getlogin(request.cookies)))

@app.route('/ultimate_dashboard')
def ultimate_dashboard():
    return render_template('super_dashboard.html', **commonkwargs(getlogin(request.cookies)))

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    email = getlogin(request.cookies)
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
    return render_template('404.html', **commonkwargs(getlogin(request.cookies)))

# --- ОБНОВЛЕННЫЙ DASHBOARD С КОРЗИНОЙ ---
@app.route('/dashboard')
def dashboard():
    email = getlogin(request.cookies)
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
    email = getlogin(request.cookies)
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
    email = getlogin(request.cookies)
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
    email = getlogin(request.cookies)
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
    email = getlogin(request.cookies)
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
    email = getlogin(request.cookies)
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
    email = getlogin(request.cookies)
    if email != 'placeholder':
        user = getuser(email)
        user['cart'] = [] # Очищаем список
        setuser(email, user)
    return redirect(url_for('dashboard'))

@app.route('/object/<int:id>')
def object_detail(id):
    return render_template('object.html', id=id, **commonkwargs(getlogin(request.cookies)))

@app.route('/product/setcommentary/<id>', methods=['POST'])
def sendcommentary(id):
    product_data = gettovar(id)
    data = request.form.to_dict(flat=False)
    # Сохраняем отзыв вместе со звездами
    product_data['reviews'].append({'user': getuser(getlogin(request.cookies))["username"], "text": data['commentary'][0], "stars": int(data['stars'][0])})
    settovar(id, product_data)
    return redirect(f'/product/{id}', 302)

@app.route('/product/<id>', methods=['GET'])
def product_detail(id):
    product_data = gettovar(id)
    if not product_data:
        return render_template('404.html', **commonkwargs(getlogin(request.cookies)))
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
        # Добавляем поле 'cart': [] при регистрации
        setuser(data['email'][0], {
            'password': data['password'][0],
            'username': data['name'][0],
            'description': "empty",
            'phone': "N/A",
            'rights': int(data['rights'][0]),
            'money': 0,
            'cart': [],
            'to_take': []
        })
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
    email = getlogin(request.cookies)
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
#Выделенный файл для всех путей, связанных с учениками (корзина, получение заказов, оплата)

from flask import render_template, request, redirect, url_for, send_file, session
from subscript.filework import *
from subscript.account_system import *
from datetime import datetime

def get_cart_objects(email):
    user = getuser(email)
    if not user or 'cart' not in user:
        return [], 0
    cart_ids = user['cart']
    all_tovars = gettovarlist()
    cart_items = []
    total_price = 0
    for item_id in cart_ids:
        if item_id[0] in all_tovars:
            item = all_tovars[item_id[0]]
            cart_items.append([item, item_id[1]])
            try:
                total_price += int(item['price']) * item_id[1]
            except:
                pass
    return cart_items, total_price

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
    admin_qu = getquerylist('student_buys.json')
    for i in range(len(admin_qu)):
        if (admin_qu[i]['id'] == id):
            admin_qu[i]['isComplete'] = True
            break
    setquerylist(name='student_buys.json', to=admin_qu)
    return redirect(url_for('dashboard'))

def add_to_cart(id):
    email = getlogin()
    if email == 'placeholder':
        return redirect(url_for('login'))
    user = getuser(email)
    if 'cart' not in user:
        user['cart'] = []
    for i in range(len(user['cart'])):
        if (user['cart'][i][0] == str(id)):
            user['cart'][i][1] += 1
            setuser(email, user)
            return redirect(url_for('dashboard'))
    user['cart'].append([str(id), 1])
    setuser(email, user)
    return redirect(url_for('dashboard'))

def remove_from_cart(id):
    email = getlogin()
    if email == 'placeholder':
        return redirect(url_for('login'))
    user = getuser(email)
    if 'cart' not in user:
        user['cart'] = []
    for i in range(len(user['cart'])):
        if (user['cart'][i][0] == str(id)):
            user['cart'][i][1] -= 1
            if user['cart'][i][1] == 0:
                user['cart'].remove(user['cart'][i])
            setuser(email, user)
            return redirect(url_for('dashboard'))
    return redirect(url_for('dashboard'))

def clear_cart():
    email = getlogin()
    if email != 'placeholder':
        user = getuser(email)
        user['cart'] = []
        setuser(email, user)
    return redirect(url_for('dashboard'))

def buy_from_cart():
    email = getlogin()
    user = getuser(email)
    if email == 'placeholder' or user['rights'] != 1:
        return redirect(url_for('login'))
    sum = 0
    if (request.form.get('abon', 'False') == 'False'):
        for i in user['cart']:
            sum += gettovar(int(i[0]))['price'] * i[1]
        if (sum > user['money']):
            return redirect(url_for('dashboard'))
        user['money'] -= sum
    dt = getquerylist("global.json")
    nowid = dt['total_student_queries']
    dt['total_student_queries'] += 1
    setquerylist(name="global.json", to=dt)
    tovarlist = gettovarlist()
    names = []
    for i in user['cart']:
        if (i[1] == 1):
            names.append(tovarlist[i[0]]['name'])
        else:
            names.append(f"{tovarlist[i[0]]['name']} x{i[1]}")
    qu = getquerylist("student_to_povar.json")
    qu.append({
        "id": nowid,
        "products": names,
        "name": user['username'],
        "userid": email,
        "time": f'{str(datetime.now())[11:16]}',
        "date": f'{request.form.get("date", "Не указано")}'
    })
    setquerylist(name="student_to_povar.json", to=qu)
    admin_qu = getquerylist('student_buys.json')
    admin_qu.append({
        "id": nowid,
        "user": email,
        'class': user['class'],
        'phone': user['phone'],
        "money": sum,
        "what": names,
        "time": f'{datetime.now().hour}:{datetime.now().minute}',
        "order_date": f'{datetime.now().date()}',
        "date": f'{request.form.get("date", "Не указано")}',
        "isCooked": False,
        'isComplete': False
    })
    setquerylist(name="student_buys.json", to=admin_qu)
    if (request.form.get('abon', 'False') == 'True'):
        user['last_used_day'] = today_days()
        user['last_used_hour'] = today_hour()
    else:
        glob = getquerylist('global.json')
        glob['today_money'] += sum
        setquerylist(name='global.json', to=glob)
    user['history'].append({
        "products": names,
        "time": f'{str(datetime.now())[11:16]}',
        "order_date": f'{datetime.now().date()}',
        "date": f'{request.form.get("date", "Не указано")}',
        "money": sum
    })
    setuser(email, user)
    return redirect(url_for('clear_cart'))

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
        return redirect(session.get('pre_previous_page', '/dashboard'))
    return render_template('payment.html', **kwargs)

def pay():
    email = getlogin()
    kwargs = commonkwargs(email)
    if (kwargs['rights'] != 1):
        return redirect(url_for('dashboard'))
    cart_items, cart_total = get_cart_objects(email)
    kwargs['cart_items'] = cart_items
    kwargs['cart_total'] = cart_total
    user = getuser(email)
    cart_objects = user['cart']
    canAbonement = True
    for i in range(1): # Так как в python нет привычного инструментария из c++ с goto, то приходится импровизировать
        if (user['abonement'] == 'null'):
            canAbonement = False
            break
        abonementDays = getquerylist('abonement_conf.json')
        if (user['last_used_day'] == today_days()):
            if (user['last_used_hour'] <= today_hour() < abonementDays[user['abonement']][0]):
                canAbonement = False
                break
            if (abonementDays[user['abonement']][-1] < user['last_used_hour'] <= today_hour()):
                canAbonement = False
                break
            for i in range(0, len(abonementDays[user['abonement']]) - 1):
                if (abonementDays[user['abonement']][i] <= user['last_used_hour'] <= today_hour() < abonementDays[user['abonement']][i + 1]):
                    canAbonement = False
                    break
        if (len(cart_objects) > 2):
            canAbonement = False
            break
        cnt = 0
        for i in cart_objects:
            cnt += i[1]
        if (cnt > 2):
            canAbonement = False
            break
        drinks = 0
        not_drinks = 0
        tovarlist = gettovarlist()
        for i in cart_objects:
            if (tovarlist[i[0]]['category'] == 'Напитки'):
                drinks += 1
            else:
                not_drinks += 1
        if (drinks > 1 or not_drinks > 1):
            canAbonement = False
            break
    if (request.method == 'POST'):
        session['cart_date'] = request.form.to_dict(flat=False)['date'][0]
        return render_template('pay.html', now_date=request.form.to_dict(flat=False)['date'][0], canAbonement=canAbonement, tovarlist=gettovarlist(), takequeries=getuser(email)['to_take'], **kwargs)
    else:
        return render_template('pay.html', now_date=session.get('cart_date', '2000-01-01'), canAbonement=canAbonement, tovarlist=gettovarlist(), takequeries=getuser(email)['to_take'], **kwargs)

def setabonement(id):
    email = getlogin()
    if email != 'placeholder':
        user = getuser(email)
        user['abonement'] = id
        user['last_used_day'] = -1
        user['last_used_hour'] = -1
        setuser(email, user)
    return redirect(url_for('pricing'))
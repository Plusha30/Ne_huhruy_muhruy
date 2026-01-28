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
        if item_id in all_tovars:
            item = all_tovars[item_id]
            cart_items.append(item)
            try:
                total_price += int(item['price'])
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
    return redirect(url_for('dashboard'))

def add_to_cart(id):
    email = getlogin()
    if email == 'placeholder':
        return redirect(url_for('login'))
    user = getuser(email)
    if 'cart' not in user:
        user['cart'] = []
    user['cart'].append(str(id))
    setuser(email, user)
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
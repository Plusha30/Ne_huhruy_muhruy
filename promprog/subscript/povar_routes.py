#Выделенный файл для всех путей, связанных со страницей товаров

from flask import render_template, request, redirect, url_for, send_file, session
from subscript.filework import *
from subscript.account_system import *
from datetime import datetime

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
            admin_qu = getquerylist('student_buys.json')
            for i in range(len(admin_qu)):
                if (admin_qu[i]['id'] == id):
                    admin_qu[i]['isCooked'] = True
                    break
            setquerylist(name='student_buys.json', to=admin_qu)
            setuser(thatmail, user)
            return redirect(url_for('dashboard'))
    return redirect(url_for('dashboard'))

def buy_to_admin():
    email = getlogin()
    user = getuser(email)
    if email == 'placeholder' or user['rights'] != 2:
        return redirect(url_for('login'))
    data = request.form.to_dict(flat=False)
    dt = getquerylist("global.json")
    nowid = dt['total_povar_queries']
    dt['total_povar_queries'] += 1
    setquerylist(name="global.json", to=dt)
    suffix = gettovarlist()[data['prod'][0]]['suffix']
    price = gettovarlist()[data['prod'][0]]['povar_price']
    qu = getquerylist("povar_to_admin.json")
    qu.append({
        "id": nowid,
        "prod": gettovarlist()[data['prod'][0]]['name'],
        "volume": f'{data['volume'][0]} {suffix}',
        "volumeint": data['volume'][0],
        "person": user['username'],
        "when": f'{str(datetime.now())[11:16]}',
        "status": 0,
        "cost": f'{int(data['volume'][0]) * price} руб.'
    })
    setquerylist(name="povar_to_admin.json", to=qu)
    setuser(email, user)
    return redirect(url_for('clear_cart'))
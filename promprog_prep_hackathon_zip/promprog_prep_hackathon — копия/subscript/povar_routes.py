#Выделенный файл для всех путей, связанных со страницей товаров

from flask import render_template, request, redirect, url_for, send_file, session
from subscript.filework import *
from subscript.account_system import *

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
#Выделенный файл для всех путей, связанных со страницей товаров

from flask import render_template, request, redirect, url_for, send_file, session
from subscript.filework import *
from subscript.account_system import *

def set_admin_query():
    email = getlogin()
    user = getuser(email)
    if email == 'placeholder' or user['rights'] != 3:
        return redirect(url_for('login'))
    data = request.form.to_dict(flat=False)
    qu = getquerylist("povar_to_admin.json")
    for i in range(len(qu)):
        if (qu[i]['id'] == int(data['id'][0])):
            qu[i]['status'] = int(data['result'][0])
            break
    setquerylist(name="povar_to_admin.json", to=qu)
    return redirect(url_for('dashboard'), 302)
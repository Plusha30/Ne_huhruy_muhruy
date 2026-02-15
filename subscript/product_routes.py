#Выделенный файл для всех путей, связанных со страницей товаров

from flask import render_template, request, redirect, url_for, send_file, session
from subscript.filework import *
from subscript.account_system import *

def sendcommentary(id):
    product_data = gettovar(id)
    data = request.form.to_dict(flat=False)
    # Сохраняем отзыв вместе со звездами
    product_data['reviews'].append({'user': getuser(getlogin())["username"], "text": data['commentary'][0], "stars": int(data['stars'][0])})
    settovar(id, product_data)
    return redirect(f'/product/{id}', 302)

def product_detail(id):
    product_data = gettovar(id)
    if not product_data:
        return render_template('404.html', **commonkwargs(getlogin()))
    return render_template('product.html', id=id, product=product_data, **commonkwargs(getlogin()))
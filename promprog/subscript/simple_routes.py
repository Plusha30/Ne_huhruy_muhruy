#Выделенный файл для однострочных функций путей

from flask import render_template, request, redirect, url_for, send_file, session
from subscript.filework import *
from subscript.account_system import *

def landing():
    return render_template('landing.html', **commonkwargs(getlogin()))

def pricing():
    return render_template('pricing.html', **commonkwargs(getlogin()))

#def ultimate_dashboard():
#    return render_template('super_dashboard.html', **commonkwargs(getlogin()))

#def rand():
#    return render_template('some_random_forms.html', **commonkwargs(getlogin()))

#def rand1():
#    return render_template('some_random_forms_1.html', **commonkwargs(getlogin()))

#def rand2():
#    return render_template('some_random_forms_2.html', **commonkwargs(getlogin()))
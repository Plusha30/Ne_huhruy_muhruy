from flask import Flask, render_template, request, redirect, url_for, send_file, session
from flask_session import Session
from subscript.filework import *
from subscript.account_system import *
import subscript.simple_routes as simple_r
import subscript.account_routes as account_r
import subscript.student_routes as student_r
import subscript.product_routes as product_r
import subscript.povar_routes as povar_r
import subscript.admin_routes as admin_r
import os
import secrets
from datetime import datetime

#Configs
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = SESSION_PATH
app.config['SESSION_PERMANENT'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)
Session(app)

#simple_routes.py
app.add_url_rule('/', view_func=simple_r.landing)
app.add_url_rule('/pricing', view_func=simple_r.pricing)
#account_routes.py
app.add_url_rule('/login', view_func=account_r.login, methods=['GET', 'POST'])
app.add_url_rule('/register', view_func=account_r.register, methods=['GET', 'POST'])
app.add_url_rule('/confirm_mail', view_func=account_r.confirm_mail, methods=['GET', 'POST'])
app.add_url_rule('/profile', view_func=account_r.profile, methods=['GET', 'POST'])
app.add_url_rule('/login_wout_pass', view_func=account_r.login_wout_pass, methods=['GET', 'POST'])
app.add_url_rule('/confirm_login_mail', view_func=account_r.confirm_login_mail, methods=['GET', 'POST'])
#student_routes.py
app.add_url_rule("/got_food/<id>", view_func=student_r.gotfood, methods=['POST'])
app.add_url_rule('/add_to_cart/<id>', view_func=student_r.add_to_cart)
app.add_url_rule('/clear_cart', view_func=student_r.clear_cart)
app.add_url_rule('/buy_from_cart', view_func=student_r.buy_from_cart, methods=['POST'])
app.add_url_rule('/remove_from_cart/<id>', view_func=student_r.remove_from_cart)
app.add_url_rule('/payment', view_func=student_r.payment, methods=['GET', 'POST'])
app.add_url_rule('/pay', view_func=student_r.pay, methods=['GET', 'POST'])
app.add_url_rule('/setabonement/<id>', view_func=student_r.setabonement)
app.add_url_rule('/returnback', view_func=student_r.returnback)
#product_routes.py
app.add_url_rule('/product/setcommentary/<id>', view_func=product_r.sendcommentary, methods=['POST'])
app.add_url_rule('/product/<id>', view_func=product_r.product_detail, methods=['GET'])
#povar_routes.py
app.add_url_rule('/send_food/<id>', view_func=povar_r.sendfood)
app.add_url_rule('/buy_to_admin', view_func=povar_r.buy_to_admin, methods=['POST'])
#admin_routes.py
app.add_url_rule('/set_admin_query', view_func=admin_r.set_admin_query, methods=['POST'])
app.add_url_rule('/download_student_report', view_func=admin_r.download_student_report)
app.add_url_rule('/download_product_report', view_func=admin_r.download_product_report)
app.add_url_rule('/approve_balance_req/<id>', view_func=admin_r.approve_balance_req)
app.add_url_rule('/decline_balance_req/<id>', view_func=admin_r.decline_balance_req)

#@app.errorhandler(404)
#def four04(error):
#    return render_template('404.html', **commonkwargs(getlogin(reset_auth=False)))

#@app.errorhandler(Exception)
#def fatal_error(error):
#    return render_template('404.html', **commonkwargs(getlogin(reset_auth=False)))

@app.before_request
def store_current_page():
    if request.endpoint and request.endpoint != 'static':
        if (session.get('now_page', '/') != request.url):
            session['pre_previous_page'] = session.get('previous_page', '/dashboard')
            session['previous_page'] = session.get('now_page', '/dashboard')
            session['now_page'] = request.url

@app.route('/choose')
def choose():
    return render_template('choose.html', **commonkwargs(getlogin()))

@app.route('/dashboard')
def dashboard():
    email = getlogin()
    kwargs = commonkwargs(email)
    if (kwargs['rights'] == 0):
        return render_template('dashboard.html', tovarlist=gettovarlist(), **kwargs)
    elif (kwargs['rights'] == 1):
        cart_items, cart_total = student_r.get_cart_objects(email)
        kwargs['cart_items'] = cart_items
        kwargs['cart_total'] = cart_total
        return render_template('dashboard.html', tovarlist=gettovarlist(), takequeries=getuser(email)['to_take'], **kwargs)
    elif (kwargs['rights'] == 2):
        return render_template('dashboard.html', **kwargs, querylist=getquerylist("student_to_povar.json"),\
                                                           productlist=gettovarlist(),
                                                           toadmin=getquerylist("povar_to_admin.json"))
    elif (kwargs['rights'] == 3):
        balance_q = getquerylist('payment.json')
        balance_requests = []
        for i in balance_q:
            us = getuser(i['email'])
            balance_requests.append({
                "approved": i['approved'],
                "email": i['email'],
                "name": us['username'],
                "amount": i['amount'],
                "phone": us['phone'],
                "grade": us['class']
            })
        glob = getquerylist('global.json')
        today = glob['today']
        if (today != today_days()):
            glob['today'] = today_days()
            glob['today_money'] = 0
            setquerylist(name="global.json", to=glob)
        return render_template('dashboard.html', admin_money=glob['today_money'], **kwargs, toadmin=getquerylist("povar_to_admin.json"), balance_requests=balance_requests)


#start
if __name__ == '__main__':
    app.run(port=5237, host="127.0.0.1", debug=True)
from flask import Flask, render_template, request, redirect, url_for, send_file, session
from flask_session import Session
from subscript.filework import *
from subscript.reports import generate_users_report
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
app.config['SESSION_TYPE'] = 'filesystem'  # or 'redis', 'mongodb', etc.
app.config['SESSION_FILE_DIR'] = SESSION_PATH
app.config['SESSION_PERMANENT'] = False
app.config.update(
    SESSION_COOKIE_SECURE=True,    # HTTPS only
    SESSION_COOKIE_HTTPONLY=True,  # No JavaScript access
    SESSION_COOKIE_SAMESITE='Lax'  # CSRF protection
)
Session(app)

#simple_routes.py
app.add_url_rule('/', view_func=simple_r.landing)
app.add_url_rule('/pricing', view_func=simple_r.pricing)
#app.add_url_rule('/ultimate_dashboard', view_func=simple_r.ultimate_dashboard)
#account_routes.py
app.add_url_rule('/login', view_func=account_r.login, methods=['GET', 'POST'])
app.add_url_rule('/register', view_func=account_r.register, methods=['GET', 'POST'])
app.add_url_rule('/confirm_mail', view_func=account_r.confirm_mail, methods=['GET', 'POST'])
app.add_url_rule('/profile', view_func=account_r.profile, methods=['GET', 'POST'])
#student_routes.py
app.add_url_rule("/got_food/<id>", view_func=student_r.gotfood, methods=['POST'])
app.add_url_rule('/add_to_cart/<id>', view_func=student_r.add_to_cart)
app.add_url_rule('/clear_cart', view_func=student_r.clear_cart)
app.add_url_rule('/buy_from_cart', view_func=student_r.buy_from_cart)
app.add_url_rule('/payment', view_func=student_r.payment)
#product_routes.py
app.add_url_rule('/product/setcommentary/<id>', view_func=product_r.sendcommentary, methods=['POST'])
app.add_url_rule('/product/<id>', view_func=product_r.product_detail, methods=['GET'])
#povar_routes.py
app.add_url_rule('/send_food/<id>', view_func=povar_r.sendfood)
app.add_url_rule('/update_inventory', view_func=povar_r.updateinventory, methods=['POST'])
app.add_url_rule('/buy_to_admin', view_func=povar_r.buy_to_admin, methods=['POST'])
#admin_routes.py
app.add_url_rule('/set_admin_query', view_func=admin_r.set_admin_query, methods=['POST'])

@app.errorhandler(404)
def four04():
    return render_template('404.html', **commonkwargs(getlogin(reset_auth=False)))

#@app.errorhandler(Exception)
#def four04(error):
#    return render_template('404.html', **commonkwargs(getlogin(reset_auth=False)))

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
                                                           productlist=getquerylist("povar.json"),
                                                           toadmin=getquerylist("povar_to_admin.json"))                 
    elif (kwargs['rights'] == 3):
        return render_template('dashboard.html', **kwargs, toadmin=getquerylist("povar_to_admin.json"))

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
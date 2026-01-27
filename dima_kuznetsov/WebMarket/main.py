from flask import Flask, render_template, request, redirect, url_for, session
from product_utils import *
from user_utils import *


app = Flask(__name__)
app.secret_key = 'aboba'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/category/<category>')
def create_category_page(category):
    products = get_products_by_category(category, False)
    return render_template('category.html', 
                         products=products,
                         category_id=category,
                         category_name=CATEGORIES[category]['name'],
                         category_icon=CATEGORIES[category]['icon'])


def auth_check():
    if 'user_email' not in session:
        return False, {}
    email = session['user_email']
    user_data = get_user(email)
    if not user_data:
        session.pop('user_email', None)
        return False, {}
    
    return True, user_data


@app.route('/profile')
def profile():
    # проверка прав на аккаунт
    valid, user_data = auth_check()
    if not valid:
        return redirect(url_for('login'))
    
    return render_template("profile.html", user=user_data)


@app.route('/compare/<category>')
def compare_category(category):
    products, all_specs = get_products_by_category(category, True)
    return render_template('compare_category.html', 
                         category=category, 
                         products=products, 
                         all_specs=sorted(all_specs),
                         category_name=CATEGORIES[category]['name'])


@app.route('/product/<product_id>')
def product_detail(product_id):
    template_data = product_page_template_data(product_id)
    if (template_data == 404):
        return "Товар не найден", 404
    else:
        return render_template('product.html', **template_data)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    elif request.method == 'POST':
        data, files = request.form, request.files
        is_valid, message = validate_pass_and_email(data['email'], data['password'], data['confirm_password'])
        if not is_valid:
            return render_template("register.html", error=message)
        
        save_user(data, files.get('avatar'))
        return render_template("success_la.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    elif request.method == 'POST':
        data = request.form
        success, result = authenticate_user(data['email'], data['password'])
        if success:
            # сохраняем email в сессии
            session['user_email'] = data['email']
            return redirect(url_for('profile'))
        else:
            return render_template("login.html", error=result)
    

@app.route('/add-product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'GET':
        return render_template("add_product.html")
    elif request.method == 'POST':
        data, files = request.form, request.files
        for key in data:
            print(key, "->", data[key])
        create_new_product_file(data, files)
        return redirect(url_for('index'))
    

@app.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    # проверка авторизации
    valid, user_data = auth_check()
    if not valid:
        return redirect(url_for('login'))
    
    if request.method == 'GET':
        return render_template("edit_profile.html", user=user_data)
    elif request.method == 'POST':
        data, files = request.form, request.files
        success, message = update_user(user_data['email'], data, files.get('avatar'))

        if success:
            return redirect(url_for('profile'))
        else:
            return render_template("edit_profile.html", user=user_data, error=message)
        

@app.route('/logout')
def logout():
    session.pop('user_email', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8080)
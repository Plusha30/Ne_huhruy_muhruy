from flask import Flask, render_template, send_from_directory, request, redirect, url_for, session, flash
import os
import glob
import hashlib
import json
from datetime import datetime
import secrets
from werkzeug.utils import secure_filename  # Добавьте эту строку
import uuid  # Добавьте эту строку для генерации уникальных имен файлов

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Создаем папки если их нет
os.makedirs('products', exist_ok=True)
os.makedirs('data', exist_ok=True)
os.makedirs('static/css', exist_ok=True)
os.makedirs('static/images', exist_ok=True)
os.makedirs('static/uploads/avatars', exist_ok=True)
os.makedirs('static/uploads/products', exist_ok=True)


def allowed_file(filename):
    """Проверка допустимых расширений файлов"""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def save_uploaded_file(file, folder):
    """Сохранение загруженного файла"""
    if file and allowed_file(file.filename):
        # Генерируем уникальное имя файла
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"

        # Сохраняем файл
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], folder, unique_filename)
        file.save(file_path)

        # Возвращаем относительный путь для использования в HTML
        return f"uploads/{folder}/{unique_filename}"
    return None


# ==================== ФУНКЦИИ ДЛЯ РАБОТЫ С ПОЛЬЗОВАТЕЛЯМИ ====================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def load_users():
    try:
        if os.path.exists('data/users.json'):
            with open('data/users.json', 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки пользователей: {e}")
    return {}


def save_users(users):
    try:
        with open('data/users.json', 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Ошибка сохранения пользователей: {e}")
        return False


def create_user(username, password, email, avatar=None):
    users = load_users()

    if username in users:
        return False, "Пользователь с таким именем уже существует"

    # Если аватар не указан, используем дефолтный
    if not avatar:
        avatar = 'images/default_avatar.jpg'

    users[username] = {
        'password_hash': hash_password(password),
        'email': email,
        'avatar': avatar,
        'created_at': datetime.now().isoformat(),
        'favorites': [],
        'cart': [],
        'compare': []
    }

    if save_users(users):
        return True, "Пользователь успешно создан"
    else:
        return False, "Ошибка сохранения пользователя"


def authenticate_user(username, password):
    users = load_users()

    if username not in users:
        return False, "Пользователь не найден"

    if users[username]['password_hash'] != hash_password(password):
        return False, "Неверный пароль"

    return True, "Успешная авторизация"


def update_user(username, email=None, avatar=None):
    users = load_users()

    if username not in users:
        return False, "Пользователь не найден"

    if email:
        users[username]['email'] = email

    if avatar:
        users[username]['avatar'] = avatar

    if save_users(users):
        return True, "Данные обновлены"
    else:
        return False, "Ошибка обновления данных"


def get_user_info(username):
    users = load_users()
    return users.get(username)


# ==================== ФУНКЦИИ ДЛЯ РАБОТЫ С ТОВАРАМИ ====================

def load_products():
    products = []

    if not os.path.exists('products'):
        os.makedirs('products')
        print("Создана папка products. Добавьте туда txt файлы с товарами.")
        return products

    product_files = glob.glob('products/*.txt')

    for file_path in product_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]

            if len(lines) >= 15:
                product = {
                    'id': lines[0],
                    'name': lines[1],
                    'category': lines[2],
                    'category_name': lines[3],
                    'image': lines[4],
                    'year': lines[5],
                    'manufacturer': lines[6],
                    'price': int(lines[7]) if lines[7].isdigit() else 0,
                    'description': lines[8],
                    'features': lines[9],
                    'dimensions': lines[10],
                    'weight': lines[11],
                    'screen': lines[12],
                    'voltage': lines[13],
                    'components': lines[14],
                    'in_stock': 2
                }
                products.append(product)
            else:
                print(f"Пропущен {file_path}: недостаточно данных")

        except Exception as e:
            print(f"Ошибка в файле {file_path}: {str(e)}")

    return products


def save_product(product_data, image_file=None):
    try:
        product_id = product_data['name'].lower().replace(' ', '_').replace('(', '').replace(')', '')
        counter = 1
        original_id = product_id
        while os.path.exists(f'products/{product_id}.txt'):
            product_id = f"{original_id}_{counter}"
            counter += 1

        # Обработка загруженного изображения
        image_path = product_data.get('image', 'images/products/default.jpg')
        if image_file and allowed_file(image_file.filename):
            uploaded_image = save_uploaded_file(image_file, 'products')
            if uploaded_image:
                image_path = uploaded_image

        content = [
            product_id,
            product_data['name'],
            product_data['category'],
            product_data['category_name'],
            image_path,
            product_data['year'],
            product_data['manufacturer'],
            product_data['price'],
            product_data['description'],
            product_data['features'],
            product_data['dimensions'],
            product_data['weight'],
            product_data['screen'],
            product_data['voltage'],
            product_data['components']
        ]

        with open(f'products/{product_id}.txt', 'w', encoding='utf-8') as f:
            for line in content:
                f.write(str(line) + '\n')

        print(f"Товар сохранен: {product_id}.txt")
        return True
    except Exception as e:
        print(f"Ошибка сохранения товара: {e}")
        return False


def filter_products(products, filters):
    # ... остальной код функции без изменений ...
    # (оставляем как было)

    filtered_products = products.copy()

    # Фильтр по поисковому запросу
    search_query = filters.get('search')
    if search_query:
        search_query = search_query.lower()
        filtered_products = [p for p in filtered_products if
                             search_query in p['name'].lower() or
                             search_query in p['description'].lower() or
                             search_query in p['manufacturer'].lower()]

    # Фильтр по категории
    category = filters.get('category')
    if category:
        filtered_products = [p for p in filtered_products if p['category'] == category]

    # Фильтр по цене
    min_price = filters.get('min_price')
    max_price = filters.get('max_price')
    if min_price and min_price.isdigit():
        filtered_products = [p for p in filtered_products if p['price'] >= int(min_price)]
    if max_price and max_price.isdigit():
        filtered_products = [p for p in filtered_products if p['price'] <= int(max_price)]

    # Фильтр по брендам
    selected_brands = filters.getlist('brand')
    if selected_brands:
        filtered_products = [p for p in filtered_products if p['manufacturer'] in selected_brands]

    # Фильтр по наличию
    in_stock_only = filters.get('in_stock')
    if in_stock_only:
        filtered_products = [p for p in filtered_products if p['in_stock'] > 0]

    # Фильтр по году
    min_year = filters.get('min_year')
    max_year = filters.get('max_year')
    if min_year and min_year.isdigit():
        filtered_products = [p for p in filtered_products if int(p['year']) >= int(min_year)]
    if max_year and max_year.isdigit():
        filtered_products = [p for p in filtered_products if int(p['year']) <= int(max_year)]

    # Фильтр по состоянию
    condition_filter = filters.get('condition')
    if condition_filter:
        if condition_filter == 'excellent':
            filtered_products = [p for p in filtered_products if p['price'] > 80000]
        elif condition_filter == 'good':
            filtered_products = [p for p in filtered_products if 40000 <= p['price'] <= 80000]

    # Сортировка
    sort_by = filters.get('sort')
    if sort_by:
        if sort_by == 'price_asc':
            filtered_products.sort(key=lambda x: x['price'])
        elif sort_by == 'price_desc':
            filtered_products.sort(key=lambda x: x['price'], reverse=True)
        elif sort_by == 'year_desc':
            filtered_products.sort(key=lambda x: int(x['year']), reverse=True)

    return filtered_products


# ==================== МАРШРУТЫ ====================

@app.route('/')
def index():
    products = load_products()
    filtered_products = filter_products(products, request.args)
    available_brands = list(set(p['manufacturer'] for p in products))

    years = [int(p['year']) for p in products if p['year'].isdigit()]
    min_year = min(years) if years else 1970
    max_year = max(years) if years else 2024

    return render_template('index.html',
                           products=filtered_products,
                           all_products=products,
                           available_brands=available_brands,
                           min_year=min_year,
                           max_year=max_year)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = request.form.get('email')
        avatar_file = request.files.get('avatar')

        # Валидация
        if not username or not password or not email:
            flash('Все поля обязательны для заполнения', 'error')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Пароли не совпадают', 'error')
            return redirect(url_for('register'))

        if len(password) < 6:
            flash('Пароль должен содержать минимум 6 символов', 'error')
            return redirect(url_for('register'))

        # Обработка загруженной аватарки
        avatar_path = None
        if avatar_file and allowed_file(avatar_file.filename):
            avatar_path = save_uploaded_file(avatar_file, 'avatars')
        elif avatar_file and not allowed_file(avatar_file.filename):
            flash('Недопустимый формат файла для аватарки', 'error')
            return redirect(url_for('register'))

        # Создаем пользователя
        success, message = create_user(username, password, email, avatar_path)

        if success:
            session['username'] = username
            flash('Регистрация прошла успешно!', 'success')
            return redirect(url_for('account'))
        else:
            flash(message, 'error')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Введите имя пользователя и пароль', 'error')
            return redirect(url_for('login'))

        success, message = authenticate_user(username, password)

        if success:
            session['username'] = username
            flash('Вход выполнен успешно!', 'success')
            return redirect(url_for('account'))
        else:
            flash(message, 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('index'))


@app.route('/account')
def account():
    if 'username' not in session:
        flash('Для доступа к личному кабинету необходимо войти в систему', 'error')
        return redirect(url_for('login'))

    user_info = get_user_info(session['username'])
    if not user_info:
        flash('Пользователь не найден', 'error')
        session.pop('username', None)
        return redirect(url_for('login'))

    return render_template('account.html', user=user_info, username=session['username'])


@app.route('/account/edit', methods=['GET', 'POST'])
def edit_account():
    if 'username' not in session:
        return redirect(url_for('login'))

    user_info = get_user_info(session['username'])

    if request.method == 'POST':
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        avatar_file = request.files.get('avatar')

        # Обработка загруженной аватарки
        avatar_path = None
        if avatar_file and avatar_file.filename:
            if allowed_file(avatar_file.filename):
                avatar_path = save_uploaded_file(avatar_file, 'avatars')
            else:
                flash('Недопустимый формат файла для аватарки', 'error')
                return redirect(url_for('edit_account'))

        # Проверяем текущий пароль если меняем пароль
        if new_password:
            if not current_password:
                flash('Для смены пароля введите текущий пароль', 'error')
                return redirect(url_for('edit_account'))

            # Проверяем текущий пароль
            success, message = authenticate_user(session['username'], current_password)
            if not success:
                flash('Неверный текущий пароль', 'error')
                return redirect(url_for('edit_account'))

            if new_password != confirm_password:
                flash('Новые пароли не совпадают', 'error')
                return redirect(url_for('edit_account'))

            # Обновляем пароль
            users = load_users()
            users[session['username']]['password_hash'] = hash_password(new_password)
            save_users(users)
            flash('Пароль успешно изменен', 'success')

        # Обновляем email
        if email and email != user_info['email']:
            update_user(session['username'], email=email)
            flash('Email успешно обновлен', 'success')

        # Обновляем аватарку
        if avatar_path:
            update_user(session['username'], avatar=avatar_path)
            flash('Аватарка успешно обновлена', 'success')

        return redirect(url_for('account'))

    return render_template('edit_account.html', user=user_info, username=session['username'])


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        # Получаем данные формы
        product_data = {
            'name': request.form.get('name', ''),
            'category': request.form.get('category', ''),
            'category_name': request.form.get('category_name', ''),
            'image': request.form.get('image', 'images/products/default.jpg'),
            'year': request.form.get('year', ''),
            'manufacturer': request.form.get('manufacturer', ''),
            'price': request.form.get('price', '0'),
            'description': request.form.get('description', ''),
            'features': request.form.get('features', ''),
            'dimensions': request.form.get('dimensions', ''),
            'weight': request.form.get('weight', ''),
            'screen': request.form.get('screen', ''),
            'voltage': request.form.get('voltage', ''),
            'components': request.form.get('components', '')
        }

        # Получаем файл изображения
        image_file = request.files.get('image_file')

        if save_product(product_data, image_file):
            flash('Товар успешно добавлен', 'success')
            return redirect(url_for('add_product'))
        else:
            flash('Ошибка при сохранении товара', 'error')

    return render_template('add_product.html')


@app.route('/product/<product_id>')
def product_page(product_id):
    products = load_products()
    product = next((p for p in products if p['id'] == product_id), None)

    if product:
        similar_products = [p for p in products
                            if p['category'] == product['category']
                            and p['id'] != product['id']][:3]

        return render_template('product_template.html',
                               product=product,
                               similar_products=similar_products)
    else:
        return render_template('404.html'), 404


# ==================== ФУНКЦИИ ДЛЯ СРАВНЕНИЯ ====================

def get_compare_list(username):
    users = load_users()
    if username in users:
        if 'compare' not in users[username]:
            users[username]['compare'] = []
            save_users(users)
        return users[username]['compare']
    return []


def add_to_compare(username, product_id):
    users = load_users()
    if username in users:
        if 'compare' not in users[username]:
            users[username]['compare'] = []
        if product_id not in users[username]['compare']:
            users[username]['compare'].append(product_id)
            save_users(users)
            return True
    return False


def remove_from_compare(username, product_id):
    users = load_users()
    if username in users and 'compare' in users[username]:
        if product_id in users[username]['compare']:
            users[username]['compare'].remove(product_id)
            save_users(users)
            return True
    return False


def clear_compare(username):
    users = load_users()
    if username in users:
        users[username]['compare'] = []
        save_users(users)
        return True
    return False


@app.route('/compare', endpoint='compare')
def compare_page():
    compare_ids = []
    if 'username' in session:
        compare_ids = get_compare_list(session['username'])

    products = load_products()
    compare_products = []
    for product in products:
        if product['id'] in compare_ids:
            compare_products.append(product)

    return render_template('compare.html',
                           compare_products=compare_products)


@app.route('/add_to_compare/<product_id>')
def add_to_compare_route(product_id):
    if 'username' not in session:
        flash('Для добавления в сравнение необходимо войти в систему', 'error')
        return redirect(url_for('login'))

    success = add_to_compare(session['username'], product_id)
    if success:
        flash('Товар добавлен в сравнение', 'success')
    else:
        flash('Товар уже в списке сравнения', 'info')

    return redirect(request.referrer or url_for('index'))


@app.route('/remove_from_compare/<product_id>')
def remove_from_compare_route(product_id):
    if 'username' not in session:
        flash('Для управления сравнением необходимо войти в систему', 'error')
        return redirect(url_for('login'))

    success = remove_from_compare(session['username'], product_id)
    if success:
        flash('Товар удален из сравнения', 'success')

    return redirect(url_for('compare_page'))


@app.route('/clear_compare')
def clear_compare_route():
    if 'username' not in session:
        flash('Для управления сравнением необходимо войти в систему', 'error')
        return redirect(url_for('login'))

    success = clear_compare(session['username'])
    if success:
        flash('Список сравнения очищен', 'success')
    else:
        flash('Ошибка при очистке сравнения', 'error')

    return redirect(url_for('compare'))


@app.route('/advice')
def advice_page():
    return render_template('advice.html')


@app.route('/<page_name>')
def show_page(page_name):
    if not page_name.endswith('.html'):
        page_name += '.html'

    category_map = {
        'classic.html': 'classic',
        'pinball.html': 'pinball',
        'racing.html': 'racing',
        'advice.html': 'advice'
    }

    if page_name in category_map:
        if page_name == 'advice.html':
            return render_template(page_name)

        products = load_products()
        category_products = [p for p in products if p['category'] == category_map[page_name]]

        filtered_products = filter_products(category_products, request.args)
        available_brands = list(set(p['manufacturer'] for p in category_products))

        years = [int(p['year']) for p in category_products if p['year'].isdigit()]
        min_year = min(years) if years else 1970
        max_year = max(years) if years else 2024

        category_name = category_products[0]['category_name'] if category_products else category_map[page_name]

        return render_template(page_name,
                               products=filtered_products,
                               all_products=category_products,
                               category_name=category_name,
                               available_brands=available_brands,
                               min_year=min_year,
                               max_year=max_year,
                               current_filters=request.args)

    return render_template('404.html'), 404


@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)


@app.route('/images/<path:filename>')
def image_files(filename):
    try:
        return send_from_directory('static/images', filename)
    except:
        return send_from_directory('templates/images', filename)


@app.route('/css/<path:filename>')
def css_files(filename):
    return send_from_directory('static/css', filename)


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.context_processor
def inject_user():
    if 'username' in session:
        users = load_users()
        username = session['username']

        compare_count = 0
        if username in users and 'compare' in users[username]:
            compare_list = users[username]['compare']
            if isinstance(compare_list, list):
                compare_count = len(compare_list)

        return {
            'current_user': username,
            'compare_count': compare_count
        }
    return {
        'current_user': None,
        'compare_count': 0
    }


if __name__ == '__main__':
    if not os.path.exists('data/users.json'):
        with open('data/users.json', 'w', encoding='utf-8') as f:
            json.dump({}, f)

    print("=" * 50)
    print("RetroArcade Server Starting...")
    print("=" * 50)

    products = load_products()
    print(f"Всего загружено товаров: {len(products)}")

    users = load_users()
    if not users:
        create_user('test', 'test123', 'test@example.com')
        print("Создан тестовый пользователь: test / test123")

    print("=" * 50)
    print("Сервер запущен: http://127.0.0.1:5000")
    print("=" * 50)

    app.run(debug=True, port=5000)
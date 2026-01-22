from flask import Flask, render_template, request, redirect, url_for
import os
import json
import pathlib
import shutil

# some global variables

global tovars_data
global users_base
tovars_data = {}
users_base = {}
email = 'placeholder'
base_path = pathlib.Path(__file__).parent.resolve()

# --- БАЗА ДАННЫХ ТОВАРОВ (UI KIT) ---
# РЕДАКТИРУЙ ЭТОТ СЛОВАРЬ, ЧТОБЫ МЕНЯТЬ ДАННЫЕ НА СТРАНИЦАХ ТОВАРОВ
products_db = {
    1: {
        "name": "Smart Watch Series 7",
        "category": "Electronics",
        "price": 299,
        "old_price": 399,
        "badge": "Sale -20%",
        "rating": 4.8,
        "reviews_count": 1204,
        "description": "Monitor your health, track your workouts, and stay connected. Now with 48-hour battery life and titanium case.",
        "main_icon": "bi-smartwatch",
        "gallery": ["bi-smartwatch", "bi-watch", "bi-cpu", "bi-play-circle"],
        "specs": {
            "Display": "1.9 inch OLED",
            "Battery": "Up to 48 hours",
            "Connectivity": "Bluetooth 5.3, Wi-Fi",
            "Waterproof": "Yes, 50m"
        },
        "reviews": [
            {"user": "John Doe", "text": "Amazing battery life!"},
            {"user": "Sarah Smith", "text": "Best watch I ever had."}
        ]
    },
    2: {
        "name": "Leather Travel Bag",
        "category": "Accessories",
        "price": 120,
        "old_price": 150,
        "badge": "New Arrival",
        "rating": 4.9,
        "reviews_count": 85,
        "description": "Handcrafted from genuine Italian leather. Spacious, durable, and perfect for weekend getaways.",
        "main_icon": "bi-handbag",
        "gallery": ["bi-handbag", "bi-wallet", "bi-briefcase", "bi-gem"],
        "specs": {
            "Material": "Genuine Leather",
            "Volume": "45 Liters",
            "Warranty": "5 Years",
            "Color": "Brown / Black"
        },
        "reviews": [
            {"user": "Mike Ross", "text": "Very stylish and robust."},
            {"user": "Elena K.", "text": "Fits everything I need."}
        ]
    },
    3: {
        "name": "Pro Headphones X",
        "category": "Audio",
        "price": 199,
        "old_price": 249,
        "badge": "Best Seller",
        "rating": 4.7,
        "reviews_count": 432,
        "description": "Active noise cancelling, studio-quality sound, and plush ear cushions for all-day comfort.",
        "main_icon": "bi-headphones",
        "gallery": ["bi-headphones", "bi-music-note-beamed", "bi-soundwave", "bi-bluetooth"],
        "specs": {
            "Type": "Over-Ear",
            "ANC": "Active Noise Cancelling",
            "Battery": "30 hours",
            "Jack": "3.5mm included"
        },
        "reviews": [
            {"user": "Audiophile99", "text": "Soundstage is incredible."},
            {"user": "Gamer_One", "text": "No lag in games."}
        ]
    }
}

# basic functions for site render

def return_image(path, placeholder):
    full_path = f"{base_path}/static/images/{path}.jpg"
    if os.path.exists(full_path):
        return f'images/{path}.jpg'
    else:
        return f'images/common/{placeholder}.jpg'

def commonkwargs(kwargs):
    if (email in users_base):
        return kwargs | {'username': users_base[email][1], 'userimg': return_image(f'users/{email}', 'user_placeholder')}
    else:
        return kwargs | {'username': 'Log in', 'userimg': return_image(f'users/{email}', 'user_placeholder')}

#read data about tovars i think (maybe delete)

def getTovarsData(folder_path):
    total = dict()
    if not os.path.exists(folder_path):
        return {}
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            d = json.loads(content)
            total |= d
            for i in d:
                d[i] |= {"tovars": {}}
            way = f"{base_path}/tovars/{filename[:-5]}"
            if os.path.exists(way):
                for tovar in os.listdir(way):
                    tovar_path = os.path.join(way, tovar)
                    with open(tovar_path, 'r', encoding='utf-8') as f1:
                        info = f1.read()
                        tov = json.loads(info)
                        for i in d:
                            d[i]["tovars"] |= tov
    return total

#app

app = Flask(__name__)
app.secret_key = 'hackathon_key'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

#routes

@app.route('/')
def landing():
    return render_template('landing.html', **commonkwargs({}))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', **commonkwargs({}))

@app.route('/object/<int:id>')
def object_detail(id):
    return render_template('object.html', id=id, **commonkwargs({}))

# --- ИЗМЕНЕННЫЙ МАРШРУТ (ДИНАМИЧЕСКИЕ ТОВАРЫ) ---
@app.route('/product/<int:id>')
def product_detail(id):
    # Берем данные из словаря products_db
    product_data = products_db.get(id)

    # Если товара нет (например, id=999), показываем ошибку
    if not product_data:
        return render_template('404.html', **commonkwargs({}))

    # Передаем данные в шаблон как переменную product
    return render_template('product.html', id=id, product=product_data, **commonkwargs({}))
# -----------------------------------------------

@app.route('/login', methods=["GET", "POST"])
def login():
    if (request.method == 'POST'):
        data = request.form.to_dict(flat=False)
        input_email = data['email'][0]
        if input_email in users_base: # Исправил data['email'][0] на input_email для читаемости
            global email
            email = input_email
            return redirect(url_for('profile'), 301)
        else:
            pass
    return render_template('login.html', **commonkwargs({}))

@app.route('/register', methods=["GET", "POST"])
def register():
    if (request.method == 'POST'):
        data = request.form.to_dict(flat=False)
        users_base[data['email'][0]] = [data['password'][0], data['name'][0]]
        with open(f"{base_path}/users_base.json", 'w', encoding='utf-8') as f:
            f.write(json.dumps(users_base, indent=4))
        global email
        email = data['email'][0]
        return redirect(url_for('profile'), 301)
    return render_template('register.html', **commonkwargs({}))

@app.route('/profile')
def profile():
    return render_template('profile.html', **commonkwargs({}))

@app.route('/pricing')
def pricing():
    return render_template('pricing.html', **commonkwargs({}))

@app.errorhandler(404)
def four04(name):
    return render_template('404.html', **commonkwargs({}))

def readfiles():
    global tovars_data
    global users_base
    global base_path
    users_path = f"{base_path}/users_base.json"
    if not os.path.exists(users_path):
        with open(users_path, 'w', encoding='utf-8') as f:
            f.write("{}")
    tovars_data = getTovarsData(f"{base_path}/categories")
    with open(users_path, 'r', encoding='utf-8') as f:
        info = f.read()
        if info:
            users_base = json.loads(info)
        else:
            users_base = {}

if __name__ == '__main__':
    readfiles()
    app.run(port=5237, host="127.0.0.1", debug=True)
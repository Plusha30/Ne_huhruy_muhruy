from flask import Flask, render_template
import os
import json
import pathlib
import shutil

app = Flask(__name__)
app.secret_key = 'hackathon_key'
tovars_data = {}
users_base = {}
email = 'placeholder'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

def return_image(path, placeholder):
    if os.path.exists(f"{pathlib.Path(__file__).parent.resolve()}/static/images/{path}.jpg"):
        return f'images/{path}.jpg'
    else:
        return f'images/common/{placeholder}.jpg'

def commonkwargs(kwargs):
    if (email in users_base):
        return kwargs | {'username': users_base[email][1], 'userimg': return_image(f'users/{email}', 'user_placeholder')}
    else:
        return kwargs | {'username': 'Вы', 'userimg': return_image(f'users/{email}', 'user_placeholder')}

@app.route('/')
def landing():
    return render_template('landing.html', **commonkwargs({}))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/object/<int:id>')
def object_detail(id):
    return render_template('object.html', id=id)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

# НОВЫЙ МАРШРУТ
@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/pricing')
def pricing():
    # ТЕПЕРЬ МЫ ИСПОЛЬЗУЕМ НОВЫЙ ШАБЛОН
    return render_template('pricing.html')

if __name__ == '__main__':
    app.run(debug=True, port="5723")

from flask import Flask, render_template

app = Flask(__name__)
app.secret_key = 'hackathon_key'

@app.route('/')
def landing():
    return render_template('landing.html')

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
    app.run(debug=True)

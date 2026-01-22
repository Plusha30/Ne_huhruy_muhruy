from flask import Flask, render_template

app = Flask(__name__)
app.secret_key = 'hackathon_key'

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Маршрут для страницы объекта
@app.route('/object/<int:id>')
def object_detail(id):
    return render_template('object.html', id=id)

# --- ИСПРАВЛЕНИЕ ОШИБКИ ЗДЕСЬ ---
# Мы добавили этот маршрут, так как он мог вызываться в шаблонах
@app.route('/pricing')
def pricing():
    # Если отдельного шаблона нет, покажем лендинг или дашборд
    return render_template('landing.html')

@app.route('/login')
def login():
    return render_template('dashboard.html')

@app.route('/register')
def register():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
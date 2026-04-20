from flask import Flask, render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'twoj_bardzo_tajny_klucz'

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return 'Strona główna. Idź do <a href="/login">logowania</a>.'

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        
        new_user = User(username=username, password=hashed_pw)
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        except Exception:
            db.session.rollback()
            return "Błąd: Użytkownik prawdopodobnie już istnieje."
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            return f"Witaj {username}! Zalogowano pomyślnie."
        else:
            return "Błędne dane logowania. <a href='/login'>Spróbuj ponownie</a>"
            
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
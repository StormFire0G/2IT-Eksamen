from flask import Flask, render_template, url_for, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mariadb+pymysql://brukernavn:passord@127.0.0.1/user_database'
app.config['SECRET_KEY'] = 'passord'
db = SQLAlchemy(app)
Bcrypt = Bcrypt(app)

# Gjør at flask og log inn kan sammarbeide
login = LoginManager()
login.init_app(app)
login.login_view = 'login'

# Modell for bruker
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # Er admin?

# Hindrer at andre kan logge inn som admin
@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Custom admin-hovedside (hindrer tilgang til /admin for ikke-admins)
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        # Sender deg til innloggingssiden hvis brukeren ikke har tilgang
        return redirect(url_for('login', next=request.url))

# Tilpasser admin-visningen for modeller
class AdminModelView(ModelView):
    def is_accessible(self):
        # Sjekker om brukeren har admin-rettigheter
        return current_user.is_authenticated and getattr(current_user, 'is_admin', False)

    def inaccessible_callback(self, name, **kwargs):
        # Sender deg til innloggingssiden hvis brukeren ikke har tilgang
        return redirect(url_for('login', next=request.url))

#ADMIN
admin = Admin(app, index_view=MyAdminIndexView())  # Bruker vår custom admin-hovedside
admin.add_view(AdminModelView(User, db.session))   # Legger til bruker i admin-panel

# Skjema for registrering
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=150)], render_kw={"placeholder": "Username"}) #Setter inn brukernavn og krever at minst skal ha 3 karakterer
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=150)], render_kw={"placeholder": "Password"}) #Setter inn passord og krever at minst skal ha 8 karakterer
    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first() #Skjekker om det er liknende brukernavn i databasen
        if existing_user_username:
            raise ValidationError('Brukernavn er tatt. Prøv en annen brukernavn')

# Skjema for innlogging
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=150)], render_kw={"placeholder": "Username"}) #Setter inn brukernavn og krever at minst skal ha 3 karakterer
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=150)], render_kw={"placeholder": "Password"}) #Setter inn passord og krever at minst skal ha 8 karakterer
    submit = SubmitField('Login')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first() #Skjekker om bruker er i database
        if user and Bcrypt.check_password_hash(user.password, form.password.data): #Sjekker om passordet er korrekt/sammenlikner krypteringenstilen til passordet vi skrev inn
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))

    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET', 'POST']) # Logger ut bruker
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST']) # Kommer til hovedskjerm, kun når man er logget inn
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/register', methods=['GET', 'POST']) # Registrerer ny bruker
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = Bcrypt.generate_password_hash(form.password.data) #Krypterer passordet
        new_user = User(username=form.username.data, password=hashed_password) #lager ny bruker
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

if __name__ == '__main__':
   app.run(debug=True, host="0.0.0.0", port=5000)
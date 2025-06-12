from flask import Flask, render_template, url_for, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from datetime import datetime  # For å tidsstemple bestillinger
import os  # For å håndtere loggfil (ikke lenger i bruk, beholdt i tilfelle)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mariadb+pymysql://brukernavn:passord@127.0.0.1/user_database'
app.config['SECRET_KEY'] = 'passord'
db = SQLAlchemy(app)
Bcrypt = Bcrypt(app)

# Gjør at flask og log inn kan sammarbeide
login = LoginManager()
login.init_app(app)
login.login_view = 'login'  # Hvis @login_required brukes og man ikke er innlogget, sendes man hit

# Modell for bruker
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # Er admin?

# Modell for klokker
class Watch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    brand = db.Column(db.String(150), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)  # Hvor mange på lager
    price = db.Column(db.Float, nullable=False)  # Pris i kr
    image_filename = db.Column(db.String(200))  # Filnavn for bilde av klokken

# Ny modell for bestillinger
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Kobler til bruker-tabellen
    watch_id = db.Column(db.Integer, db.ForeignKey('watch.id'), nullable=False)  # Kobler til klokke-tabellen
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Automatisk tidspunkt

    user = db.relationship('User', backref='orders')  # Gjør det mulig å skrive order.user
    watch = db.relationship('Watch', backref='orders')  # Gjør det mulig å skrive order.watch

# Handlekurv-tabell
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    watch_id = db.Column(db.Integer, db.ForeignKey('watch.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', backref='cart_items')  # Tilgang til brukers handlekurv
    watch = db.relationship('Watch')  # Tilgang til klokke-objekt

# Hindrer at andre kan logge inn som admin
@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Henter brukerobjekt fra ID

# Custom admin-hovedside (hindrer tilgang til /admin for ikke-admins)
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

# Tilpasser admin-visningen for modeller
class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user, 'is_admin', False)

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=request.url))

# Kan se hvem og som har bestil hva, og kan fjerne det i admin panel
class OrderAdminView(AdminModelView):
    column_list = ['id', 'user_info', 'watch.name', 'quantity', 'total_price', 'timestamp']
    column_labels = {
        'user_info': 'Bruker (ID / navn)',
        'watch.name': 'Klokke',
        'quantity': 'Antall',
        'total_price': 'Totalpris',
        'timestamp': 'Tidspunkt'
    }

    def _user_info_formatter(self, context, model, name):
        return f"{model.user_id} / {model.user.username}"  # Viser ID og brukernavn samtidig

    column_formatters = {
        'user_info': _user_info_formatter
    }

# Legger til modellene i admin-panelet
admin = Admin(app, index_view=MyAdminIndexView())
admin.add_view(AdminModelView(User, db.session))
admin.add_view(ModelView(Watch, db.session))
admin.add_view(OrderAdminView(Order, db.session))
admin.add_view(AdminModelView(CartItem, db.session))

# Skjema for registrering
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=150)], render_kw={"placeholder": "Username"})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=150)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError('Brukernavn er tatt. Prøv en annen brukernavn')

# Skjema for innlogging
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=150)], render_kw={"placeholder": "Username"})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=150)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')

@app.route('/')
def home():
    return redirect(url_for('register'))  # Sender brukeren rett til registrering

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and Bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)  # Logger inn brukeren og lagrer det i session
            next_page = request.args.get('next')  # Hvis bruker ble sendt hit pga @login_required, send tilbake
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))

    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()  # Logger ut og fjerner session-data
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    query = Watch.query
    search = request.args.get('search')  # Søkeord fra bruker
    brand = request.args.get('brand')  # Filter på merke

    if search:
        query = query.filter(
            (Watch.name.ilike(f'%{search}%')) |
            (Watch.brand.ilike(f'%{search}%'))
        )
    if brand:
        query = query.filter_by(brand=brand)

    watches = query.all()
    all_brands = db.session.query(Watch.brand).distinct().all()  # Henter unike merker for dropdown
    return render_template('dashboard.html', watches=watches, brands=[b[0] for b in all_brands])

# Se hva current_user har bestilt
@app.route('/my_orders')
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.timestamp.desc()).all()
    return render_template('my_orders.html', orders=orders)

# Endret for å lagre bestillinger i database
@app.route('/order/<int:watch_id>', methods=['GET', 'POST'])
@login_required
def order_watch(watch_id):
    watch = Watch.query.get_or_404(watch_id)

    if request.method == 'POST':
        try:
            quantity = int(request.form['quantity'])
        except ValueError:
            quantity = 0

        if quantity <= 0:
            return render_template('error.html', message="Ugyldig antall valgt.", back_url=url_for('dashboard'))

        if quantity > watch.quantity:
            return render_template('error.html', message=f"Ikke nok klokker på lager. Kun {watch.quantity} igjen.", back_url=url_for('dashboard'))

        total_price = quantity * watch.price
        watch.quantity -= quantity

        new_order = Order(user_id=current_user.id, watch_id=watch.id, quantity=quantity, total_price=total_price)
        db.session.add(new_order)
        db.session.commit()

        return render_template('success.html', message=f"Du har bestilt {quantity} stk. {watch.name} for totalt {total_price:.2f} kr.", back_url=url_for('dashboard'))

    return render_template('order_watch.html', watch=watch)

# Viser bestillingsloggen – kun tilgjengelig for admin
@app.route('/admin/orders')
@login_required
def view_orders():
    if not current_user.is_admin:
        return redirect(url_for('dashboard'))

    if not os.path.exists('orders.log'):
        log_entries = ["Ingen bestillinger registrert ennå."]
    else:
        with open('orders.log', 'r', encoding='utf-8') as f:
            log_entries = f.readlines()

    return render_template('orders_log.html', log_entries=log_entries)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = Bcrypt.generate_password_hash(form.password.data)  # Krypterer passordet
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/add_to_cart/<int:watch_id>', methods=['POST'])
@login_required
def add_to_cart(watch_id):
    watch = Watch.query.get_or_404(watch_id)
    quantity = int(request.form['quantity'])

    if quantity <= 0 or quantity > watch.quantity:
        return render_template('error.html', message="Ugyldig antall valgt.", back_url=url_for('dashboard'))

    # Sjekk om varen allerede finnes i handlekurv
    existing_item = CartItem.query.filter_by(user_id=current_user.id, watch_id=watch_id).first()
    if existing_item:
        existing_item.quantity += quantity
    else:
        new_item = CartItem(user_id=current_user.id, watch_id=watch_id, quantity=quantity)
        db.session.add(new_item)

    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/cart')
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.quantity * item.watch.price for item in cart_items)  # Summerer total pris
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/remove_from_cart/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    item = CartItem.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        return redirect(url_for('cart'))  # Bruker kan bare fjerne egne varer
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        return render_template('error.html', message="Handlekurven din er tom.", back_url=url_for('dashboard'))

    # Først sjekker vi at alt i handlekurven er mulig å kjøpe
    for item in cart_items:
        if item.quantity > item.watch.quantity:
            return render_template('error.html', message=f"Ikke nok på lager for {item.watch.name}.", back_url=url_for('cart'))

    total_sum = 0
    for item in cart_items:
        item.watch.quantity -= item.quantity
        total_price = item.quantity * item.watch.price
        total_sum += total_price
        new_order = Order(user_id=current_user.id, watch_id=item.watch.id, quantity=item.quantity, total_price=total_price)
        db.session.add(new_order)
        db.session.delete(item)  # Fjerner fra handlekurven

    db.session.commit()

    message = f"Du har bestilt varer for totalt {total_sum:.2f} kr."
    return render_template('success.html', message=message, back_url=url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5001)  # Kjøres på alle IP-er, port 5001

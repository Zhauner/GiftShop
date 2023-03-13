from flask import (
    Flask,
    render_template,
    request,
    redirect,
    flash,
    url_for,
)

import sqlite3
import os
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from UserLogin import UserLogin
from getUserID import get_user, get_user_by_email, get_username

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = f'{os.getcwd()}\\static'
app.config['SECRET_KEY'] = 'fgtqwert453345555345'

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'auth'


@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id)


class Item(db.Model):
    article = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    extension = db.Column(db.String(10), nullable=False)
    number = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(25), nullable=False)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mail = db.Column(db.String(100), nullable=False)
    passwrd = db.Column(db.String(20), nullable=False)
    number = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(25), nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def main():
    items = Item.query.order_by(Item.article.desc()).all()
    return render_template('index.html', items=items, get_user=get_username(current_user.get_id()))


@app.route('/<int:article>')
def more(article):
    item = Item.query.get(article)
    return render_template('more_inf.html', item=item, get_user=get_username(current_user.get_id()))


@app.route('/buy')
def buy():
    return '[Здесь должно быть окно оплаты]'


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы!', category='success')
    return redirect('/')


@app.route('/auth', methods=['POST', 'GET'])
def auth():
    if request.method == 'POST':

        mail = request.form['name']
        passwrd = request.form['pswd']

        user = get_user_by_email(mail)

        if user and check_password_hash(user[2], passwrd):
            userLogin = UserLogin().create(user)
            login_user(userLogin)
            return redirect('/')

        flash('Неправильный логин или пароль', category='error')
        return redirect('/auth')

    else:
        return render_template('login_form.html', get_user=get_username(current_user.get_id()))


@app.route('/reg', methods=['POST', 'GET'])
def reg():
    if request.method == 'POST':

        all_mails = []

        mail = request.form['mail']
        pswd = request.form['pswd']
        ag_pswd = request.form['ag_pswd']
        name = request.form['name']
        number = request.form['number']

        if len(mail.strip()) > 100 or len(str(pswd.strip())) > 20 or len(str(ag_pswd.strip())) > 20 \
                                                            or pswd.strip() != ag_pswd.strip():
            flash(
                'Проверьте длину(email <= 100 символов, пароль <= 20 \
                символов) либо совпадение паролей',
                category='error'
            )
            return redirect('/reg')

        connect = sqlite3.connect('instance\\shop.db')
        cursor = connect.cursor()
        cursor.execute('SELECT mail FROM users')
        rows = cursor.fetchall()

        for row in rows:
            for x in row:
                all_mails.append(x)

        if mail.strip() in all_mails:
            flash('Такой email уже существует', category='error')
            return redirect('/reg')
        elif not '@' in mail.strip() or not '.' in mail.strip():
            flash('Неверный формат email', category='error')
            return redirect('/reg')


        user = Users(
            mail=mail.strip(),
            passwrd=generate_password_hash(str(pswd)),
            name=name.strip(),
            number=number.strip()
        )

        try:
            db.session.add(user)
            db.session.commit()
            return redirect('/')
        except:
            return 'Ошибка регистрации'


    else:
        return render_template('register_form.html', get_user=get_username(current_user.get_id()))


@app.route('/add', methods=['POST', 'GET'])
@login_required
def add_items():
    if request.method == 'POST':

        allowed_extensions = ['jpg', 'png', 'jpeg']

        title = request.form['title']
        text = request.form['text']
        price = request.form['price']
        file = request.files['file']
        name = get_user(int(current_user.get_id()))[4]
        number = get_user(int(current_user.get_id()))[3]

        extensions = file.filename.split('.')[-1]

        item = Item(
            title=title,
            text=text,
            price=price,
            extension=extensions,
            name=name,
            number=number
        )

        connect = sqlite3.connect('instance\\shop.db')
        cur = connect.cursor()
        cur.execute('SELECT article FROM item')
        rows = cur.fetchall()

        count_rows = []
        for row in rows:
            for x in row:
                count_rows.append(x)

        if extensions not in allowed_extensions:
            return redirect('/add_items.html')

        try:

            file.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'], str(len(count_rows) + 1) + '.' + extensions
                )
            )

            db.session.add(item)
            db.session.commit()
            return redirect('/')
        except:
            return 'Ошибка!'

    else:
        return render_template('add_items.html', get_user=get_username(current_user.get_id()))


if __name__ == '__main__':
    app.run(debug=True)

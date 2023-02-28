from flask import (
    Flask,
    render_template,
    request,
    redirect,
)

from flask_sqlalchemy import SQLAlchemy
import os
import sqlite3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = f'{os.getcwd()}\\images_of_items'
db = SQLAlchemy(app)


class Item(db.Model):
    article = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer, nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/add', methods=['POST', 'GET'])
def add_items():
    if request.method == 'POST':

        allowed_extensions = ['jpg', 'png', 'jpeg']

        title = request.form['title']
        text = request.form['text']
        price = request.form['price']
        file = request.files['file']

        item = Item(title=title, text=text, price=price)

        extensions = file.filename.split('.')[-1]

        connect = sqlite3.connect('instance\\shop.db')
        cur = connect.cursor()
        cur.execute('SELECT article FROM item')
        rows = cur.fetchall()

        count_rows = []
        for row in rows:
            for x in row:
                count_rows.append(x)


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
        return render_template('add_items.html')


if __name__ == '__main__':
    app.run(debug=True)

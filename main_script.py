from datetime import datetime
import os

from flask import Flask, request, make_response, jsonify, redirect, render_template, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from jinja2 import Environment, FileSystemLoader

app = Flask(__name__)
app.config["DEBUG"] = True
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shelter.db'
db = SQLAlchemy(app)
app.secret_key = "Secret Key"


class Shelter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    animal_type = db.Column(db.String, nullable=False)
    nickname = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer)
    height = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    birthday = db.Column(db.Date)
    passport = db.Column(db.Boolean)
    passport_number = db.Column(db.Integer, unique=True)

    def __init__(self, animal_type, nickname, age, height, weight, birthday, passport, passport_number):
        self.animal_type = animal_type
        self.nickname = nickname
        self.age = age
        self.height = height
        self.weight = weight
        self.birthday = birthday
        self.passport = passport
        self.passport_number = passport_number


class Movements(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reasons = db.Column(db.String, nullable=False)
    nickname = db.Column(db.String, db.ForeignKey('shelter.nickname'))

    def __init__(self, reasons, nickname):
        self.reasons = reasons
        self.nickname = nickname


with app.app_context():
    db.create_all()


def get_age(birthday):
    now = datetime.now()  # current year

    nowadays = int(now.strftime("%Y"))
    year_of_birth = int(datetime.strptime(birthday, '%Y-%m-%d').strftime("%Y"))

    return nowadays - year_of_birth


def calculate_the_food(weight):
    return round(95 * weight, 2)


func_dict = {
    "calculate_the_food": calculate_the_food
}


def render(template, all_data, summary):
    env = Environment(loader=FileSystemLoader("templates/"))
    jinja_template = env.get_template(template)
    jinja_template.globals.update(func_dict)
    template_string = jinja_template.render(all_data=all_data, summary=summary)
    return template_string


@app.route('/', methods=['GET'])
def home():
    all_data = Shelter.query.all()
    return render_template("index.html", all_data=all_data)


@app.route('/feeding')
def feed():
    summary = 0
    all_data = Shelter.query.all()
    for row in all_data:
        summary += calculate_the_food(row.weight)
    return render("feeding.html", all_data=all_data, summary=summary)


@app.route('/sort', methods=['POST'])
def sorting():
    animal_type = request.form['type']
    if animal_type != 'all':
        all_data = Shelter.query.filter_by(animal_type=animal_type).all()
    else:
        all_data = Shelter.query.all()
    return render_template("index.html", all_data=all_data)


@app.route('/insert', methods=['POST'])
def insert():
    if request.method == 'POST':
        animal_type = request.form['type']
        nickname = request.form['nickname']
        birthday = request.form['birthday']
        height = float(request.form['height'])
        weight = float(request.form['weight'])
        try:
            passport_number = int(request.form['passport_number'])
        except ValueError:
            passport_number = None

        if passport_number is None:
            passport = False
        else:
            passport = True

        my_data = Shelter(animal_type=animal_type, age=get_age(birthday), nickname=nickname,
                          birthday=datetime.strptime(birthday, '%Y-%m-%d'), height=height, weight=weight,
                          passport_number=passport_number, passport=passport)
        db.session.add(my_data)
        db.session.commit()

        flash("Animal inserted successfully")

        return redirect(url_for('home'))


@app.route('/update', methods=['GET', 'POST'])
def update():
    if request.method == 'POST':
        my_data = Shelter.query.get(request.form.get('id'))

        my_data.height = request.form['height']
        my_data.weight = request.form['weight']

        db.session.commit()
        flash("Animal Updated Successfully")

        return redirect(url_for('home'))


@app.route('/delete', methods=['GET', 'POST'])
def delete():
    if request.method == 'POST':
        id = request.form['id']
        my_data = Shelter.query.get(id)
        reasons = request.form['reason']
        nickname = request.form['nickname']
        db.session.add(Movements(reasons=reasons, nickname=nickname))
        db.session.delete(my_data)
        db.session.commit()

        flash("Animal Deleted Successfully")

    return redirect(url_for("home"))


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
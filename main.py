from crypt import methods
from flask import Flask, render_template, url_for,redirect,request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Float, Integer, String, Boolean
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField
from wtforms.fields.simple import URLField, BooleanField
from wtforms.validators import DataRequired
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
Bootstrap5(app)
# CREATE DB
class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///coffees.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Coffee Table Configuration
class CafePlace(db.Model):
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    name: Mapped[str] = mapped_column(String(250),unique=True,nullable=False)
    popular_coffee: Mapped[str] = mapped_column(String(250),nullable=False)
    map_url: Mapped[str] = mapped_column(String(250),nullable=False)
    img_url: Mapped[str] = mapped_column(String(250),nullable=False)
    location: Mapped[str] = mapped_column(String(250),nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean,nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean,nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean,nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean,nullable=False)
    coffe_price: Mapped[str] = mapped_column(String(250),nullable=False)

# CREATE FLASKFORM
class NewCoffeeForm(FlaskForm):
    place = StringField(label='Add a new Place', validators=[DataRequired()])
    popular_coffee = StringField(label='What is his best coffe to make',validators=[DataRequired()])
    location = StringField(label='Location', validators=[DataRequired()])
    map_url = URLField(label='Coffee Place URL',validators=[DataRequired()])
    img_url = URLField(label='Place Image URL',validators=[DataRequired()])
    has_wifi = BooleanField(label='Does the place has wifi?')
    has_toilet = BooleanField(label='Does the place has toilet?')
    has_sockets = BooleanField(label='Does the place has sockets?')
    can_take_calls = BooleanField(label='Does the place allows to take calls?')
    coffe_price = StringField(label="What's the price for the coffee?")

    submit = SubmitField(label='Submit Data')



with app.app_context():
    db.create_all()

@app.route('/', methods=['GET'])
def home():
    all_coffees = db.session.execute(
        db.select(CafePlace.popular_coffee).distinct()
    ).scalars().all()

    return render_template('index.html', all_coffees=all_coffees)

@app.route('/show-coffees/cafe_name',methods=['GET'])
def show_coffees_by_name():
    cafe_name = request.args.get('cafe_name')
    if cafe_name:
        all_cafes = db.session.execute(db.select(CafePlace).where(CafePlace.popular_coffee==cafe_name)).scalars().all()
        return render_template('cafes.html',all_cafes = all_cafes)

@app.route('/add-cafe',methods=['GET','POST'])
def add_coffe():
    coffee_form = NewCoffeeForm()
    if coffee_form.validate_on_submit():
        new_coffee = CafePlace(
        name = coffee_form.place.data,
        popular_coffee = coffee_form.popular_coffee.data,
        map_url = coffee_form.map_url.data,
        img_url = coffee_form.img_url.data,
        location = coffee_form.location.data,
        has_wifi = bool(coffee_form.has_wifi.data),
        has_toilet = bool(coffee_form.has_toilet.data),
        has_sockets = bool(coffee_form.has_sockets.data),
        can_take_calls = bool(coffee_form.can_take_calls.data),
        coffe_price = bool(coffee_form.coffe_price.data)
        )
        db.session.add(new_coffee)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template('make-coffee.html',form=coffee_form)

@app.route('/edit-cafe/<int:cafe_id>',methods=['GET','POST'])
def edit_coffe(cafe_id):
    coffe_to_update = db.get_or_404(CafePlace,cafe_id)
    edit_coffe_form = NewCoffeeForm(
        place= coffe_to_update.name,
        popular_coffee = coffe_to_update.popular_coffee,
        location = coffe_to_update.location,
        map_url = coffe_to_update.map_url,
        img_url = coffe_to_update.img_url,
        has_wifi = coffe_to_update.has_wifi,
        has_toilet = coffe_to_update.has_toilet,
        has_sockets =  coffe_to_update.has_sockets,
        can_take_calls = coffe_to_update.can_take_calls,
        coffe_price = coffe_to_update.coffe_price
        )
    if edit_coffe_form.validate_on_submit():
        coffe_to_update.name = edit_coffe_form.place
        coffe_to_update.popular_coffee = edit_coffe_form.popular_coffee
        coffe_to_update.location = edit_coffe_form.location
        coffe_to_update.map_url = edit_coffe_form.map_url
        coffe_to_update.img_url = edit_coffe_form.img_url
        coffe_to_update.has_wifi = edit_coffe_form.has_wifi
        coffe_to_update.has_toilet = edit_coffe_form.has_toilet
        coffe_to_update.has_sockets = edit_coffe_form.has_sockets
        coffe_to_update.can_take_calls = edit_coffe_form.can_take_calls
        coffe_to_update.coffe_price = edit_coffe_form.coffe_price

        db.session.commit()
        return redirect(url_for('show_coffees_by_name'))

    return render_template('make-coffee.html',form=edit_coffe_form,to_edit=True)

@app.route('/delete-coffee/<int:coffe_id>', methods=['GET'])
def delete_coffee(coffe_id):
    cafe_to_delete = db.get_or_404(CafePlace,coffe_id)
    db.session.delete(cafe_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/contact')
def contact_page():
    return render_template('contact.html')

if __name__ == "__main__":
    app.run(debug=True)
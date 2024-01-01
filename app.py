from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DecimalField
from wtforms.validators import DataRequired, Email, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
from wtforms import SelectField, SubmitField
from sqlalchemy import func


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:finalproject@database-2.cai0ndpuecwk.us-east-1.rds.amazonaws.com:5432/postgres'
app.config['SECRET_KEY'] = 'finalproject'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
bcrypt = Bcrypt(app)


# Define models
class Customer(UserMixin, db.Model):
    __tablename__ = 'customer'
    __table_args__ = {'schema': 'food_ordering_system'}
    customer_id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(15))
    orders = db.relationship('Order', backref='customer', lazy=True)
    def get_id(self):
        return str(self.customer_id)



class RestaurantCuisine(db.Model):
    __tablename__ = 'restaurantcuisine'
    __table_args__ = {'schema': 'food_ordering_system'}
    restaurant_id = db.Column(db.Integer, db.ForeignKey('food_ordering_system.restaurant.restaurant_id'), primary_key=True)
    cuisine_id = db.Column(db.Integer, db.ForeignKey('food_ordering_system.cuisine.cuisine_id'), primary_key=True)
    restaurant = db.relationship('Restaurant', backref=db.backref('food_ordering_system.restaurantcuisines', lazy='dynamic'))
    cuisine = db.relationship('Cuisine', backref=db.backref('food_ordering_system.restaurantcuisines', lazy='dynamic'))

class RestaurantDish(db.Model):
    __tablename__ = 'restaurantdish'
    __table_args__ = {'schema': 'food_ordering_system'}
    restaurant_id = db.Column(db.Integer, db.ForeignKey('food_ordering_system.restaurant.restaurant_id'), primary_key=True)
    dish_id = db.Column(db.Integer, db.ForeignKey('food_ordering_system.dishes.dish_id'), primary_key=True)
    restaurant = db.relationship('Restaurant', backref=db.backref('food_ordering_system.restaurantdish', lazy='dynamic'))
    dish = db.relationship('Dishes', backref=db.backref('food_ordering_system.restaurantdish', lazy='dynamic'))

class Cuisine(db.Model):
    __tablename__ = 'cuisine'
    __table_args__ = {'schema': 'food_ordering_system'}
    cuisine_id = db.Column(db.Integer, primary_key=True)
    cuisine_name = db.Column(db.String(255), nullable=False)
    
class Restaurant(db.Model):
    __tablename__ = 'restaurant'
    __table_args__ = {'schema': 'food_ordering_system'}
    restaurant_id = db.Column(db.Integer, primary_key=True)
    restaurant_name = db.Column(db.String(255), nullable=False)
    reviews = db.Column(db.Integer)
    rating = db.Column(db.Float)
    price_range = db.Column(db.String(10), nullable=True)
    cuisines = db.relationship('Cuisine', secondary= "food_ordering_system.restaurantcuisine", backref='restaurant', lazy='subquery')
    dishes = db.relationship('Dishes', secondary="food_ordering_system.restaurantdish", backref='restaurant', lazy='subquery')


class Dishes(db.Model):
    __tablename__ = 'dishes'
    __table_args__ = {'schema': 'food_ordering_system'}
    dish_id = db.Column(db.Integer, primary_key=True)
    dish_name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(10, 2))
    cuisine_id = db.Column(db.Integer, db.ForeignKey('food_ordering_system.cuisine.cuisine_id'))
    cuisine = db.relationship('Cuisine', backref=db.backref('dishes', lazy=True))


class Order(db.Model):
    __tablename__ = 'order'
    __table_args__ = {'schema': 'food_ordering_system'}
    order_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('food_ordering_system.customer.customer_id'))
    dish_id = db.Column(db.Integer, db.ForeignKey('food_ordering_system.dishes.dish_id'))
    quantity = db.Column(db.Integer)
    total_price = db.Column(db.Numeric(10, 2))

    dish = db.relationship('Dishes', backref=db.backref('orders', lazy=True))

    

# Define forms
class RegistrationForm(FlaskForm):
    customer_name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirm_password')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])
    phone_number = StringField('Phone Number')
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


# Flask-Login setup
@login_manager.user_loader
def load_user(user_id):
    return Customer.query.get(int(user_id))


# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/restaurants')
def restaurants():
    restaurants = (
            db.session.query(Restaurant)
            .join(RestaurantDish, Restaurant.restaurant_id == RestaurantDish.restaurant_id)
            .distinct()
            .all()
        )
    return render_template('restaurants.html', restaurants=restaurants)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_customer = Customer(customer_name=form.customer_name.data,
                                email=form.email.data,
                                password_hash=hashed_password,
                                phone_number=form.phone_number.data)
        db.session.add(new_customer)
        db.session.commit()
        flash('Account created successfully. You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        customer = Customer.query.filter_by(email=form.email.data).first()

        if customer and bcrypt.check_password_hash(customer.password_hash, form.password.data):
            login_user(customer)
            flash('Login successful.', 'success')
            return redirect(url_for('filter_restaurants'))  # Redirect to restaurants page
        else:
            flash('Login failed. Check your email and password.', 'danger')
            return redirect(url_for('home'))  # Redirect to home page

    return render_template('login.html', form=form)

def filter_restaurants_by_criteria(cuisine_id, price, review):
    # Start by getting the average worth of products for each restaurant
    avg_worth = func.avg(Dishes.price).label('avg_worth')
    avg_worth_subquery = (
        db.session.query(avg_worth, Restaurant.restaurant_id)
        .join(RestaurantCuisine, RestaurantCuisine.restaurant_id == Restaurant.restaurant_id)
        .join(Dishes, Dishes.cuisine_id == RestaurantCuisine.cuisine_id)
        .group_by(Restaurant.restaurant_id)
        .subquery()
    )

    # Get the overall average worth among all restaurants
    overall_avg_worth = db.session.query(func.avg(avg_worth_subquery.c.avg_worth)).scalar()

    # Define the price range categories
    expensive_threshold = overall_avg_worth + 50  # Adjust the threshold as needed
    affordable_threshold = overall_avg_worth - 50  # Adjust the threshold as needed

    # Build the main query to filter restaurants based on the criteria
    query = db.session.query(Restaurant)

    if cuisine_id != '0':
        query = query.join(RestaurantCuisine, RestaurantCuisine.restaurant_id == Restaurant.restaurant_id)
        query = query.filter(RestaurantCuisine.cuisine_id == cuisine_id)
    
    if price == 'expensive':
        query = query.join(avg_worth_subquery, avg_worth_subquery.c.restaurant_id == Restaurant.restaurant_id)
        query = query.filter(avg_worth_subquery.c.avg_worth > expensive_threshold)
    elif price == 'affordable':
        query = query.join(avg_worth_subquery, avg_worth_subquery.c.restaurant_id == Restaurant.restaurant_id)
        query = query.filter(avg_worth_subquery.c.avg_worth < affordable_threshold)
    elif price == 'average':
        query = query.join(avg_worth_subquery, avg_worth_subquery.c.restaurant_id == Restaurant.restaurant_id)
        query = query.filter((avg_worth_subquery.c.avg_worth >= affordable_threshold) & (avg_worth_subquery.c.avg_worth <= expensive_threshold))

    if review == '501':
        query = query.filter(Restaurant.reviews > 500)
    elif review == '301':
        query = query.filter(Restaurant.reviews > 300)
    elif review == '101':
        query = query.filter(Restaurant.reviews > 100)

    # Execute the query and return the filtered restaurants
    filtered_restaurants = query.all()
    
    return filtered_restaurants

class FilterForm(FlaskForm):
    with app.app_context():
        cuisines = Cuisine.query.all()
        cuisine_choices = [(cuisine.cuisine_id, cuisine.cuisine_name) for cuisine in cuisines]
        cuisine_choices.insert(0, (0, 'Any Cuisine'))  # Add an option for no specific cuisine
        print(cuisine_choices)

        cuisine = SelectField('Cuisine', choices=cuisine_choices)

        # Define custom price choices
        price_choices = [
            ('None', 'Any Price Range'),
            ('expensive', 'Expensive'),
            ('average', 'Average'),
            ('affordable', 'Affordable'),
        ]

        price = SelectField('Price Range', choices=price_choices)

        # Define custom review choices
        review_choices = [
            ('', 'Any Review Number'), 
            (501, 'More than 500'),
            (301, 'More than 300'),
            (101, 'More than 100'),
        ]

        review = SelectField('Review Number', choices=review_choices)

        submit = SubmitField('Filter')
    
    
@app.route('/filter', methods=['GET', 'POST'])
def filter_restaurants():
    form = FilterForm()

    if form.validate_on_submit():
        cuisine_id = form.cuisine.data or None
        price = form.price.data or None
        review = form.review.data or None

        filtered_restaurants = filter_restaurants_by_criteria(cuisine_id, price, review)
        return render_template('restaurants.html', restaurants=filtered_restaurants)

    return render_template('filter.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/menu/<int:restaurant_id>')
def menu(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    dishes = restaurant.dishes
    return render_template('menu.html', restaurant=restaurant, dishes=dishes)


@app.route('/order/<int:dish_id>', methods=['POST'])
@login_required
def order(dish_id):
    dish = Dishes.query.get_or_404(dish_id)
    quantity = int(request.form.get('quantity'))

    if quantity <= 0:
        flash('Invalid quantity. Please select at least one item.', 'danger')
        return redirect(url_for('menu', restaurant_id=dish.cuisine.restaurants[0].restaurant_id))

    total_price = dish.price * quantity

    # Assuming the primary key in your Dishes model is named dish_id
    new_order = Order(customer=current_user, dish_id=dish.dish_id, quantity=quantity, total_price=total_price)
    db.session.add(new_order)
    db.session.commit()

    flash(f'Order placed successfully. Total: ${total_price}', 'success')
    return redirect(url_for('order_history'))

with app.app_context():
    try:
        # Ensure the tables are created
        db.create_all()

        # Fetch some data from the Restaurant table (change as needed)
        restaurants = Restaurant.query.limit(5).all()

        # Display the fetched data
        print("\nRestaurant Table:")
        for restaurant in restaurants:
            print(f"Restaurant ID: {restaurant.restaurant_id}, Name: {restaurant.restaurant_name}, Reviews: {restaurant.reviews}, Rating: {restaurant.rating}, Price Range: {restaurant.price_range}")

        # Fetch some data from the RestaurantCuisine association table (change as needed)
        restaurant_cuisines = RestaurantCuisine.query.limit(5).all()

        # Display the fetched data
        print("\nRestaurantCuisine Association Table:")
        for row in restaurant_cuisines:
            print(f"Restaurant ID: {row.restaurant_id}, Cuisine ID: {row.cuisine_id}")

    except Exception as e:
        print(f"Error connecting to the database: {e}")



@app.route('/order_history')
@login_required
def order_history():
    orders = Order.query.filter_by(customer_id=current_user.customer_id).all()
    return render_template('order_history.html', orders=orders)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
    print("Connected to the database successfully.")
    app.run(debug=True)

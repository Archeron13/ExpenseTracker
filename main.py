from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from collections import defaultdict
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///based.db'
app.secret_key = os.urandom(24)  # Doesnt work without it

db = SQLAlchemy(app)


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    expense_name = db.Column(db.String(50), nullable=False)
    expense_type = db.Column(db.String(50), nullable=False)
    cost_dollars = db.Column(db.Float, nullable=False)  # Store cost in dollars
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    expenses = db.relationship('Expense', backref='user', lazy=True)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = username  # Store the username in the session
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid credentials. Please try again.'
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return 'Username already exists. Please choose a different username.'
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))
    user = User.query.filter_by(username=username).first()
    expenses = user.expenses
    return render_template('dashboard.html', username=username, expenses=expenses)

@app.route('/add_expense', methods=['POST'])
def add_expense():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    expense_type = request.form['expense_type']
    expense_name = request.form['expense_name']
    cost = float(request.form['cost'])  # Store cost in original currency
    currency = request.form['currency']

    # Convert cost to dollars if necessary
    if currency == 'Rupees':
        cost_dollars = cost / 83.45  # Conversion rate: 1 Rupee = 1 / 83.45 Dollars
    elif currency == 'Rubles':
        cost_dollars = cost / 92.4  # Conversion rate: 1 Ruble = 1 / 92.4 Dollars
    else:  # Default to Dollars
        cost_dollars = cost

    # Get the user and add the expense
    user = User.query.filter_by(username=username).first()
    new_expense = Expense(expense_type=expense_type, expense_name=expense_name, cost_dollars=cost_dollars, user=user)
    db.session.add(new_expense)
    db.session.commit()

    return redirect(url_for('dashboard'))

@app.route('/show_expenses', methods=['GET', 'POST'])
def show_expenses():
    username = session.get('username')
    if not username:
        return redirect(url_for('login'))

    if request.method == 'POST':
        selected_currency = request.form.get('currency', 'Dollars')  # Default to Dollars
        selected_category = request.form.get('category', 'All')  # Default to All categories
        print("Selected category:", selected_category)
    else:
        selected_currency = 'Dollars'  # Default to Dollars
        selected_category = 'All'  # Default to All categories

    user = User.query.filter_by(username=username).first()
    expenses = user.expenses

    if selected_category != 'All':
        filtered_expenses = []
        for expense in expenses:
            if expense.expense_type == selected_category:
                filtered_expenses.append(expense)
        expenses = filtered_expenses

    # Calculate total amount by category
    total_by_category = {}
    for expense in expenses:
        category = expense.expense_type
        total_by_category[category] = total_by_category.get(category, 0) + expense.cost_dollars

    return render_template('expenses.html', expenses=expenses, selected_currency=selected_currency,
                           selected_category=selected_category, total_by_category=total_by_category)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

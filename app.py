from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change to a random secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db = SQLAlchemy(app)

# Database model for User
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Database model for Expense
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100), nullable=False)

# Create database tables
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        return redirect(url_for('dashboard'))

    return "Invalid credentials!"

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = generate_password_hash(request.form['password'])

    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()
    
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    expenses = Expense.query.filter_by(user_id=session['user_id']).all()
    return render_template('dashboard.html', expenses=expenses)

@app.route('/add_expense', methods=['POST'])
def add_expense():
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401

    name = request.form['name']
    amount = float(request.form['amount'])
    category = request.form['category']

    new_expense = Expense(user_id=session['user_id'], name=name, amount=amount, category=category)
    db.session.add(new_expense)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/delete_expense/<int:id>', methods=['POST'])
def delete_expense(id):
    expense = Expense.query.get(id)
    if expense and expense.user_id == session['user_id']:
        db.session.delete(expense)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'error': 'Expense not found'}), 404

@app.route('/edit_expense/<int:id>', methods=['POST'])
def edit_expense(id):
    expense = Expense.query.get(id)
    if expense and expense.user_id == session['user_id']:
        expense.name = request.form['name']
        expense.amount = float(request.form['amount'])
        expense.category = request.form['category']
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'error': 'Expense not found'}), 404

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

@app.route('/api/expenses')
def get_expenses():
    if 'user_id' not in session:
        return jsonify({'error': 'User not logged in'}), 401
    expenses = Expense.query.filter_by(user_id=session['user_id']).all()
    return jsonify([{'id': e.id, 'name': e.name, 'amount': e.amount, 'category': e.category} for e in expenses])

if __name__ == '__main__':
    app.run(debug=True)

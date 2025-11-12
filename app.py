from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

# app.py
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import json

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "dev_secret_change_me")

# --- Optional DB (SQLite) setup for persisting orders
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'shop.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Order model
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    items_json = db.Column(db.Text, nullable=False)   # store cart as JSON
    amount = db.Column(db.Float, nullable=False)
    payment_id = db.Column(db.String(120), nullable=True)
    status = db.Column(db.String(40), default='pending')

    def items(self):
        return json.loads(self.items_json)

# Create DB (run once)
# with app.app_context(): db.create_all()

# --- Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    item = request.form.get('item')
    price = float(request.form.get('price', 0))
    qty = int(request.form.get('qty', 1))

    cart = session.get('cart', [])
    # merge same item (simple approach)
    for c in cart:
        if c['item'] == item and abs(c['price'] - price) < 1e-6:
            c['qty'] += qty
            session['cart'] = cart
            session.modified = True
            return redirect(url_for('view_cart'))

    cart.append({'item': item, 'price': price, 'qty': qty})
    session['cart'] = cart
    session.modified = True
    return redirect(url_for('view_cart'))

@app.route('/cart')
def view_cart():
    cart = session.get('cart', [])
    total = sum(c['price'] * c['qty'] for c in cart)
    return render_template('cart.html', cart=cart, total=total)

@app.route('/update_cart', methods=['POST'])
def update_cart():
    action = request.form.get('action')
    item = request.form.get('item')
    cart = session.get('cart', [])
    if action == 'remove':
        cart = [c for c in cart if c['item'] != item]
    elif action == 'update':
        qty = int(request.form.get('qty', 1))
        for c in cart:
            if c['item'] == item:
                c['qty'] = qty
    session['cart'] = cart
    session.modified = True
    return redirect(url_for('view_cart'))

# A simple checkout page (no payment yet)
@app.route('/checkout')
def checkout():
    cart = session.get('cart', [])
    if not cart:
        return redirect(url_for('home'))
    total = sum(c['price'] * c['qty'] for c in cart)
    return render_template('checkout.html', cart=cart, total=total)

# confirm order without payment (for testing)
@app.route('/order_success', methods=['POST'])
def order_success():
    cart = session.get('cart', [])
    total = sum(c['price'] * c['qty'] for c in cart)
    # persist order
    order = Order(items_json=json.dumps(cart), amount=total, status='paid' if request.form.get('paid') == '1' else 'confirmed', payment_id=request.form.get('payment_id'))
    db.session.add(order)
    db.session.commit()

    # clear cart
    session.pop('cart', None)
    return render_template('success.html', order=order)

if __name__ == '__main__':
    app.run(debug=True)

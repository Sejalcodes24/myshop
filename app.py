from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "supersecretkey"   # required for session


# -----------------------
# HOME PAGE
# -----------------------
@app.route("/")
def home():
    return render_template("index.html")


# -----------------------
# ADD ITEM TO CART
# -----------------------
@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    item = request.form.get("item")
    price = float(request.form.get("price"))
    qty = int(request.form.get("qty", 1))

    # create cart if not exists
    if "cart" not in session:
        session["cart"] = []

    # add item
    session["cart"].append({
        "item": item,
        "price": price,
        "qty": qty,
        "total": price * qty
    })

    session.modified = True
    return redirect(url_for("cart"))


# -----------------------
# CART PAGE
# -----------------------
@app.route("/cart")
def cart():
    cart_items = session.get("cart", [])
    total_amount = sum(item["total"] for item in cart_items)
    return render_template("cart.html", cart=cart_items, total=total_amount)


# -----------------------
# REMOVE ITEM
# -----------------------
@app.route("/remove/<int:index>")
def remove(index):
    if "cart" in session:
        session["cart"].pop(index)
        session.modified = True
    return redirect(url_for("cart"))


# -----------------------
# CHECKOUT PAGE
# -----------------------
@app.route("/checkout")
def checkout():
    cart_items = session.get("cart", [])
    total_amount = sum(item["total"] for item in cart_items)
    return render_template("checkout.html", cart=cart_items, total=total_amount)


# -----------------------
# CLEAR CART
# -----------------------
@app.route("/clear_cart")
def clear_cart():
    session.pop("cart", None)
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True)

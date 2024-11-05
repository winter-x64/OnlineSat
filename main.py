# Import required modules
import json
from datetime import datetime

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app
app = Flask(import_name=__name__)


# Configure SQLAlchemy database settings
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize SQLAlchemy database
db = SQLAlchemy(app)


# Define Order model for database
class Order(db.Model):
    # Primary key for order
    id = db.Column(db.Integer, primary_key=True)
    # Store item details as JSON string
    items = db.Column(db.Text, nullable=False)
    # Store total amount of order
    total_amount = db.Column(db.Float, nullable=False)
    # Store timestamp of order creation
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Order {self.id}>"


# Create database tables
with app.app_context():
    db.create_all()


# Route for home page
@app.route(rule="/")
def index():
    return render_template(template_name_or_list="index.html")


# Route for shop page
@app.route(rule="/shop")
def shop():
    return render_template(template_name_or_list="shop.html")


# Route for order confirmation page
@app.route(rule="/confirm")
def confirm_page():
    return render_template(template_name_or_list="confirm_page.html")


# API endpoint to save transaction/order details
@app.route("/save_transaction", methods=["POST"])
def save_transaction():
    try:
        # Get JSON data from request
        data = request.get_json()
        items = data["items"]

        # Create a map to count duplicate items
        item_count_map = {}
        for item in items:
            if item["name"] not in item_count_map:
                # Add new item to map
                item_count_map[item["name"]] = {
                    "name": item["name"],
                    "price": item["price"],
                    "count": 1,
                }
            else:
                # Increment count for existing item
                item_count_map[item["name"]]["count"] += 1

        # Convert item map to list for database storage
        items_with_count = list(item_count_map.values())

        # Create new order record
        order = Order(
            items=json.dumps(items_with_count), total_amount=data["total_amount"]
        )

        # Save order to database
        db.session.add(order)
        db.session.commit()

        # Return order ID on success
        return jsonify({"transaction_id": order.id}), 200
    except Exception as e:
        # Rollback transaction on error
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# Run Flask app in debug mode if executed directly
if __name__ == "__main__":
    app.run(debug=True)

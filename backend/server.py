from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2

# Assuming DB connection details are correct
db_connection = psycopg2.connect(dbname="ecommerce", user="postgres", password="postgres", host="db", port="5432")
db_cursor = db_connection.cursor()

app = Flask(__name__)
CORS(app)  # Enable CORS if your frontend is served from a different origin

@app.route('/api/products', methods=['GET', 'POST'])
def products():
    if request.method == 'POST':
        data = request.json
        db_cursor.execute("INSERT INTO products (name, description, price, category, stock_status, image_url) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                          (data['name'], data['description'], data['price'], data['category'], data['stock_status'], data['image_url']))
        db_connection.commit()
        product_id = db_cursor.fetchone()[0]
        return jsonify({'id': product_id}), 201

    elif request.method == 'GET':
        db_cursor.execute("SELECT * FROM products")
        products = db_cursor.fetchall()
        product_list = [{'id': prod[0], 'name': prod[1], 'description': prod[2], 'price': prod[3], 'category': prod[4], 'stock_status': prod[5], 'image_url': prod[6]} for prod in products]
        return jsonify(product_list)


@app.route('/api/products/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def product(id):
    if request.method == 'GET':
        db_cursor.execute("SELECT * FROM products WHERE id = %s", (id,))
        product = db_cursor.fetchone()
        if product:
            return jsonify({'id': product[0], 'name': product[1], 'description': product[2], 'price': product[3], 'category': product[4], 'stock_status': product[5], 'image_url': product[6]})
        else:
            return jsonify({'message': 'Product not found'}), 404

    elif request.method == 'PUT':
        data = request.json
        db_cursor.execute("UPDATE products SET name = %s, description = %s, price = %s, category = %s, stock_status = %s, image_url = %s WHERE id = %s",
                          (data['name'], data['description'], data['price'], data['category'], data['stock_status'], data['image_url'], id))
        db_connection.commit()
        return jsonify({'message': 'Product updated'})

    elif request.method == 'DELETE':
        db_cursor.execute("DELETE FROM products WHERE id = %s", (id,))
        db_connection.commit()
        return jsonify({'message': 'Product deleted'})

@app.route('/api/orders', methods=['POST'])
def orders():
    data = request.json
    db_cursor.execute("INSERT INTO orders (user_id, total_price, status) VALUES (%s, %s, %s) RETURNING id",
                      (data['user_id'], data['total_price'], data['status']))
    db_connection.commit()
    order_id = db_cursor.fetchone()[0]
    return jsonify({'order_id': order_id}), 201

@app.route('/api/orders/<int:user_id>', methods=['GET'])    
def order(user_id):
    db_cursor.execute("SELECT * FROM orders WHERE user_id = %s", (user_id,))
    orders = db_cursor.fetchall()
    orders_list = [{'id': ord[0], 'user_id': ord[1], 'total_price': ord[2], 'status': ord[3]} for ord in orders]
    return jsonify(orders_list)

@app.route('/api/cart/<int:user_id>', methods=['GET', 'POST'])
def cart(user_id):
    if request.method == 'POST':
        data = request.json
        db_cursor.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, %s)",
                          (user_id, data['product_id'], data['quantity']))
        db_connection.commit()
        return jsonify({'message': 'Item added to cart'})

    elif request.method == 'GET':
        db_cursor.execute("SELECT * FROM cart WHERE user_id = %s", (user_id,))
        cart_items = db_cursor.fetchall()
        cart_list = [{'user_id': item[0], 'product_id': item[1], 'quantity': item[2]} for item in cart_items]
        return jsonify(cart_list)

@app.route('/api/cart/<int:user_id>/item/<int:product_id>', methods=['DELETE'])
def delete_cart_item(user_id, product_id):
    db_cursor.execute("DELETE FROM cart WHERE user_id = %s AND product_id = %s", (user_id, product_id))
    db_connection.commit()
    return jsonify({'message': 'Item removed from cart'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001)

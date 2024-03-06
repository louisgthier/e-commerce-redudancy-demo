from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import threading
import time

# Assuming DB connection details are correct

db_connections = []

for i in range(1, 3):
    try:
        db_connections.append(psycopg2.connect(dbname="ecommerce", user="postgres", password="postgres", host=f"db{i}", port="5432"))
    except psycopg2.OperationalError:
        print(f"Error: Could not connect to db{i}")

db_cursors = [db_connection.cursor() for db_connection in db_connections]

def replicate_to_secondary(query, params=None):
    for cursor in db_cursors[1:]:  # Exclude the first cursor, which is for the primary DB
        try:
            cursor.execute(query, params)
        except psycopg2.InterfaceError:
            print("Error: Lost connection to secondary database")

def execute_query(query, params=None, commit=False):
    primary_cursor = db_cursors[0]  # Primary database cursor
    try:
        primary_cursor.execute(query, params)
        if commit:
            db_connections[0].commit()  # Commit on primary DB
            # Replicate asynchronously to secondary DBs
            replication_thread = threading.Thread(target=replicate_to_secondary, args=(query, params))
            replication_thread.start()
    except psycopg2.InterfaceError:
        print("Error: Lost connection to primary database")

# Commit on secondary DBs every 10 seconds
def commit_to_secondary():
    while True:
        for connection in db_connections[1:]:
            try:
                connection.commit()
                print("Committed to secondary database")
            except psycopg2.InterfaceError:
                print("Error: Lost connection to secondary database")
            except Exception as e:
                print(f"Error: {e}")
        print("Sleeping for 10 seconds")
        time.sleep(10)
        print("Woke up")

commit_thread = threading.Thread(target=commit_to_secondary)
commit_thread.start()


app = Flask(__name__)
CORS(app)  # Enable CORS if your frontend is served from a different origin

@app.route('/api/products', methods=['GET', 'POST'])
def products():
    if request.method == 'POST':
        data = request.json
        execute_query("INSERT INTO products (name, description, price, category, stock_status, image_url) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                          (data['name'], data['description'], data['price'], data['category'], data['stock_status'], data['image_url']), commit=True)
        product_id = db_cursors[0].fetchone()[0]
        return jsonify({'id': product_id}), 201

    elif request.method == 'GET':
        execute_query("SELECT * FROM products")
        products = db_cursors[0].fetchall()
        product_list = [{'id': prod[0], 'name': prod[1], 'description': prod[2], 'price': prod[3], 'category': prod[4], 'stock_status': prod[5], 'image_url': prod[6]} for prod in products]
        return jsonify(product_list)


@app.route('/api/products/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def product(id):
    if request.method == 'GET':
        execute_query("SELECT * FROM products WHERE id = %s", (id,))
        product = db_cursors[0].fetchone()
        if product:
            return jsonify({'id': product[0], 'name': product[1], 'description': product[2], 'price': product[3], 'category': product[4], 'stock_status': product[5], 'image_url': product[6]})
        else:
            return jsonify({'message': 'Product not found'}), 404

    elif request.method == 'PUT':
        data = request.json
        execute_query("UPDATE products SET name = %s, description = %s, price = %s, category = %s, stock_status = %s, image_url = %s WHERE id = %s",
                          (data['name'], data['description'], data['price'], data['category'], data['stock_status'], data['image_url'], id), commit=True)
        return jsonify({'message': 'Product updated'})

    elif request.method == 'DELETE':
        execute_query("DELETE FROM products WHERE id = %s", (id,), commit=True)
        return jsonify({'message': 'Product deleted'})

@app.route('/api/orders', methods=['POST'])
def orders():
    data = request.json
    execute_query("INSERT INTO orders (user_id, total_price, status) VALUES (%s, %s, %s) RETURNING id",
                      (data['user_id'], data['total_price'], data['status']), commit=True)
    order_id = db_cursors[0].fetchone()[0]
    return jsonify({'order_id': order_id}), 201

@app.route('/api/orders/<int:user_id>', methods=['GET'])    
def order(user_id):
    execute_query("SELECT * FROM orders WHERE user_id = %s", (user_id,))
    orders = db_cursors[0].fetchall()
    orders_list = [{'id': ord[0], 'user_id': ord[1], 'total_price': ord[2], 'status': ord[3]} for ord in orders]
    return jsonify(orders_list)

@app.route('/api/cart/<int:user_id>', methods=['GET', 'POST'])
def cart(user_id):
    if request.method == 'POST':
        data = request.json
        execute_query("INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, %s)",
                          (user_id, data['product_id'], data['quantity']), commit=True)
        return jsonify({'message': 'Item added to cart'})

    elif request.method == 'GET':
        execute_query("SELECT * FROM cart WHERE user_id = %s", (user_id,))
        cart_items = db_cursors[0].fetchall()
        cart_list = [{'user_id': item[0], 'product_id': item[1], 'quantity': item[2]} for item in cart_items]
        return jsonify(cart_list)

@app.route('/api/cart/<int:user_id>/item/<int:product_id>', methods=['DELETE'])
def delete_cart_item(user_id, product_id):
    execute_query("DELETE FROM cart WHERE user_id = %s AND product_id = %s", (user_id, product_id), commit=True)
    return jsonify({'message': 'Item removed from cart'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001)

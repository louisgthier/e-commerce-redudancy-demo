CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    price DECIMAL(10, 2),
    category VARCHAR(255),
    stock_status BOOLEAN,
    image_url TEXT
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT,
    total_price DECIMAL(10, 2),
    status VARCHAR(50)
);

CREATE TABLE order_items (
    order_id INT,
    product_id INT,
    quantity INT,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE carts (
    user_id INT PRIMARY KEY,
    product_id INT,
    quantity INT,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

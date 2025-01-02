import pytest

from app import app
from db_utils import get_db_connection


@pytest.fixture
def app_context():
    """Provide a Flask application context for tests."""
    app.config["TESTING"] = True  # Ensure TESTING mode is enabled
    print(f"TESTING set to: {app.config['TESTING']}")  # Debug output
    with app.app_context():
        yield app


@pytest.fixture
def client(app_context):
    """Configure Flask app for testing with an in-memory SQLite database."""
    client = app.test_client()

    # Set up an in-memory database
    with app.app_context():
        conn = get_db_connection()

        # Create tables
        cursor = conn.cursor()
        cursor.execute(
            """
        CREATE TABLE products (
            sku TEXT PRIMARY KEY,
            name TEXT,
            cost REAL,
            listed_price REAL,
            inventory_level INTEGER,
            estimated_shipping_cost REAL
        );
        """
        )
        cursor.execute(
            """
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_total REAL,
            actual_shipping_cost REAL,
            total_estimated_shipping_cost REAL,
            order_date DATE  -- Add this column
        );
        """
        )
        cursor.execute(
            """
        CREATE TABLE line_items (
            line_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            sku TEXT,
            quantity INTEGER,
            price REAL,
            subtotal REAL,
            supplier TEXT,
            subtotal_estimated_shipping_cost REAL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (sku) REFERENCES products(sku)
        );
        """
        )
        conn.commit()

        # Populate the database with test data
        populate_test_data(conn)

    yield client


def populate_test_data(conn):
    """Insert test data into the in-memory database."""
    cursor = conn.cursor()

    # Insert sample products
    cursor.execute(
        """
    INSERT INTO products (sku, name, cost, listed_price, inventory_level, estimated_shipping_cost)
    VALUES ('SKU001', 'Test Product A', 10.0, 15.0, 100, 5.0),
           ('SKU002', 'Test Product B', 20.0, 30.0, 50, 7.0);
    """
    )

    # Insert sample orders with dates
    cursor.execute(
        """
    INSERT INTO orders (order_total, actual_shipping_cost, total_estimated_shipping_cost, order_date)
    VALUES (100.0, 10.0, 8.0, DATE('now', '-2 days')), -- Order from 2 days ago
           (200.0, 15.0, 12.0, DATE('now', '-10 days')), -- Order from 10 days ago
           (150.0, 12.0, 9.0, DATE('now', '-40 days')); -- Order from 40 days ago
    """
    )

    # Insert sample line items
    cursor.execute(
        """
    INSERT INTO line_items (order_id, sku, quantity, price, subtotal, supplier, subtotal_estimated_shipping_cost)
    VALUES (1, 'SKU001', 2, 15.0, 30.0, 'Supplier A', 10.0),
           (2, 'SKU002', 1, 30.0, 30.0, 'Supplier B', 7.0),
           (3, 'SKU001', 3, 15.0, 45.0, 'Supplier A', 15.0);
    """
    )
    conn.commit()

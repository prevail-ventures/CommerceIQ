from app import app
from db_utils import get_db_connection


def test_flask_context(app_context):
    """Ensure the Flask context is properly initialized."""
    with app.app_context():  # Use app.app_context() instead of just app
        print(f"TESTING: {app.config['TESTING']}")  # Debug output
        assert app.config["TESTING"] is True  # Verify TESTING is enabled


def test_database_connection(app_context):
    """Ensure the database connection works."""
    app.config["TESTING"] = True  # Explicitly set testing mode
    conn = get_db_connection()
    assert conn is not None
    conn.close()


def test_insert_and_query_product():
    """Test inserting and querying a product."""
    with app.app_context():  # Use app.app_context() instead of app
        conn = get_db_connection()

        # Recreate tables (if needed) for safety
        cursor = conn.cursor()
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS products (
            sku TEXT PRIMARY KEY,
            name TEXT,
            cost REAL,
            listed_price REAL,
            inventory_level INTEGER,
            estimated_shipping_cost REAL
        );
        """
        )
        conn.commit()

        # Insert a product into the products table
        cursor.execute(
            """
        INSERT INTO products (sku, name, cost, listed_price, inventory_level, estimated_shipping_cost)
        VALUES ('SKU003', 'Test Product C', 25.0, 35.0, 75, 6.5);
        """
        )
        conn.commit()

        # Query the product to ensure it was inserted correctly
        cursor.execute("SELECT * FROM products WHERE sku = 'SKU003';")
        product = cursor.fetchone()
        assert product is not None
        assert product["name"] == "Test Product C"
        assert product["cost"] == 25.0
        assert product["estimated_shipping_cost"] == 6.5

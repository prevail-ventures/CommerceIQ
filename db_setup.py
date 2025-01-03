from db_utils import get_db_connection


def create_tables():
    """Create the database tables."""
    print("Connecting to the database...")
    conn = get_db_connection()
    cursor = conn.cursor()

    # Drop tables if they exist to ensure a clean slate
    print("Dropping existing tables...")
    try:
        cursor.execute("DROP TABLE IF EXISTS line_items;")
        cursor.execute("DROP TABLE IF EXISTS orders;")
        cursor.execute("DROP TABLE IF EXISTS products;")
    except Exception as e:
        print(f"Error dropping tables: {e}")

    # Create products table
    print("Creating products table...")
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            sku VARCHAR(255) PRIMARY KEY,
            name VARCHAR(255),
            cost DECIMAL(10, 2),
            listed_price DECIMAL(10, 2),
            inventory_level INT,
            estimated_shipping_cost DECIMAL(10, 2)
        );
        """
    )

    # Create orders table
    print("Creating orders table...")
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id INT AUTO_INCREMENT PRIMARY KEY,
            order_total DECIMAL(10, 2),
            actual_order_total DECIMAL(10, 2),
            actual_shipping_cost DECIMAL(10, 2),
            total_estimated_shipping_cost DECIMAL(10, 2),
            projected_shipping_company VARCHAR(255),
            projected_shipping_method VARCHAR(255),
            actual_shipping_method VARCHAR(255),
            shipping_address_state VARCHAR(255),
            order_date DATE
        );
        """
    )

    # Create line items table
    print("Creating line_items table...")
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS line_items (
            line_item_id INT AUTO_INCREMENT PRIMARY KEY,
            order_id INT,
            sku VARCHAR(255),
            quantity INT,
            price DECIMAL(10, 2),
            subtotal DECIMAL(10, 2),
            supplier VARCHAR(255),
            subtotal_estimated_shipping_cost DECIMAL(10, 2),
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (sku) REFERENCES products(sku)
        );
        """
    )

    conn.commit()
    cursor.close()
    conn.close()
    print("Database tables created successfully.")


if __name__ == "__main__":
    create_tables()

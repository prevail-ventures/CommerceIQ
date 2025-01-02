from db_utils import get_db_connection


def populate_data():
    """Insert sample data into the database."""
    print("Connecting to the database...")
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Insert sample products
        print("Inserting sample products...")
        cursor.execute(
            """
        INSERT INTO products (sku, name, cost, listed_price, inventory_level, estimated_shipping_cost)
        VALUES 
            ('SKU001', 'Product A', 10.0, 15.0, 100, 5.0),
            ('SKU002', 'Product B', 20.0, 30.0, 50, 7.0),
            ('SKU003', 'Product C', 25.0, 35.0, 75, 6.5),
            ('SKU004', 'Product D', 15.0, 20.0, 80, 4.0),
            ('SKU005', 'Product E', 30.0, 40.0, 60, 8.0)
        """
        )
        conn.commit()

        # Insert sample orders
        print("Inserting sample orders...")
        cursor.execute(
            """
        INSERT INTO orders (order_total, actual_shipping_cost, total_estimated_shipping_cost, order_date)
        VALUES 
            (100.0, 10.0, 8.0, '2024-12-25'),  -- Positive differential
            (200.0, 15.0, 20.0, '2024-12-20'), -- Negative differential
            (150.0, 12.0, 12.0, '2024-11-15'), -- Zero differential
            (250.0, 18.0, 20.0, '2024-09-01'), -- Within last 3 months
            (300.0, 20.0, 18.0, '2023-01-01')  -- Outside last 6 months
        """
        )
        conn.commit()

        # Fetch order IDs
        print("Fetching order IDs...")
        cursor.execute("SELECT order_id FROM orders ORDER BY order_date ASC")
        order_ids = [row[0] for row in cursor.fetchall()]
        print(f"Order IDs: {order_ids}")

        # Insert sample line items using the fetched order IDs
        print("Inserting sample line items...")
        cursor.execute(
            """
        INSERT INTO line_items (order_id, sku, quantity, price, subtotal, supplier)
        VALUES 
            (%s, 'SKU001', 2, 15.0, 30.0, 'Supplier A'), -- Order 1
            (%s, 'SKU002', 1, 30.0, 30.0, 'Supplier B'), -- Order 1
            (%s, 'SKU003', 3, 35.0, 105.0, 'Supplier A'), -- Order 2
            (%s, 'SKU004', 1, 20.0, 20.0, 'Supplier C'), -- Order 2
            (%s, 'SKU005', 2, 40.0, 80.0, 'Supplier D'), -- Order 3
            (%s, 'SKU001', 1, 15.0, 15.0, 'Supplier A'), -- Order 4
            (%s, 'SKU002', 3, 30.0, 90.0, 'Supplier B')  -- Order 5
        """,
            (
                order_ids[0],
                order_ids[0],
                order_ids[1],
                order_ids[1],
                order_ids[2],
                order_ids[3],
                order_ids[4],
            ),
        )
        conn.commit()

        print("Sample data populated successfully.")
    except Exception as e:
        print(f"Error populating data: {e}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    populate_data()

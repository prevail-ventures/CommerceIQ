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
            ('SKU005', 'Product E', 30.0, 40.0, 60, 8.0),
            ('SKU006', 'Product F', 12.0, 18.0, 40, 6.0)
        """
        )
        conn.commit()

        # Insert sample orders
        print("Inserting sample orders...")
        cursor.execute(
            """
        INSERT INTO orders (order_total, actual_order_total, actual_shipping_cost, total_estimated_shipping_cost, 
                            projected_shipping_company, projected_shipping_method, actual_shipping_method, 
                            shipping_address_state, order_date)
        VALUES 
            (100.0, 95.0, 10.0, 8.0, 'FedEx', 'Standard', 'Overnight', 'CA', '2024-12-25'),  -- Positive differential
            (200.0, 190.0, 15.0, 20.0, 'UPS', '2-Day', 'Ground', 'TX', '2024-12-20'),       -- Negative differential
            (150.0, 140.0, 12.0, 12.0, 'USPS', 'Priority', 'Priority', 'NY', '2024-11-15'), -- Zero differential
            (250.0, 240.0, 18.0, 20.0, 'DHL', 'Express', 'Express', 'FL', '2024-09-01'),    -- Within last 3 months
            (300.0, 290.0, 20.0, 18.0, 'FedEx', 'Ground', 'Ground', 'WA', '2023-01-01'),    -- Outside last 6 months
            (50.0, 48.0, 5.5, 6.0, 'UPS', 'Standard', 'Standard', 'OR', '2024-12-30'),      -- Single order for SKU006
            (120.0, 115.0, 7.0, 10.0, 'USPS', 'First-Class', 'First-Class', 'AZ', '2024-12-28') -- Multiple orders for SKU006
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
        INSERT INTO line_items (order_id, sku, quantity, price, subtotal, supplier, subtotal_estimated_shipping_cost)
        VALUES 
            (%s, 'SKU001', 2, 15.0, 30.0, 'Supplier A', 10.0),  -- Order 1
            (%s, 'SKU002', 1, 30.0, 30.0, 'Supplier B', 7.0),  -- Order 1
            (%s, 'SKU003', 3, 35.0, 105.0, 'Supplier A', 19.5),-- Order 2
            (%s, 'SKU004', 1, 20.0, 20.0, 'Supplier C', 4.0),  -- Order 2
            (%s, 'SKU005', 2, 40.0, 80.0, 'Supplier D', 16.0), -- Order 3
            (%s, 'SKU001', 1, 15.0, 15.0, 'Supplier A', 5.0),  -- Order 4
            (%s, 'SKU006', 2, 18.0, 36.0, 'Supplier E', 12.0), -- Order 6
            (%s, 'SKU006', 1, 18.0, 18.0, 'Supplier E', 6.0)   -- Order 7
        """,
            (
                order_ids[0],
                order_ids[0],
                order_ids[1],
                order_ids[1],
                order_ids[2],
                order_ids[3],
                order_ids[5],
                order_ids[6],
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

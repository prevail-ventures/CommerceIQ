import os

from flask import Flask, render_template, request

from db_utils import get_db_connection

app = Flask(__name__)

# Configure the app based on environment
if os.getenv("FLASK_ENV") == "testing":
    app.config["TESTING"] = True
else:
    app.config["TESTING"] = False


@app.route("/", methods=["GET", "POST"])
def dashboard():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # Enable dictionary-like row access for MySQL

    # Default filter values
    date_filter = "last_7_days"
    supplier_filter = "all"

    if request.method == "POST":
        date_filter = request.form.get("date_filter", "last_7_days")
        supplier_filter = request.form.get("supplier_filter", "all")

    # Date filter SQL logic
    date_filter_conditions = {
        "last_7_days": "order_date >= DATE(NOW() - INTERVAL 7 DAY)",
        "last_14_days": "order_date >= DATE(NOW() - INTERVAL 14 DAY)",
        "last_month": "order_date >= DATE(NOW() - INTERVAL 1 MONTH)",
        "last_3_months": "order_date >= DATE(NOW() - INTERVAL 3 MONTH)",
        "last_6_months": "order_date >= DATE(NOW() - INTERVAL 6 MONTH)",
        "last_year": "order_date >= DATE(NOW() - INTERVAL 1 YEAR)",
    }
    date_condition = date_filter_conditions.get(
        date_filter, date_filter_conditions["last_7_days"]
    )

    # Supplier filter SQL logic
    supplier_condition = (
        f"supplier = '{supplier_filter}'" if supplier_filter != "all" else "1=1"
    )

    # Combine filters and execute query for orders
    filtered_query = f"""
    SELECT DISTINCT o.order_id, o.order_total, o.actual_shipping_cost, o.total_estimated_shipping_cost, o.order_date
    FROM orders o
    JOIN line_items li ON o.order_id = li.order_id
    WHERE {date_condition} AND {supplier_condition}
    """
    cursor.execute(filtered_query)
    orders = cursor.fetchall()

    # Sales Analytics
    sales_query = f"""
    SELECT 
        SUM(o.order_total) AS total_revenue,
        li.supplier,
        SUM(o.order_total) AS revenue_by_supplier
    FROM orders o
    JOIN line_items li ON o.order_id = li.order_id
    WHERE {date_condition} AND {supplier_condition}
    GROUP BY li.supplier
    """
    cursor.execute(sales_query)
    sales_data = cursor.fetchall()
    total_revenue = sum(item["revenue_by_supplier"] for item in sales_data)
    revenue_by_supplier = {
        item["supplier"]: item["revenue_by_supplier"] for item in sales_data
    }

    # Shipping Analytics
    shipping_query = f"""
    SELECT 
        SUM(o.actual_shipping_cost) AS total_actual_shipping,
        SUM(o.total_estimated_shipping_cost) AS total_estimated_shipping
    FROM orders o
    JOIN line_items li ON o.order_id = li.order_id
    WHERE {date_condition} AND {supplier_condition}
    """
    cursor.execute(shipping_query)
    shipping_data = cursor.fetchone()
    total_actual_shipping = shipping_data["total_actual_shipping"] or 0
    total_estimated_shipping = shipping_data["total_estimated_shipping"] or 0
    aggregate_shipping_differential = total_estimated_shipping - total_actual_shipping

    # Orders To Investigate
    orders_to_investigate_query = f"""
    SELECT DISTINCT o.order_id, o.order_total, o.actual_shipping_cost, o.total_estimated_shipping_cost, o.order_date,
    (o.total_estimated_shipping_cost - o.actual_shipping_cost) AS shipping_difference
    FROM orders o
    JOIN line_items li ON o.order_id = li.order_id
    WHERE {date_condition} AND {supplier_condition}
    HAVING shipping_difference < -1 OR shipping_difference > 1
    """
    cursor.execute(orders_to_investigate_query)
    orders_to_investigate = cursor.fetchall()

    # Fetch distinct suppliers for the dropdown
    cursor.execute("SELECT DISTINCT supplier FROM line_items")
    suppliers = [row["supplier"] for row in cursor.fetchall()]

    conn.close()

    return render_template(
        "dashboard.html",
        orders=orders,
        suppliers=suppliers,
        date_filter=date_filter,
        supplier_filter=supplier_filter,
        total_revenue=total_revenue,
        revenue_by_supplier=revenue_by_supplier,
        total_actual_shipping=total_actual_shipping,
        total_estimated_shipping=total_estimated_shipping,
        aggregate_shipping_differential=aggregate_shipping_differential,
        orders_to_investigate=orders_to_investigate,
    )


@app.route("/orders/<int:order_id>")
def order_details(order_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch order details
    cursor.execute(
        """
    SELECT o.order_id, o.actual_shipping_cost, o.order_date, o.order_total
    FROM orders o
    WHERE o.order_id = %s
    """,
        (order_id,),
    )
    order = cursor.fetchone()

    # Fetch line items with calculated estimated shipping subtotals
    cursor.execute(
        """
    SELECT 
        li.sku, 
        li.quantity, 
        li.price AS list_price, 
        li.subtotal, 
        (p.estimated_shipping_cost * li.quantity) AS estimated_shipping_subtotal,
        li.supplier
    FROM line_items li
    JOIN products p ON li.sku = p.sku
    WHERE li.order_id = %s
    """,
        (order_id,),
    )
    line_items = cursor.fetchall()

    # Calculate order subtotal (sum of all line item subtotals)
    order_subtotal = sum(item["subtotal"] for item in line_items)

    # Calculate total estimated shipping cost
    total_estimated_shipping_cost = sum(
        item["estimated_shipping_subtotal"] for item in line_items
    )

    # Calculate shipping differential
    shipping_differential = (
        total_estimated_shipping_cost - order["actual_shipping_cost"]
    )

    conn.close()

    return render_template(
        "order_details.html",
        order=order,
        line_items=line_items,
        order_subtotal=order_subtotal,
        total_estimated_shipping_cost=total_estimated_shipping_cost,
        shipping_differential=shipping_differential,
    )


@app.route("/products/<sku>")
def product_details(sku):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch product details
    cursor.execute(
        """
    SELECT 
        sku, 
        name, 
        cost, 
        listed_price, 
        inventory_level, 
        estimated_shipping_cost
    FROM products
    WHERE sku = %s
    """,
        (sku,),
    )
    product = cursor.fetchone()

    conn.close()

    if not product:
        return f"Product with SKU {sku} not found.", 404

    return render_template("product_details.html", product=product)


if __name__ == "__main__":
    app.run(debug=True)

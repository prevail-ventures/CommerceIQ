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
    SELECT DISTINCT o.order_id, o.order_total, o.actual_order_total, 
        o.actual_shipping_cost, o.total_estimated_shipping_cost, 
        o.projected_shipping_company, o.projected_shipping_method, 
        o.actual_shipping_method, o.shipping_address_state, o.order_date
    FROM orders o
    JOIN line_items li ON o.order_id = li.order_id
    WHERE {date_condition} AND {supplier_condition}
    """
    cursor.execute(filtered_query)
    orders = cursor.fetchall()

    # Sales Analytics
    sales_query = f"""
    SELECT 
        li.supplier AS supplier_name,
        SUM(o.order_total) AS total_revenue,
        SUM(o.actual_order_total) AS actual_totals
    FROM orders o
    JOIN line_items li ON o.order_id = li.order_id
    WHERE {date_condition} AND {supplier_condition}
    GROUP BY li.supplier
    """
    cursor.execute(sales_query)
    sales_data = cursor.fetchall()

    # Aggregate sales data
    revenue_by_supplier = []
    total_revenue = 0
    for item in sales_data:
        supplier_name = item["supplier_name"]
        total_revenue += item["total_revenue"]
        margin = (
            ((item["total_revenue"] - item["actual_totals"]) / item["total_revenue"])
            * 100
            if item["total_revenue"] > 0
            else 0
        )
        revenue_by_supplier.append(
            {
                "supplier_name": supplier_name,
                "total_revenue": item["total_revenue"],
                "margin": round(margin, 2),
            }
        )

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
    SELECT DISTINCT o.order_id, o.order_total, o.actual_order_total, 
        o.total_estimated_shipping_cost, o.actual_shipping_cost, 
        o.projected_shipping_company, o.projected_shipping_method, 
        o.actual_shipping_method, o.shipping_address_state, o.order_date,
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

    # Fetch line items
    cursor.execute(
        """
    SELECT 
        li.sku, 
        li.quantity, 
        li.price AS list_price, 
        li.subtotal, 
        (p.estimated_shipping_cost * li.quantity) AS estimated_shipping_subtotal,
        li.supplier,
        p.name,
        p.estimated_shipping_cost
    FROM line_items li
    JOIN products p ON li.sku = p.sku
    WHERE li.order_id = %s
    """,
        (order_id,),
    )
    line_items = cursor.fetchall()

    # Calculate order subtotal
    order_subtotal = sum(item["subtotal"] for item in line_items)

    # Calculate total estimated shipping cost
    total_estimated_shipping_cost = sum(
        item["estimated_shipping_subtotal"] for item in line_items
    )

    # Calculate shipping differential
    shipping_differential = (
        total_estimated_shipping_cost - order["actual_shipping_cost"]
    )

    # Fetch suggested actions for each product
    suggestions = []
    for item in line_items:
        sku = item["sku"]
        product_name = item["name"]
        current_estimated_shipping = item["estimated_shipping_cost"]

        # Fetch past orders for this product (last 6 months)
        cursor.execute(
            """
        SELECT actual_shipping_cost
        FROM orders o
        JOIN line_items li ON o.order_id = li.order_id
        WHERE li.sku = %s AND o.order_date >= DATE(NOW() - INTERVAL 6 MONTH)
        """,
            (sku,),
        )
        past_shipping_costs = [row["actual_shipping_cost"] for row in cursor.fetchall()]
        num_orders = len(past_shipping_costs)

        if num_orders > 0:
            # Calculate suggested estimated shipping cost
            average_actual_shipping = sum(past_shipping_costs) / num_orders
            suggested_estimated_shipping = max(
                average_actual_shipping, 0.01
            )  # Buffer to stay positive

            # Determine confidence color
            if num_orders <= 3:
                confidence_color = "red"
            elif 4 <= num_orders <= 10:
                confidence_color = "yellow"
            else:
                confidence_color = "green"

            # Add suggestion
            suggestions.append(
                {
                    "product_name": product_name,
                    "current_estimated_shipping": current_estimated_shipping,
                    "suggested_estimated_shipping": round(
                        suggested_estimated_shipping, 2
                    ),
                    "num_orders": num_orders,
                    "confidence_color": confidence_color,
                }
            )

    conn.close()

    return render_template(
        "order_details.html",
        order=order,
        line_items=line_items,
        order_subtotal=order_subtotal,
        total_estimated_shipping_cost=total_estimated_shipping_cost,
        shipping_differential=shipping_differential,
        suggestions=suggestions,
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

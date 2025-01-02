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
    if supplier_filter != "all":
        supplier_condition = f"supplier = '{supplier_filter}'"
    else:
        supplier_condition = "1=1"  # No supplier filter applied

    # Combine filters and execute query
    filtered_query = f"""
    SELECT DISTINCT o.order_id, o.order_total, o.actual_shipping_cost, o.total_estimated_shipping_cost, o.order_date
    FROM orders o
    JOIN line_items li ON o.order_id = li.order_id
    WHERE {date_condition} AND {supplier_condition}
    """
    cursor.execute(filtered_query)
    orders = cursor.fetchall()

    # Calculate aggregate shipping difference for filtered orders
    aggregate_query = f"""
    SELECT
        SUM(o.actual_shipping_cost) AS total_actual_shipping,
        SUM(o.total_estimated_shipping_cost) AS total_estimated_shipping
    FROM orders o
    JOIN line_items li ON o.order_id = li.order_id
    WHERE {date_condition} AND {supplier_condition}
    """
    cursor.execute(aggregate_query)
    result = cursor.fetchone()
    total_actual_shipping = result["total_actual_shipping"] or 0
    total_estimated_shipping = result["total_estimated_shipping"] or 0

    if total_estimated_shipping > 0:
        aggregate_difference = round(
            (
                (total_actual_shipping - total_estimated_shipping)
                / total_estimated_shipping
            )
            * 100,
            2,
        )
    else:
        aggregate_difference = 0.0

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
        aggregate_difference=aggregate_difference,
    )


if __name__ == "__main__":
    app.run(debug=True)

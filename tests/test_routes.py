def test_dashboard_combined_filters(client):
    """Test the dashboard with combined date and supplier filters."""
    # Filter by last 7 days and Supplier A
    response = client.post(
        "/", data={"date_filter": "last_7_days", "supplier_filter": "Supplier A"}
    )
    assert response.status_code == 200
    assert b"Test Product A" in response.data  # Verify Supplier A's orders appear
    assert b"Supplier B" not in response.data  # Verify Supplier B's orders are excluded

    # Filter by last month and Supplier B
    response = client.post(
        "/", data={"date_filter": "last_month", "supplier_filter": "Supplier B"}
    )
    assert response.status_code == 200
    assert b"Test Product B" in response.data  # Verify Supplier B's orders appear
    assert b"Supplier A" not in response.data  # Verify Supplier A's orders are excluded

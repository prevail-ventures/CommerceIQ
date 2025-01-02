import os
import sqlite3

import mysql.connector
from dotenv import load_dotenv
from flask import current_app, has_app_context

# Load environment variables
load_dotenv()


def get_db_connection():
    """Get a database connection based on the app's mode (testing or production)."""
    if has_app_context() and current_app.config.get("TESTING", False):
        # Use SQLite in-memory database for testing
        print("Using SQLite In-Memory Database")
        conn = sqlite3.connect(":memory:")  # In-memory database
        conn.row_factory = sqlite3.Row  # Enable dictionary-like row access for SQLite
    else:
        # Use MySQL for production or standalone scripts
        print("Using MySQL Database")
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )
    return conn

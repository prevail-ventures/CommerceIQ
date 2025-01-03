# CommerceIQ

CommerceIQ is a modular application designed to streamline the management and analytics of e-commerce dropshipping businesses. The app facilitates data acquisition, analysis, and visualization to help e-commerce managers optimize shipping costs, predict inventory needs, and gain actionable insights from business operations.

## Features

### Data Acquisition
- Retrieve data from APIs of internal and external systems.
- Support for occasional CSV imports.
- Scheduled daily data collection using AWS Lambda or cron jobs.

### Data Storage
- Store processed data in an SQL database (e.g., MySQL).
- Organized tables for products, orders, line items, and analytics metrics.
- Designed for extensibility to include new data points as needed.

### Analysis
- Analyze shipping cost variances (estimated vs. actual).
- Identify trends and suggest formula improvements.
- Predict inventory restocking needs based on demand trends.
- Expandable to include AI-driven insights and natural language queries.

### Display
- Intuitive dashboard with:
  - **Sales Analytics**: Total revenue, revenue by supplier.
  - **Shipping Analytics**: Total estimated shipping cost, total actual shipping cost, aggregate shipping differential, and flagged orders for investigation.
- Exportable data for reports in CSV or PDF formats.
- Backend built with Python (Flask) and a responsive HTML/CSS frontend.

## Tech Stack
- **Backend**: Python (Flask).
- **Frontend**: HTML, CSS.
- **Database**: MySQL hosted on AWS RDS.
- **Hosting**: AWS EC2 for the app, S3 for static assets.
- **Scheduling**: AWS Lambda or cron jobs.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/prevail-ventures/CommerceIQ.git
   ```

2. Navigate to the project directory:
   ```bash
   cd CommerceIQ
   ```

3. Set up a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Configure environment variables:
   - Create a `.env` file in the root directory.
   - Add variables for database connection, API keys, and AWS credentials:
     ```
     DB_HOST=localhost
     DB_PORT=3306
     DB_NAME=commerceiq
     DB_USER=youruser
     DB_PASSWORD=yourpassword
     ```

6. Initialize the database:
   ```bash
   python db_setup.py
   ```

7. Populate test data:
   ```bash
   python populate_data.py
   ```

8. Run the application locally:
   ```bash
   python app.py
   ```
   Access the app at `http://127.0.0.1:5000/`.

## Usage
- Use the dashboard to view metrics, apply filters, and access detailed order and product information.
- Set up API connections and data collection schedules through backend scripts.
- Export reports for further analysis or board presentations.

## Future Enhancements
- AI capabilities for advanced insights and recommendations.
- NLP-based assistant to answer user queries.
- Integration with additional data sources and third-party tools.
- Enhanced user management and role-based permissions.

## Contributing
We welcome contributions from the community. To contribute:
1. Fork the repository.
2. Create a feature branch: `git checkout -b feature-name`.
3. Commit changes: `git commit -m 'Add feature-name'`.
4. Push to the branch: `git push origin feature-name`.
5. Create a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Contact
For questions or support, please contact:
- **Name**: Austin Graham
- **Email**: austin.graham86@gmail.com
- **GitHub**: [austinlgraham](https://github.com/austinlgraham)

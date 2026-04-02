"""ETL Pipeline — Amman Digital Market Customer Analytics

Extracts data from PostgreSQL, transforms it into customer-level summaries,
validates data quality, and loads results to a database table and CSV file.
"""
from sqlalchemy import create_engine
import pandas as pd
import os


def extract(engine):
    """Extract all source tables from PostgreSQL into DataFrames.

    Args:
        engine: SQLAlchemy engine connected to the amman_market database

    Returns:
        dict: {"customers": df, "products": df, "orders": df, "order_items": df}
    """

    data_dict = {}

    data_dict["customers"] = pd.read_sql("SELECT * FROM customers", engine)
    data_dict["products"] = pd.read_sql("SELECT * FROM products", engine)
    data_dict["orders"] = pd.read_sql("SELECT * FROM orders", engine)
    data_dict["order_items"] = pd.read_sql("SELECT * FROM order_items", engine)
    
    return data_dict



def transform(data_dict):
    """Transform raw data into customer-level analytics summary.

    Steps:
    1. Join orders with order_items and products
    2. Compute line_total (quantity * unit_price)
    3. Filter out cancelled orders (status = 'cancelled')
    4. Filter out suspicious quantities (quantity > 100)
    5. Aggregate to customer level: total_orders, total_revenue,
       avg_order_value, top_category

    Args:
        data_dict: dict of DataFrames from extract()

    Returns:
        DataFrame: customer-level summary with columns:
            customer_id, customer_name, city, total_orders,
            total_revenue, avg_order_value, top_category
    """
    #read tables from data_dict and save each table to a variable
    customers = data_dict["customers"]
    products = data_dict["products"]
    orders = data_dict["orders"]
    order_items = data_dict["order_items"]

    # merged to know woh bought what
    merged = order_items.merge(orders, on="order_id")
    merged = merged.merge(products, on="product_id")

    # Compute line_total
    merged["line_total"] = merged["quantity"] * merged["unit_price"]

    # Filter out cancelled orders and suspicious quantities
    merged = merged[merged["status"] != "cancelled"]
    merged = merged[merged["quantity"] <= 100]

    # Aggregate to customer level
    customer_summary = merged.groupby("customer_id").agg(
        total_revenue=('line_total', 'sum'),
        total_orders=('order_id', 'nunique')
        ).reset_index()

    # Join with customers table to get customer details
    customer_summary = customer_summary.merge(customers, on="customer_id")

    # Compute average order value
    customer_summary["avg_order_value"] = customer_summary["total_revenue"] / customer_summary["total_orders"]

    # Determine top category for each customer
    top_category = merged.groupby(['customer_id', 'category'])['quantity'].sum().reset_index()
    top_category = top_category.sort_values(['customer_id', 'quantity'], ascending=[True, False])
    top_category = top_category.drop_duplicates(subset=['customer_id'], keep='first')
    top_category = top_category.rename(columns={'category': 'top_category'})[['customer_id', 'top_category']]
    
    # Merge top category back to customer summary
    customer_summary = customer_summary.merge(top_category, on='customer_id', how='left')
    # order of columns
    customer_summary = customer_summary[['customer_id', 'customer_name', 'city', 'total_orders', 'total_revenue', 'avg_order_value', 'top_category']]
    
    return customer_summary



def validate(df):
    """Run data quality checks on the transformed DataFrame.

    Checks:
    - No nulls in customer_id or customer_name
    - total_revenue > 0 for all customers
    - No duplicate customer_ids
    - total_orders > 0 for all customers

    Args:
        df: transformed customer summary DataFrame

    Returns:
        dict: {check_name: bool} for each check

    Raises:
        ValueError: if any critical check fails
    """
    checks = {}
    checks["no_nulls"] = df["customer_id"].notnull().all() and df["customer_name"].notnull().all()
    checks["positive_revenue"] = (df["total_revenue"] > 0).all()
    checks["no_duplicates"] = df["customer_id"].is_unique
    checks["positive_orders"] = (df["total_orders"] > 0).all()

    if not all(checks.values()):
        failed_checks = [k for k, v in checks.items() if not v]
        raise ValueError(f"Data validation failed for: {failed_checks}")


    return checks
    


def load(df, engine, csv_path):
    """Load customer summary to PostgreSQL table and CSV file.

    Args:
        df: validated customer summary DataFrame
        engine: SQLAlchemy engine
        csv_path: path for CSV output
    """
    df.to_sql("customer_summary", engine, if_exists="replace", index=False)
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    df.to_csv(csv_path, index=False)
    print(f"Data loaded to database and saved to {csv_path} successfully.")


def main():
    """Orchestrate the ETL pipeline: extract -> transform -> validate -> load."""
    # TODO: Implement main orchestration
    DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/amman_market")
    # 1. Create engine from DATABASE_URL env var (or default)
    engine = create_engine(DB_URL)
    CSV_PATH = "output/customer_analytics.csv"
    # 2. Extract
    print("Extracting data...")
    raw_data = extract(engine)
    # 3. Transform
    print("Transforming data...")
    transformed_data = transform(raw_data)

    # 4. Validate
    print("Validating data...")
    validate(transformed_data)

    # 5. Load to customer_summary table and output/customer_analytics.csv
    print("Loading data...")
    load(transformed_data, engine, CSV_PATH)
    
    print("ETL pipeline completed successfully!") 



if __name__ == "__main__":
    main()

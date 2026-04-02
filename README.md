[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/Nvxy3054)
# ETL Pipeline — Amman Digital Market

## Overview

<!-- What does this pipeline do? -->

This project implements a complete **ETL (Extract, Transform, Load)** pipeline for the Amman Digital Market. The pipeline is designed to automate the process of understanding customer purchasing behavior.


## Setup

1. Start PostgreSQL container:
   ```bash
   docker run -d --name postgres-m3-int \
     -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres \
     -e POSTGRES_DB=amman_market \
     -p 5432:5432 -v pgdata_m3_int:/var/lib/postgresql/data \
     postgres:15-alpine
   ```
2. Load schema and data:
   ```bash
   psql -h localhost -U postgres -d amman_market -f schema.sql
   psql -h localhost -U postgres -d amman_market -f seed_data.sql
   ```
3. Install dependencies: `pip install -r requirements.txt`

## How to Run

```bash
python etl_pipeline.py

To run the automated tests (using pytest)
```

## Output

<!-- What does customer_analytics.csv contain? -->
The pipeline successfully generates a clean, structured file named customer_analytics.csv.
This file contains a summarized view of each customer's lifetime value and preferences, including:

**customer_id & customer_name**: The customer's identity.
city: The customer's location.

**total_orders**: The total number of completed, valid orders.

**total_revenue**: The total money spent by the customer.

**avg_order_value**: The average amount spent per order.

**top_category**: The product category from which the customer bought the highest quantity of items.

## Quality Checks

<!-- What validations are performed and why? -->

## Quality Checks & Automated Testing

To ensure the analytics team receives 100% accurate data, the pipeline enforces strict validation rules backed by an automated `pytest` suite:

1. **Data Integrity (`test_validate_catches_nulls`):** 
   The `validate()` function ensures there are no `NULL` values in `customer_id` or `customer_name`, and guarantees no duplicate customers. If any are found, the pipeline halts immediately with a `ValueError`.

2. **Valid Transactions Only (`test_transform_filters_cancelled`):** 
   The transformation logic strictly excludes any orders marked as 'cancelled' to prevent inflated revenue and order counts.

3. **Outlier Detection (`test_transform_filters_suspicious_quantity`):** 
   Unrealistic and suspicious order quantities (e.g., > 100 items) are successfully filtered out to ensure the `avg_order_value` remains mathematically accurate.

4. **Financial Accuracy:** 
   Before loading to the database, the pipeline validates that both `total_revenue` and `total_orders` are strictly greater than 0 for all active customers.
   
---

## License

This repository is provided for educational use only. See [LICENSE](LICENSE) for terms.

You may clone and modify this repository for personal learning and practice, and reference code you wrote here in your professional portfolio. Redistribution outside this course is not permitted.

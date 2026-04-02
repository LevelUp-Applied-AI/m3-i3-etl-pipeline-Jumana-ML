"""Tests for the ETL pipeline.

Write at least 3 tests:
1. test_transform_filters_cancelled — cancelled orders excluded after transform
2. test_transform_filters_suspicious_quantity — quantities > 100 excluded
3. test_validate_catches_nulls — validate() raises ValueError on null customer_id
"""
import pandas as pd
import pytest
from etl_pipeline import transform, validate

def test_transform_filters_cancelled():
    """Create test DataFrames with a cancelled order. Confirm it's excluded."""
    data_dict = {"customers": pd.DataFrame({
                            "customer_id": [1],
                            "customer_name": ["jumana"],
                            "city": ["Amman"]
                        }),
                 "products": pd.DataFrame({
                            "product_id": [1],
                            "product_name": ["Product A"],
                            "category": ["Electronics"]
                        }),
                 "orders": pd.DataFrame({
                            "order_id": [100,101],
                            "customer_id": [1,1],
                            "status": ["cancelled", "completed"]
                        }),
                 "order_items": pd.DataFrame({
                            "order_id": [100,101],
                            "product_id": [1,1],
                            "quantity": [5, 20],
                            "unit_price": [100.0, 100.0 ]
                        })
                    }
    result = transform(data_dict)
    assert result["total_orders"].iloc[0] == 1


def test_transform_filters_suspicious_quantity():
    """Create test DataFrames with quantity > 100. Confirm it's excluded."""
    data_dict = {"customers": pd.DataFrame({
                            "customer_id": [2],
                            "customer_name": ["shaden"],
                            "city": ["Amman"]
                        }),
                        "products": pd.DataFrame({
                            "product_id": [10],
                            "product_name": ["Product B"],
                            "category": ["Clothing"]
                        }),
                    "orders": pd.DataFrame({
                            "order_id": [200,201],
                            "customer_id": [2,2],
                            "status": ["completed", "completed"]
                        }),
                        "order_items": pd.DataFrame({
                            "order_id": [200,201],
                            "product_id": [10,10],
                            "quantity": [5, 150],
                            "unit_price": [10.0, 10.0 ]
                        })
                    }
    result = transform(data_dict)
    assert result["total_revenue"].iloc[0] == 50


def test_validate_catches_nulls():
    """Create a DataFrame with null customer_id. Confirm validate() raises ValueError."""
    bad_df = pd.DataFrame({
        "customer_id": [None],
        "customer_name": ["jumana"],
        "city": ["Amman"],
        "total_orders": [2],
        "total_revenue": [150.0],
        "avg_order_value": [75.0],
        "top_category": ["Electronics"]
    })
    with pytest.raises(ValueError):
        validate(bad_df)
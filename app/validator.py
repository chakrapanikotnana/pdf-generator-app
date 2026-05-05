import pandas as pd


def is_blank(value):
    return pd.isna(value) or str(value).strip() == ""


def validate_excel(df):
    errors = []

    required_columns = ["Drawing", "FileName", "Type"]

    # Check required columns
    for col in required_columns:
        if col not in df.columns:
            errors.append(f"Missing column: {col}")

    # Row-level checks
    for i, row in df.iterrows():
        if is_blank(row.get("Drawing")):
            errors.append(f"Row {i+1}: Drawing is missing")

        if is_blank(row.get("FileName")):
            errors.append(f"Row {i+1}: FileName is missing")

    return errors

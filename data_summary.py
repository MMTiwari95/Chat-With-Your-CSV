import pandas as pd


def get_data_summary(df: pd.DataFrame):
    """
    Generate a complete dataset summary.
    """

    summary = {
        "total_rows": int(df.shape[0]),
        "total_columns": int(df.shape[1]),
        "columns": df.columns.tolist(),
        "data_types": {
            column: str(dtype)
            for column, dtype in df.dtypes.items()
        },
        "missing_values": {
            column: int(value)
            for column, value in df.isnull().sum().items()
            if value > 0
        },
        "duplicate_rows": int(
            df.duplicated().sum()
        ),
        "numeric_columns": df.select_dtypes(
            include="number"
        ).columns.tolist(),
        "categorical_columns": df.select_dtypes(
            exclude="number"
        ).columns.tolist(),
    }

    return summary

import pandas as pd


def loader_csv(file) -> pd.DataFrame:
    """
    Load a CSV file into a Pandas DataFrame.

    Parameters:
        file: CSV file object.

    Returns:
        pd.DataFrame: Loaded dataset.

    Raises:
        ValueError: If the CSV file cannot be loaded.
    """
    try:
        return pd.read_csv(file)

    except Exception as e:
        raise ValueError(
            f"Error loading CSV file: {e}"
        ) from e

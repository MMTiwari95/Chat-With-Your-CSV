
import pandas as pd

def analyze_data(df: pd.DataFrame,operation: str,column: str = None,group_by: str = None):
    """Perform reliable data analysis on the complete dataset.Supported operations: -shape -columns -head -describe -missing_values -duplicates -mean -sum -min -max -count -unique -value_counts -group_mean -group_sum -group_count -top -bottom -correlation -financial_comparison"""

    # BASIC VALIDATION
    if df is None:
        raise ValueError("Dataset is empty.")
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input data must be a Pandas DataFrame.")
    if df.empty:
        raise ValueError("Dataset contains no rows.")
    # Work on a copy
    data = df.copy()
    # Clean column names
    data.columns = (data.columns.astype(str).str.strip())
    # Clean operation
    operation = str(operation).strip().lower()
    # BASIC OPERATIONS
    if operation == "shape":
        return {"rows": int(data.shape[0]),"columns": int(data.shape[1])}
    elif operation == "columns":
        return data.columns.tolist()
    elif operation == "head":
        return data.head(10)
    elif operation == "describe":
        return data.describe(include="all")
    elif operation == "missing_values":
        return (data.isnull().sum().sort_values(ascending=False))
    elif operation == "duplicates":
        return {"duplicate_rows": int(data.duplicated().sum())}
    # FINANCIAL COMPARISON
    elif operation == "financial_comparison":
        required_columns = ["Year","Variable_name","Value"]
        # CHECK REQUIRED COLUMNS
        missing_columns = [col for col in required_columns if col not in data.columns]

        if missing_columns:
            raise ValueError("Financial comparison requires" f"columns: {required_columns}." f"Missing columns: {missing_columns}")
        # CLEAN YEAR
        data["Year"] = pd.to_numeric(data["Year"],errors="coerce")
        # CLEAN VALUE
        data["Value"] = (data["Value"].astype(str).str.replace(",","",regex=False).str.replace("$","",regex=False).str.strip())
        data["Value"] = pd.to_numeric(data["Value"],errors="coerce")
        # CLEAN VARIABLE NAME
        data["Variable_name"] = (data["Variable_name"].astype(str).str.strip().str.lower())
        # REMOVE INVALID DATA
        data = data.dropna(subset=["Year","Value"])
        # FIND TOTAL INCOME
        income_df = data[data["Variable_name"]== "total income"]
        # FIND TOTAL EXPENDITURE
        expenditure_df = data[data["Variable_name"]== "total expenditure"]
        # VALIDATE INCOME
        if income_df.empty:
            raise ValueError("No records found for " "'Total income'.")
        # VALIDATE EXPENDITURE
        if expenditure_df.empty:
            raise ValueError("No records found for " "'Total expenditure'.")
        # GROUP ONLY BY YEAR
        income_result = (income_df.groupby("Year",dropna=False)["Value"].sum().reset_index().rename(columns={"Value": "Total Income"}))
        expenditure_result = (expenditure_df.groupby("Year",dropna=False)["Value"].sum().reset_index().rename(columns={"Value": "Total Expenditure"}))
        # MERGE INCOME + EXPENDITURE
        result = (income_result.merge(expenditure_result,on="Year",how="outer"))
        # HANDLE MISSING VALUES
        result["Total Income"] = (result["Total Income"].fillna(0))
        result["Total Expenditure"] = (result["Total Expenditure"].fillna(0))
        # CALCULATE DIFFERENCE
        result["Difference"] = (result["Total Income"]-result["Total Expenditure"])
        # CALCULATE STATUS
        result["Status"] = (
            result["Difference"]
            .apply(
                lambda x:
                "Income Higher"
                if x > 0
                else (
                    "Expenditure Higher"
                    if x < 0
                    else "Equal"
                )
            )
        )
        # SORT BY YEAR
        result = (result.sort_values(by="Year").reset_index(drop=True))
        return result

    # OPERATIONS THAT REQUIRE COLUMN
    column_operations = ["mean", "sum", "min", "max", "count", "unique", "value_counts", "top", "bottom", "group_mean", "group_sum"]
    if operation in column_operations:
        if not column:
            raise ValueError(f"Column name is required " f"for operation '{operation}'.")
        if column not in data.columns:
            raise ValueError(f"Column '{column}' " "does not exist.")
    # COUNT
    if operation == "count":
        return int(data[column].count())
    # UNIQUE
    elif operation == "unique":
        return (data[column].dropna().unique().tolist())
    # VALUE COUNTS
    elif operation == "value_counts":
        return (data[column].value_counts())
    # NUMERIC CONVERSION
    if operation in [ "mean", "sum", "min", "max", "group_mean", "group_sum", "top", "bottom"]:
        numeric_series = (data[column].astype(str).str.replace(",", "", regex=False).str.replace("$", "", regex=False).str.strip())
        numeric_series = pd.to_numeric(numeric_series, errors="coerce")

        if numeric_series.dropna().empty:
            raise ValueError(f"Column '{column}'" "does not contain valid " "numeric values.")
    # MEAN
    if operation == "mean":
        return float(numeric_series.mean())
    # SUM
    elif operation == "sum":
        return float(numeric_series.sum())
    # MIN
    elif operation == "min":
        return float(numeric_series.min())
    # MAX
    elif operation == "max":
        return float(numeric_series.max())
    # GROUP MEAN
    elif operation == "group_mean":
        if not group_by:
            raise ValueError("Group-by column is required.")
        if group_by not in data.columns:
            raise ValueError(f"Column '{group_by}'" "does not exist.")

        temp = data.copy()
        temp["_numeric_value_"] = (numeric_series)
        result = (temp.dropna(subset=[group_by,"_numeric_value_"]).groupby(group_by,dropna=False)["_numeric_value_"].mean().sort_values(ascending=False))

        return result

    # GROUP SUM
    elif operation == "group_sum":
        if not group_by:
            raise ValueError("Group-by column is required.")
        if group_by not in data.columns:
            raise ValueError(f"Column '{group_by}'" "does not exist.")

        temp = data.copy()
        temp["_numeric_value_"] = (numeric_series)
        result = (temp.dropna(subset=[group_by,"_numeric_value_"]).groupby(group_by,dropna=False)["_numeric_value_"].sum().sort_values(ascending=False))

        return result
    # GROUP COUNT
    elif operation == "group_count":
        if not group_by:
            raise ValueError("Group-by column is required.")

        if group_by not in data.columns:
            raise ValueError(f"Column '{group_by}'" "does not exist.")
        return (data.groupby(group_by,dropna=False).size().sort_values(ascending=False ))
    # TOP 10
    elif operation == "top":

        temp = data.copy()
        temp["_numeric_value_"] = (numeric_series)
        return (temp.dropna(subset=["_numeric_value_"]).sort_values(by="_numeric_value_",ascending=False).head(10).drop(columns=["_numeric_value_"]))

    # BOTTOM 10
    elif operation == "bottom":
        temp = data.copy()
        temp["_numeric_value_"] = (numeric_series)
        return (temp.dropna(subset=["_numeric_value_"]).sort_values(by="_numeric_value_",ascending=True).head(10).drop(columns=["_numeric_value_"]))

    # CORRELATION
    elif operation == "correlation":
        numeric_df = (data.select_dtypes(include="number"))

        if numeric_df.empty:
            raise ValueError("No numeric columns" "available for correlation.")
        return (numeric_df.corr())
    # UNSUPPORTED OPERATION
    else:
        raise ValueError(f"Unsupported operation:" f"{operation}")


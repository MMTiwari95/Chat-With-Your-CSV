import os
import json
import hashlib

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

from utils.loader_csv import loader_csv
from tools.data_summary import get_data_summary
from tools.data_analysis import analyze_data


st.set_page_config(
    page_title="Chat With Your CSV",
    page_icon="📊",
    layout="wide",
)

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error(
        "❌ GROQ_API_KEY is missing.\n\n"
        "Please add GROQ_API_KEY to your .env file."
    )
    st.stop()

client = Groq(api_key=GROQ_API_KEY)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "dataframe" not in st.session_state:
    st.session_state.dataframe = None
if "file_hash" not in st.session_state:
    st.session_state.file_hash = None

with st.sidebar:
    st.title("⚙️ Settings")
    st.divider()

    st.subheader("🤖 Model Settings")
    model_name = st.selectbox(
        "Select AI Model",
        options=[
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile",
        ],
        index=0,
    )

    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.1,
        step=0.1,
        help="Lower values provide more consistent answers.",
    )

    max_tokens = st.slider(
        "Max Response Tokens",
        min_value=500,
        max_value=3000,
        value=1200,
        step=100,
    )

    st.divider()

    st.subheader("💬 Chat Controls")
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    st.subheader("📊 Dataset")
    if st.session_state.dataframe is not None:
        current_df = st.session_state.dataframe
        st.success("CSV Loaded ✅")
        st.write(f"**Rows:** {current_df.shape[0]}")
        st.write(f"**Columns:** {current_df.shape[1]}")
        st.write(
            f"**Missing Values:** "
            f"{int(current_df.isnull().sum().sum())}"
        )
    else:
        st.info("Upload a CSV file to start.")

    st.divider()

    st.subheader("ℹ️ About")
    st.write(
        "Chat With Your CSV is an AI-powered "
        "data analysis application using Pandas "
        "and Groq LLMs."
    )

st.title("📊 Chat With Your CSV")
st.caption(
    "Upload your CSV and ask questions about "
    "your data using AI."
)

uploaded_file = st.file_uploader(
    "📂 Upload your CSV file",
    type=["csv"],
)

if uploaded_file is not None:
    try:
        file_bytes = uploaded_file.getvalue()
        current_file_hash = hashlib.md5(file_bytes).hexdigest()

        if st.session_state.file_hash != current_file_hash:
            st.session_state.messages = []
            uploaded_file.seek(0)

            df = loader_csv(uploaded_file)
            df.columns = df.columns.astype(str).str.strip()

            if "Value" in df.columns:
                value_series = (
                    df["Value"]
                    .astype(str)
                    .str.replace(",", "", regex=False)
                    .str.replace("$", "", regex=False)
                    .str.strip()
                )
                df["Value"] = pd.to_numeric(
                    value_series,
                    errors="coerce",
                )

            if "Year" in df.columns:
                df["Year"] = pd.to_numeric(
                    df["Year"],
                    errors="coerce",
                )

            st.session_state.dataframe = df
            st.session_state.file_hash = current_file_hash
            st.success("CSV uploaded successfully! ✅")

    except Exception as e:
        st.error(f"❌ Error loading CSV: {e}")
        st.stop()

df = st.session_state.dataframe

if df is not None:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Rows", df.shape[0])

    with col2:
        st.metric("Total Columns", df.shape[1])

    with col3:
        st.metric(
            "Missing Values",
            int(df.isnull().sum().sum()),
        )

    with st.expander("👀 Preview Dataset"):
        st.dataframe(
            df.head(20),
            use_container_width=True,
        )

    with st.expander("📋 Dataset Summary"):
        try:
            summary = get_data_summary(df)
            st.json(summary)
        except Exception as e:
            st.warning(
                f"Could not generate summary: {e}"
            )

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input(
        "Ask a question about your CSV..."
    )

    if question:
        st.session_state.messages.append(
            {
                "role": "user",
                "content": question,
            }
        )

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner(
                "🔍 Analyzing your data..."
            ):
                try:
                    question_lower = question.strip().lower()

                    financial_keywords = [
                        "total income",
                        "total expenditure",
                        "income and expenditure",
                        "income vs expenditure",
                        "income versus expenditure",
                        "income - expenditure",
                        "income minus expenditure",
                    ]

                    is_financial_question = any(
                        keyword in question_lower
                        for keyword in financial_keywords
                    )

                    if is_financial_question:
                        operation = "financial_comparison"
                        column = "Value"
                        group_by = "Year"
                    else:
                        metadata = {
                            "rows": int(df.shape[0]),
                            "columns": df.columns.tolist(),
                            "numeric_columns": (
                                df.select_dtypes(
                                    include="number"
                                )
                                .columns
                                .tolist()
                            ),
                            "categorical_columns": (
                                df.select_dtypes(
                                    exclude="number"
                                )
                                .columns
                                .tolist()
                            ),
                        }

                        planning_prompt = f"""
You are a Pandas data analysis planner.

Dataset columns:
{json.dumps(metadata["columns"])}

Numeric columns:
{json.dumps(metadata["numeric_columns"])}

User question:
{question}

Choose exactly ONE operation:
shape columns head describe missing_values duplicates
mean sum min max count unique value_counts group_mean
group_sum group_count top bottom correlation

Rules:
- Average/mean -> mean
- Total/sum -> sum
- Highest -> top
- Lowest -> bottom
- Compare by year/category -> group_sum
- Average by year/category -> group_mean
- Total by year/category -> group_sum
- Never use mean on string columns
- Use exact column names only

Return ONLY JSON:
{{
    "operation": "operation_name",
    "column": null,
    "group_by": null
}}
"""

                        planning_response = (
                            client.chat.completions.create(
                                model=model_name,
                                messages=[
                                    {
                                        "role": "system",
                                        "content": planning_prompt,
                                    }
                                ],
                                temperature=0,
                                max_tokens=200,
                                response_format={
                                    "type": "json_object"
                                },
                            )
                        )

                        plan_text = (
                            planning_response
                            .choices[0]
                            .message
                            .content
                        )

                        try:
                            plan = json.loads(plan_text)
                        except json.JSONDecodeError as exc:
                            raise ValueError(
                                "AI returned invalid analysis plan."
                            ) from exc

                        operation = plan.get("operation")
                        column = plan.get("column")
                        group_by = plan.get("group_by")

                    allowed_operations = [
                        "shape",
                        "columns",
                        "head",
                        "describe",
                        "missing_values",
                        "duplicates",
                        "mean",
                        "sum",
                        "min",
                        "max",
                        "count",
                        "unique",
                        "value_counts",
                        "group_mean",
                        "group_sum",
                        "group_count",
                        "top",
                        "bottom",
                        "correlation",
                        "financial_comparison",
                    ]

                    if operation not in allowed_operations:
                        raise ValueError(
                            f"Invalid analysis operation: "
                            f"{operation}"
                        )

                    if column and column not in df.columns:
                        raise ValueError(
                            f"Column '{column}' does not exist."
                        )

                    if group_by and group_by not in df.columns:
                        raise ValueError(
                            f"Group-by column '{group_by}' "
                            f"does not exist."
                        )

                    result = analyze_data(
                        df=df,
                        operation=operation,
                        column=column,
                        group_by=group_by,
                    )

                    if result is None:
                        raise ValueError(
                            "No analysis result was returned."
                        )

                    max_result_rows = 100

                    if isinstance(result, pd.DataFrame):
                        if result.empty:
                            result_text = (
                                "Analysis returned an empty result."
                            )
                        else:
                            if operation == "financial_comparison":
                                compact_result = (
                                    result.sort_values(
                                        by="Year"
                                    ).head(max_result_rows)
                                )
                            else:
                                compact_result = result.head(
                                    max_result_rows
                                )

                            result_text = (
                                compact_result.to_string(
                                    index=False
                                )
                            )

                            if len(result) > max_result_rows:
                                result_text += (
                                    f"\n\nShowing first "
                                    f"{max_result_rows} rows "
                                    f"out of {len(result)} rows."
                                )

                    elif isinstance(result, pd.Series):
                        if result.empty:
                            result_text = (
                                "Analysis returned an empty result."
                            )
                        else:
                            compact_result = result.head(
                                max_result_rows
                            )
                            result_text = compact_result.to_string()

                            if len(result) > max_result_rows:
                                result_text += (
                                    f"\n\nShowing first "
                                    f"{max_result_rows} results "
                                    f"out of {len(result)}."
                                )

                    elif isinstance(result, dict):
                        result_text = json.dumps(
                            result,
                            indent=2,
                            default=str,
                        )
                    else:
                        result_text = str(result)

                    final_prompt = f"""
You are a data analyst.

User question:
{question}

Verified Pandas result:
{result_text}

Answer ONLY using the verified result.

Rules:
1. Never invent numbers.
2. Never invent missing data.
3. Do not make unsupported assumptions.
4. Clearly answer the user's question.
5. Use a Markdown table when useful.
6. For financial comparison, explain:
   - Total Income
   - Total Expenditure
   - Difference
   - Status
7. If data is unavailable, say so clearly.
8. Keep the answer concise.
"""

                    final_response = (
                        client.chat.completions.create(
                            model=model_name,
                            messages=[
                                {
                                    "role": "system",
                                    "content": final_prompt,
                                }
                            ],
                            temperature=temperature,
                            max_tokens=max_tokens,
                        )
                    )

                    answer = (
                        final_response
                        .choices[0]
                        .message
                        .content
                    )

                    st.markdown(answer)

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": answer,
                        }
                    )

                    with st.expander(
                        "🔍 Analysis Details"
                    ):
                        st.write(
                            "Selected Operation:",
                            operation,
                        )
                        st.write(
                            "Selected Column:",
                            column,
                        )
                        st.write(
                            "Group By:",
                            group_by,
                        )
                        st.write(
                            "Raw Pandas Result:"
                        )

                        if isinstance(
                            result,
                            (pd.DataFrame, pd.Series),
                        ):
                            st.dataframe(
                                result,
                                use_container_width=True,
                            )
                        else:
                            st.write(result)

                except Exception as e:
                    error_text = str(e)

                    if (
                        "413" in error_text
                        or "tokens per minute"
                        in error_text.lower()
                        or "request too large"
                        in error_text.lower()
                    ):
                        error_message = (
                            "Groq request is too large.\n\n"
                            "The dataset analysis result "
                            "contains too much data for "
                            "the selected AI model.\n\n"
                            "Try using a smaller result "
                            "or ask a more specific question."
                        )
                    else:
                        error_message = (
                            f"Error: {error_text}"
                        )

                    st.error(error_message)

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": error_message,
                        }
                    )
else:
    st.info(
        "👆 Please upload a CSV file "
        "to start analyzing your data."
    )

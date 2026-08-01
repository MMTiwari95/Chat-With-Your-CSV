# 📊 Chat With Your CSV – AI-Powered Data Analyst

An AI-powered CSV data analysis application built with **Python, Streamlit, Pandas, and Groq LLMs**.

Upload a CSV file, ask questions in natural language, and get answers based on verified Pandas calculations rather than unsupported AI guesses.

---

## ✨ Features

- 📂 Upload CSV files directly in the browser
- 👀 Preview the uploaded dataset
- 📋 Automatic dataset summary
- 📊 Row, column, and missing-value metrics
- 🤖 Groq-powered natural-language question understanding
- 🧠 AI analysis planner
- 🐼 Verified Pandas-based calculations
- 📈 Year-wise and category-wise analysis
- 💰 Income vs. expenditure comparison
- 🔢 Statistical operations
- 🔍 Analysis details with raw Pandas results
- 💬 Chat history
- 🗑️ Clear chat
- ⚙️ Select supported Groq models
- 🌡️ Adjustable response temperature
- 🚨 Large-result / token-limit error handling

---

## 🏗️ Project Architecture

```text
User uploads CSV
       │
       ▼
  loader_csv.py
       │
       ▼
 Pandas DataFrame
       │
       ├──────────────► data_summary.py
       │                      │
       │                      ▼
       │                Dataset Metadata
       │
       ▼
 User asks a question
       │
       ▼
    Groq AI Planner
       │
       ▼
 Select analysis operation
       │
       ▼
  data_analysis.py
       │
       ▼
 Verified Pandas Result
       │
       ▼
    Groq Final Response
       │
       ▼
      Answer
```

The application follows a **calculate first, explain second** approach:

1. The AI planner interprets the user's question.
2. The selected operation is validated.
3. Pandas performs the actual calculation.
4. The verified result is passed to the final LLM.
5. The LLM explains only the verified result.

This reduces the risk of hallucinated numerical answers.

---

## 📁 Project Structure

```text
chat-with-your-csv/
│
├── app.py
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── utils/
│   ├── __init__.py
│   └── loader_csv.py
│
├── tools/
│   ├── __init__.py
│   ├── data_analysis.py
│   └── data_summary.py
│
└── assets/
    └── screenshots/
```

---

## 🛠️ Technologies Used

- **Python**
- **Pandas**
- **Streamlit**
- **Groq API**
- **LLM-based planning**
- **python-dotenv**

---

## ⚙️ Supported Analysis Operations

| Operation | Description |
|---|---|
| `shape` | Get dataset row and column counts |
| `columns` | List all column names |
| `head` | Show the first 10 rows |
| `describe` | Generate statistical description |
| `missing_values` | Find missing values |
| `duplicates` | Count duplicate rows |
| `mean` | Calculate average |
| `sum` | Calculate total |
| `min` | Find minimum |
| `max` | Find maximum |
| `count` | Count non-null values |
| `unique` | Find unique values |
| `value_counts` | Count value frequency |
| `group_mean` | Calculate group-wise average |
| `group_sum` | Calculate group-wise total |
| `group_count` | Count records by group |
| `top` | Find top 10 numeric records |
| `bottom` | Find bottom 10 numeric records |
| `correlation` | Calculate numeric correlations |
| `financial_comparison` | Compare total income and expenditure by year |

---

## 💰 Financial Comparison

For datasets containing:

- `Year`
- `Variable_name`
- `Value`

the application can compare:

- Total Income
- Total Expenditure
- Difference
- Status

Possible status values:

- `Income Higher`
- `Expenditure Higher`
- `Equal`

Example question:

> Compare total income and total expenditure for each year.

---

## 💡 Example Questions

### Basic

- How many rows are in the dataset?
- What are the column names?
- Show me the first 10 rows.
- How many duplicate rows are there?
- Are there any missing values?

### Statistics

- What is the average value?
- What is the total value?
- What is the highest value?
- What is the lowest value?

### Year-wise Analysis

- What is the total value for each year?
- What is the average value for each year?
- Compare values across different years.
- Which year has the highest value?

### Financial Analysis

- Compare total income and total expenditure for each year.
- Calculate the difference between total income and total expenditure.
- Which years have higher income than expenditure?

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/chat-with-your-csv.git
cd chat-with-your-csv
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Create a Virtual Environment

Windows:

```bash
python -m venv .venv
```

Activate it in PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks script execution:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Then activate again:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Groq API Key

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Run the Application

```bash
python -m streamlit run app.py
```

The application will open in your browser.

---

## 🔐 Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | API key used to access Groq LLMs |

Use `.env.example` as a template.

---

## 🧠 AI + Data Analysis Workflow

The application uses two AI interactions:

### 1. AI Planner

The first LLM call determines which Pandas analysis operation should be used.

Example:

```text
User:
What is the total value for each year?

AI Planner:
operation = group_sum
column = Value
group_by = Year
```

### 2. Verified Data Analysis

The selected operation is executed using Pandas.

```text
AI Planner
    ↓
Pandas Analysis
    ↓
Verified Result
```

### 3. Final AI Response

The verified result is passed to the final LLM, which generates a concise natural-language answer.

This architecture helps keep numerical answers grounded in the actual dataset.

---

## 🛡️ Security

---

## 🔮 Future Improvements

- [ ] Add interactive charts and visualizations
- [ ] Support Excel files
- [ ] Add downloadable analysis reports
- [ ] Add conversational memory across datasets
- [ ] Add automatic chart recommendations
- [ ] Add more advanced AI agents
- [ ] Add SQL-based analysis
- [ ] Add multi-file analysis
- [ ] Deploy the application online
- [ ] Add authentication
- [ ] Add automated testing

---

## 👨‍💻 Author

**Murli Manohar Tiwari**

B.Tech Computer Science & Engineering Student  
Interested in Python, Data Analytics, Artificial Intelligence, Machine Learning, Generative AI, LLMs, and AI Agents.

---

## ⭐ If You Like This Project

If this project helped you or you found it interesting, consider giving the repository a ⭐ on GitHub.

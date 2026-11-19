# Student Performance Analysis

A Streamlit dashboard for exploring class performance, subject results, attendance, student risk levels and a simple study-habits prediction model.

## Features

- Upload a class dataset as a CSV or use the included sample dataset.
- Clean and prepare student records.
- Calculate totals, averages, percentages, grades, ranks, failures and risk levels.
- Explore class insights, subject comparisons, grade distribution and leaderboard.
- Inspect an individual student and compare their results with the class or another student.
- Analyse attendance and its relationship with marks.
- Estimate marks from study hours and attendance using a simple linear regression model.
- Download student reports, processed results and a CSV template.

## Tech stack

- Python
- Streamlit
- Pandas and NumPy
- Plotly
- scikit-learn

## Run locally

Python 3.10 or newer is recommended.

```bash
# 1. Create and activate a virtual environment
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# 2. Install dependencies
python -m pip install -r requirements.txt

# 3. Start the app
streamlit run app.py
```

Open the local URL printed by Streamlit, usually `http://localhost:8501`.

## CSV format

Required columns:

- `Name`
- `Attendance` (percentage, 0–100)
- `Study_Hours` (daily study hours)
- At least one subject column containing marks out of 100

`Student_ID` is optional. Subject columns can have any names, as long as they are not one of the reserved fields used by the app.

Example:

```csv
Student_ID,Name,Math,Science,English,Attendance,Study_Hours
S001,Example Student,75,80,70,90,3.5
```

## Project structure

```text
student_performance/
├── .streamlit/
│   └── config.toml
├── app.py
├── analysis.py
├── charts.py
├── students.csv
├── requirements.txt
├── .gitignore
└── README.md
```

## Notes

- The prediction is a simple estimate based on the available dataset. It is not a guarantee of future marks; interpret it cautiously, especially with small datasets.
- The included `students.csv` is sample data. Replace it with an appropriate dataset or upload your own CSV in the app.

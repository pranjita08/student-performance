"""Modules 1-4 + extras: loading, cleaning, performance, subject analysis,
attendance analysis, risk detection, insights and a simple ML predictor."""
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import cross_val_score

DERIVED_COLS = ["Total", "Average", "Percentage", "Grade", "Rank", "Fails", "Risk"]
NON_SUBJECT_COLS = ["Student_ID", "Name", "Attendance", "Study_Hours"] + DERIVED_COLS
PASS_MARK = 40
MAX_MARK = 100
LOW_ATTENDANCE = 75


# ---------- Module 1: Dataset loading ----------
def load_data(source) -> pd.DataFrame:
    """Load a CSV from a file path or an uploaded file object."""
    return pd.read_csv(source)


# ---------- Module 2: Data cleaning ----------
def get_subject_columns(df: pd.DataFrame) -> list:
    return [c for c in df.columns if c not in NON_SUBJECT_COLS]


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Tidy column names, drop duplicates, fix missing/invalid values."""
    df = df.copy()
    df.columns = [c.strip().replace(" ", "_") for c in df.columns]
    df = df.drop_duplicates()
    df = df.dropna(subset=["Name"])
    df["Name"] = df["Name"].astype(str).str.strip()

    subjects = get_subject_columns(df)
    for col in subjects + ["Attendance", "Study_Hours"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in subjects:  # marks: fill gaps with subject median, keep in 0-100
        df[col] = df[col].fillna(df[col].median()).clip(0, MAX_MARK)
    if "Attendance" in df.columns:
        df["Attendance"] = df["Attendance"].fillna(df["Attendance"].median()).clip(0, 100)
    if "Study_Hours" in df.columns:
        df["Study_Hours"] = df["Study_Hours"].fillna(df["Study_Hours"].median()).clip(lower=0)
    return df.reset_index(drop=True)


def cleaning_notes(raw: pd.DataFrame, clean: pd.DataFrame) -> list:
    """Plain-language log of what cleaning changed."""
    notes = [f"Loaded {len(raw)} rows and {raw.shape[1]} columns."]
    missing = int(raw.isna().sum().sum())
    notes.append(f"Filled {missing} missing value(s) with the column median." if missing
                 else "No missing values found.")
    dropped = len(raw) - len(clean)
    if dropped:
        notes.append(f"Removed {dropped} duplicate or nameless row(s).")
    notes.append("Marks were limited to the 0-100 range.")
    return notes


# ---------- Module 3: Performance calculation ----------
def grade_from_percentage(p: float) -> str:
    if p >= 90: return "A+"
    if p >= 80: return "A"
    if p >= 70: return "B"
    if p >= 60: return "C"
    if p >= 50: return "D"
    if p >= PASS_MARK: return "E"
    return "F"


def _risk(row) -> str:
    if row["Average"] < 50 or row["Fails"] >= 2:
        return "High"
    low_att = "Attendance" in row and row["Attendance"] < LOW_ATTENDANCE
    if row["Average"] < 65 or row["Fails"] >= 1 or low_att:
        return "Medium"
    return "Low"


def calculate_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Add Total, Average, Percentage, Grade, Rank, Fails and Risk columns."""
    df = df.copy()
    subjects = get_subject_columns(df)
    df["Total"] = df[subjects].sum(axis=1)
    df["Average"] = df[subjects].mean(axis=1).round(2)
    df["Percentage"] = (df["Total"] / (MAX_MARK * len(subjects)) * 100).round(2)
    df["Grade"] = df["Percentage"].apply(grade_from_percentage)
    df["Rank"] = df["Total"].rank(ascending=False, method="min").astype(int)
    df["Fails"] = (df[subjects] < PASS_MARK).sum(axis=1)
    df["Risk"] = df.apply(_risk, axis=1)
    return df


# ---------- Module 4: Subject-wise analysis ----------
def subject_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Class-level statistics for every subject."""
    rows = []
    for s in get_subject_columns(df):
        rows.append({
            "Subject": s,
            "Mean": round(df[s].mean(), 2),
            "Median": round(df[s].median(), 2),
            "Highest": df[s].max(),
            "Lowest": df[s].min(),
            "Std Dev": round(df[s].std(), 2),
            "Pass Rate %": round((df[s] >= PASS_MARK).mean() * 100, 1),
        })
    return pd.DataFrame(rows).set_index("Subject")


def weak_subjects(df: pd.DataFrame, student_name: str, gap: float = 10) -> pd.DataFrame:
    """Subjects where the student is failing or well below the class average."""
    subjects = get_subject_columns(df)
    row = df[df["Name"] == student_name].iloc[0]
    class_avg = df[subjects].mean()
    out = []
    for s in subjects:
        diff = row[s] - class_avg[s]
        if row[s] < PASS_MARK:
            reason = "Below pass mark"
        elif diff <= -gap:
            reason = f"{abs(diff):.0f} points below class average"
        else:
            continue
        out.append({"Subject": s, "Marks": row[s],
                    "Class Average": round(class_avg[s], 1), "Reason": reason})
    return pd.DataFrame(out, columns=["Subject", "Marks", "Class Average", "Reason"])


def strongest_and_weakest(df: pd.DataFrame, student_name: str):
    subjects = get_subject_columns(df)
    row = df[df["Name"] == student_name].iloc[0][subjects].astype(float)
    return row.idxmax(), row.idxmin()


def safe_corr(a, b) -> float:
    if len(a) < 3 or np.std(a) == 0 or np.std(b) == 0:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def study_hours_correlation(df: pd.DataFrame) -> float:
    if "Study_Hours" not in df.columns:
        return float("nan")
    return safe_corr(df["Study_Hours"], df["Average"])


# ---------- Attendance analysis ----------
def attendance_bands(df: pd.DataFrame) -> pd.DataFrame:
    """Average marks and head-count for each attendance band."""
    bands = pd.cut(df["Attendance"], [-1, 75, 85, 101],
                   labels=["Below 75%", "75-85%", "Above 85%"])
    out = (df.groupby(bands, observed=False)
             .agg(Students=("Name", "count"), Average_Marks=("Average", "mean"))
             .round(1).reset_index())
    out.columns = ["Attendance band", "Students", "Average marks"]
    return out


def attendance_correlation(df: pd.DataFrame) -> float:
    return safe_corr(df["Attendance"], df["Average"])


# ---------- Insights and advice ----------
def class_insights(df: pd.DataFrame) -> list:
    subjects = get_subject_columns(df)
    means = df[subjects].mean()
    pass_rates = (df[subjects] >= PASS_MARK).mean() * 100
    high = int((df["Risk"] == "High").sum())
    med = int((df["Risk"] == "Medium").sum())
    out = [
        f"Strongest subject is **{means.idxmax()}** (average {means.max():.1f}); "
        f"weakest is **{means.idxmin()}** (average {means.min():.1f}).",
        f"**{high}** student(s) are high risk and **{med}** are medium risk.",
    ]
    hardest = pass_rates.idxmin()
    if pass_rates.min() < 100:
        out.append(f"**{hardest}** has the lowest pass rate ({pass_rates.min():.0f}%).")
    r = study_hours_correlation(df)
    if not np.isnan(r):
        strength = "strong" if abs(r) >= 0.7 else "moderate" if abs(r) >= 0.4 else "weak"
        out.append(f"Study hours and marks show a **{strength}** relationship (r = {r:.2f}).")
    ra = attendance_correlation(df)
    if not np.isnan(ra):
        strength = "strong" if abs(ra) >= 0.7 else "moderate" if abs(ra) >= 0.4 else "weak"
        out.append(f"Attendance and marks show a **{strength}** relationship (r = {ra:.2f}).")
    return out


def recommendations(df: pd.DataFrame, student_name: str) -> list:
    """Practical, rule-based advice for one student."""
    row = df[df["Name"] == student_name].iloc[0]
    weak = weak_subjects(df, student_name)
    tips = []
    for _, w in weak.iterrows():
        if w["Reason"] == "Below pass mark":
            tips.append(f"**{w['Subject']}**: failing at {w['Marks']:.0f}. Make this the first priority "
                        "and ask the teacher for extra help.")
        else:
            tips.append(f"**{w['Subject']}**: {w['Reason']}. Add regular practice.")
    if row["Attendance"] < LOW_ATTENDANCE:
        tips.append(f"Attendance is {row['Attendance']:.0f}%, below {LOW_ATTENDANCE}%. "
                    "Attending more classes should help marks.")
    if row["Study_Hours"] < df["Study_Hours"].mean() - 0.5:
        tips.append(f"Studies {row['Study_Hours']:.1f} h/day against a class average of "
                    f"{df['Study_Hours'].mean():.1f} h. A little more daily study will help.")
    if not tips:
        tips.append("Performing well across the board. Keep the routine going.")
    return tips


def student_report_text(df: pd.DataFrame, student_name: str) -> str:
    subjects = get_subject_columns(df)
    row = df[df["Name"] == student_name].iloc[0]
    lines = [
        f"STUDENT PERFORMANCE REPORT: {student_name}",
        "=" * 50,
        f"Total: {row['Total']:.0f} / {MAX_MARK * len(subjects)}",
        f"Average: {row['Average']:.1f}   Grade: {row['Grade']}   Rank: {row['Rank']} of {len(df)}",
        f"Attendance: {row['Attendance']:.0f}%   Study hours/day: {row['Study_Hours']:.1f}",
        f"Risk level: {row['Risk']}",
        "", "Subject marks (class average in brackets):",
    ]
    for s in subjects:
        lines.append(f"  {s:<12} {row[s]:>5.0f}   ({df[s].mean():.1f})")
    lines += ["", "Recommendations:"]
    lines += [f"  - {t.replace('**', '')}" for t in recommendations(df, student_name)]
    return "\n".join(lines)


# ---------- Machine-learning predictor ----------
FEATURES = ["Study_Hours", "Attendance"]


def train_model(df: pd.DataFrame):
    """Fit a linear regression predicting Average from study hours and attendance.
    Returns (model, cross-validated R2 or NaN)."""
    X, y = df[FEATURES].values, df["Average"].values
    model = LinearRegression().fit(X, y)
    r2 = float("nan")
    if len(df) >= 8:
        r2 = float(cross_val_score(LinearRegression(), X, y, cv=min(5, len(df) // 2), scoring="r2").mean())
    return model, r2


def predict_average(model, hours: float, attendance: float) -> float:
    return float(np.clip(model.predict([[hours, attendance]])[0], 0, 100))


def hours_needed(model, target: float, attendance: float):
    """Daily study hours the model says are needed to reach `target` average, or None."""
    b_hours = model.coef_[0]
    if b_hours <= 0:
        return None
    h = (target - model.intercept_ - model.coef_[1] * attendance) / b_hours
    return float(max(h, 0))

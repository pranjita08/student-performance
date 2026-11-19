"""Module 6: results dashboard (mobile-friendly). Run with:  streamlit run app.py"""
from pathlib import Path

import streamlit as st

import analysis as an
import charts as ch

st.set_page_config(page_title="Student Performance", page_icon="🎓", layout="wide",
                   initial_sidebar_state="collapsed")

# ---------------- Styling ----------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Manrope:wght@400;500;600;700;800&display=swap');
:root {
  --burgundy:#54263C; --wine:#793D58; --rose:#B77C91; --dusty-rose:#D9A8B7;
  --blush:#F1E2E5; --ivory:#FAF6F2; --surface:#FFFFFF; --border:#E8E0DB;
  --ink:#332C30; --muted:#746A6D; --subtle:#92847F;
  --sage:#32734D; --sage-bg:#E5F0E8; --amber:#A66A27; --amber-bg:#FAEEDC;
  --danger:#A94750; --danger-bg:#F6E4E5;
}
html, body, .stApp,{font-family:'Manrope',sans-serif;}
[data-testid="stIconMaterial"], .material-symbols-rounded, .material-icons {font-family:'Material Symbols Rounded','Material Icons' !important;}
.stApp {background:var(--ivory); color:var(--ink);}
.block-container {max-width:1240px; padding-top:2rem; padding-bottom:3.5rem;}
#MainMenu, footer {visibility:hidden;}
header[data-testid="stHeader"] {background:rgba(250,246,242,.88);}
[data-testid="stToolbar"] {right:1rem;}
* {scrollbar-color:#C9AAB5 transparent; scrollbar-width:thin;}

/* Hero */
.hero {position:relative; overflow:hidden; border-radius:22px; padding:34px 36px; margin:0 0 22px;
  background:linear-gradient(118deg,#54263C 0%,#69354D 58%,#8B5268 100%);
  box-shadow:0 16px 38px rgba(84,38,60,.15);}
.hero:before {content:""; position:absolute; width:340px; height:340px; right:-100px; top:-190px;
  border:1px solid rgba(255,255,255,.17); border-radius:50%; box-shadow:0 0 0 34px rgba(255,255,255,.035),0 0 0 72px rgba(255,255,255,.025);}
.hero:after {content:""; position:absolute; width:180px; height:180px; right:90px; bottom:-145px;
  background:rgba(217,168,183,.16); border-radius:50%; filter:blur(2px);}
.hero .hero-kicker {color:#E8C9D3; text-transform:uppercase; letter-spacing:.16em; font-size:.72rem; font-weight:800; margin-bottom:10px;}
.hero h1 {font-family:'DM Serif Display',serif!important; font-weight:400; color:#FFF9F7; font-size:clamp(2rem,4vw,2.8rem); line-height:1.08; margin:0; max-width:850px;}
.hero p {color:#F1E2E5; font-size:.96rem; line-height:1.65; max-width:720px; margin:12px 0 18px;}
.chips {display:flex; flex-wrap:wrap; gap:8px; position:relative; z-index:1;}
.chip {background:rgba(255,255,255,.10); border:1px solid rgba(255,255,255,.22); color:#FFF8F6; padding:5px 11px; border-radius:999px; font-size:.72rem; font-weight:600;}

/* Main sections and typography */
h1,h2,h3,h4 {font-family:'Manrope',sans-serif!important; color:var(--ink); letter-spacing:-.035em;}
h2 {font-size:1.45rem!important; font-weight:800!important;}
h3 {font-size:1.12rem!important; font-weight:800!important; border:0; padding:0; margin-top:1.1rem;}
p,li,label,.stMarkdown {color:var(--ink);}
.stCaption, [data-testid="stCaptionContainer"] {color:var(--muted)!important;}
[data-testid="stExpander"] {background:var(--surface); border:1px solid var(--border); border-radius:14px;}
[data-testid="stExpander"] summary {color:var(--burgundy); font-weight:700;}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {gap:7px; background:transparent; border-bottom:1px solid var(--border); padding:4px 2px 10px;}
.stTabs [data-baseweb="tab"] {background:transparent; border-radius:10px; padding:9px 14px; color:var(--muted); font-weight:700; font-size:.86rem; white-space:nowrap;}
.stTabs [aria-selected="true"] {background:var(--blush)!important; color:var(--burgundy)!important;}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {background:var(--wine)!important; height:3px;}
.stTabs [data-baseweb="tab-panel"] {padding-top:1.15rem;}

/* KPI cards */
.kpis {display:grid; grid-template-columns:repeat(auto-fit,minmax(165px,1fr)); gap:14px; margin:8px 0 26px;}
.kpi {position:relative; background:var(--surface); border:1px solid var(--border); border-radius:16px; padding:17px 18px 16px;
  box-shadow:0 5px 18px rgba(84,38,60,.045); transition:transform .18s ease,box-shadow .18s ease; min-width:0;}
.kpi:hover {transform:translateY(-3px); box-shadow:0 10px 25px rgba(84,38,60,.09);}
.kpi:before {content:""; position:absolute; top:0; left:18px; width:38px; height:3px; border-radius:0 0 4px 4px; background:var(--rose);}
.kpi .label {font-size:.68rem; color:var(--subtle); text-transform:uppercase; letter-spacing:.105em; font-weight:800; margin-bottom:7px;}
.kpi .value {font-family:'Manrope',sans-serif; font-size:1.72rem; font-weight:800; line-height:1.25; color:var(--burgundy); overflow-wrap:anywhere; font-variant-numeric:tabular-nums;}
.kpi .sub {font-size:.73rem; color:var(--muted); margin-top:5px; line-height:1.4;}

/* Risk badges */
.badge {display:inline-block; padding:5px 12px; border-radius:999px; font-weight:800; font-size:.78rem; box-shadow:none;}
.badge.Low {background:var(--sage-bg); color:var(--sage);}
.badge.Medium {background:var(--amber-bg); color:var(--amber);}
.badge.High {background:var(--danger-bg); color:var(--danger);}

/* Charts, tables and data widgets */
[data-testid="stPlotlyChart"] {background:var(--surface); border:1px solid var(--border); border-radius:16px; padding:8px 8px 2px;
  margin:4px 0 16px; box-shadow:0 5px 18px rgba(84,38,60,.035);}
[data-testid="stDataFrame"] {background:var(--surface); border:1px solid var(--border); border-radius:13px; overflow:hidden;}
[data-testid="stTable"] {background:var(--surface);}
[data-baseweb="select"] > div, [data-baseweb="input"] > div, [data-baseweb="textarea"] {background:#FFF!important; border-color:var(--border)!important; border-radius:10px!important;}
[data-testid="stFileUploader"] section {background:#FFF; border:1px dashed #C9AAB5; border-radius:13px;}
.stButton > button, .stDownloadButton > button {background:var(--burgundy); color:#FFF; border:1px solid var(--burgundy); border-radius:10px;
  font-family:'Manrope',sans-serif; font-weight:700; padding:.55rem 1rem; box-shadow:0 5px 13px rgba(84,38,60,.12); transition:all .18s ease;}
.stButton > button:hover, .stDownloadButton > button:hover {background:var(--wine); border-color:var(--wine); color:#FFF; transform:translateY(-1px);}
.stButton > button:focus, .stDownloadButton > button:focus {box-shadow:0 0 0 3px rgba(183,124,145,.25);}
[data-testid="stAlert"] {border-radius:12px;}
hr {border-color:var(--border)!important;}

@media (max-width:760px) {
 .block-container {padding:1rem 1rem 2.5rem;}
 .hero {padding:26px 22px; border-radius:17px;}
 .hero h1 {font-size:1.9rem;}
 .hero p {font-size:.88rem;}
 .stTabs [data-baseweb="tab"] {padding:8px 10px; font-size:.78rem;}
 .kpis {grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px;}
 .kpi {padding:14px;}
 .kpi .value {font-size:1.45rem;}
}
@media (prefers-reduced-motion:reduce) {*,*::before,*::after {animation:none!important; transition:none!important; scroll-behavior:auto!important;}}
</style>
""",
    unsafe_allow_html=True,
)


def kpi_row(items):
    """items: list of (label, value, sub). A CSS grid keeps 2 cards per row on phones."""
    from html import escape
    cards = "".join(
        f'<div class="kpi"><div class="label">{escape(str(l))}</div><div class="value">{escape(str(v))}</div>'
        f'<div class="sub">{escape(str(s))}</div></div>' for l, v, s in items)
    st.markdown(f'<div class="kpis">{cards}</div>', unsafe_allow_html=True)


def show(fig):
    st.plotly_chart(fig, config={"displayModeBar": False})


st.markdown(
    '<div class="hero"><div class="hero-kicker">Student performance intelligence</div>'
    '<h1>Understand performance. Discover potential.</h1>'
    '<p>Turn marks, attendance and study habits into meaningful insights, early risk signals and informed predictions.</p>'
    '<div class="chips"><span class="chip">Class insights</span><span class="chip">Subject analysis</span>'
    '<span class="chip">Attendance trends</span><span class="chip">Predictive insights</span></div></div>',
    unsafe_allow_html=True,
)

# ---------------- Data ----------------
with st.expander("📁 Data source (upload your own CSV)"):
    uploaded = st.file_uploader("Upload a CSV", type="csv")
    st.caption("Columns needed: Name, Attendance, Study_Hours, plus one column per subject "
               "(marks out of 100). Student_ID is optional. The sample data is used if nothing is uploaded.")


@st.cache_data
def prepare(source):
    raw = an.load_data(source)
    clean = an.clean_data(raw)
    return an.calculate_performance(clean), an.cleaning_notes(raw, clean)


try:
    data, notes = prepare(uploaded if uploaded else Path(__file__).with_name("students.csv"))
except Exception as e:  # bad upload
    st.error(f"Could not read the data: {e}")
    st.stop()

subjects = an.get_subject_columns(data)
n = len(data)
model, r2 = an.train_model(data)

tabs = st.tabs(["📊 Overview", "🧑‍🎓 Student", "📚 Subjects", "🗓️ Attendance", "🔮 Predictor", "📥 Data"])

# ================= Overview =================
with tabs[0]:
    top = data.loc[data["Total"].idxmax()]
    kpi_row([
        ("Students", n, f"{len(subjects)} subjects"),
        ("Class average", f"{data['Average'].mean():.1f}", f"pass rate {(data['Fails'] == 0).mean() * 100:.0f}% clear all"),
        ("Top scorer", top["Name"], f"average {top['Average']:.1f}"),
        ("At risk", int((data["Risk"] == "High").sum()), "high-risk students"),
    ])
    st.subheader("Key insights")
    for line in an.class_insights(data):
        st.markdown(f"- {line}")

    c1, c2 = st.columns(2)
    with c1:
        show(ch.subject_averages(data))
        show(ch.study_hours_scatter(data))
    with c2:
        show(ch.grade_distribution(data))
        show(ch.risk_donut(data))
    show(ch.subject_boxplot(data))

    st.subheader("Leaderboard")
    risk_filter = st.multiselect("Show risk levels", ["Low", "Medium", "High"], default=["Low", "Medium", "High"])
    lb = data[data["Risk"].isin(risk_filter)].sort_values("Rank")[["Rank", "Name", "Average", "Grade", "Attendance", "Risk"]]
    st.dataframe(
        lb, hide_index=True,
        column_config={"Average": st.column_config.ProgressColumn("Average", min_value=0, max_value=100, format="%.1f")},
    )

# ================= Student =================
with tabs[1]:
    s1, s2 = st.columns(2)
    name = s1.selectbox("Choose a student", data["Name"])
    other = s2.selectbox("Compare with (optional)", ["None"] + [x for x in data["Name"] if x != name])
    row = data[data["Name"] == name].iloc[0]
    best, worst = an.strongest_and_weakest(data, name)

    st.markdown(f'<span class="badge {row["Risk"]}">{row["Risk"]} risk</span>', unsafe_allow_html=True)
    kpi_row([
        ("Total", f"{row['Total']:.0f}", f"out of {100 * len(subjects)}"),
        ("Average", f"{row['Average']:.1f}", f"class {data['Average'].mean():.1f}"),
        ("Grade", row["Grade"], f"rank {row['Rank']} of {n}"),
        ("Attendance", f"{row['Attendance']:.0f}%", f"{row['Study_Hours']:.1f} study h/day"),
    ])
    st.write(f"**Strongest:** {best} ({row[best]:.0f})  ·  **Weakest:** {worst} ({row[worst]:.0f})")

    c1, c2 = st.columns(2)
    with c1:
        show(ch.student_vs_class(data, name))
    with c2:
        show(ch.student_radar(data, name, None if other == "None" else other))

    st.subheader("Subjects that need attention")
    weak = an.weak_subjects(data, name)
    if weak.empty:
        st.success("No subject is failing or well below the class average. Keep it up!")
    else:
        st.dataframe(weak, hide_index=True)

    st.subheader("Recommendations")
    for tip in an.recommendations(data, name):
        st.markdown(f"- {tip}")

    st.download_button("⬇️ Download this student's report (.txt)", an.student_report_text(data, name),
                       file_name=f"{name.replace(' ', '_')}_report.txt")

# ================= Subjects =================
with tabs[2]:
    subject = st.selectbox("Choose a subject", subjects)
    summary = an.subject_summary(data)
    s = summary.loc[subject]
    kpi_row([
        ("Mean", s["Mean"], f"median {s['Median']}"),
        ("Pass rate", f"{s['Pass Rate %']}%", "marks 40 and above"),
        ("Highest", s["Highest"], ""),
        ("Lowest", s["Lowest"], ""),
    ])
    c1, c2 = st.columns(2)
    with c1:
        show(ch.subject_distribution(data, subject))
    with c2:
        show(ch.correlation_heatmap(data))

    st.subheader(f"Students struggling in {subject}")
    low = data[data[subject] < an.PASS_MARK][["Name", subject]].sort_values(subject)
    if low.empty:
        st.info("Everyone passed this subject.")
    else:
        st.dataframe(low, hide_index=True)

    st.subheader("All subjects compared")
    st.dataframe(summary)

# ================= Attendance =================
with tabs[3]:
    low_att = data[data["Attendance"] < an.LOW_ATTENDANCE]
    kpi_row([
        ("Average attendance", f"{data['Attendance'].mean():.0f}%", ""),
        ("Below 75%", len(low_att), "students"),
        ("Attendance vs marks (r)", f"{an.attendance_correlation(data):.2f}", "closer to 1 = stronger link"),
    ])
    c1, c2 = st.columns(2)
    with c1:
        show(ch.attendance_scatter(data))
    with c2:
        st.subheader("Marks by attendance band")
        st.dataframe(an.attendance_bands(data), hide_index=True)
        st.subheader("Low-attendance students")
        if low_att.empty:
            st.success("Everyone is at or above 75%.")
        else:
            st.dataframe(low_att.sort_values("Attendance")[["Name", "Attendance", "Average", "Risk"]], hide_index=True)

# ================= Predictor =================
with tabs[4]:
    st.subheader("Predict marks from study habits")
    if r2 == r2:  # not NaN
        st.caption(f"Linear regression on study hours and attendance. Cross-validated R² = {r2:.2f}. "
                   "This is a simple estimate from a small dataset, so treat it as guidance, not a guarantee.")
    else:
        st.caption("Simple linear regression on study hours and attendance. Too little data to validate it.")

    p1, p2 = st.columns(2)
    hours = p1.slider("Study hours per day", 0.0, 8.0, 3.0, 0.5)
    att = p2.slider("Attendance %", 40, 100, 85)
    pred = an.predict_average(model, hours, att)
    grade = an.grade_from_percentage(pred)
    c1, c2 = st.columns(2)
    with c1:
        show(ch.predicted_gauge(pred, grade))
    with c2:
        show(ch.hours_curve(model, att, hours))

    st.subheader("What would it take?")
    t1, t2 = st.columns(2)
    who = t1.selectbox("Student", data["Name"], key="whatif_student")
    target = t2.slider("Target average", 40, 95, 70)
    r = data[data["Name"] == who].iloc[0]
    need = an.hours_needed(model, target, r["Attendance"])
    if need is None:
        st.info("The model can't estimate this from the current data.")
    elif need > 12:
        st.warning(f"Reaching {target} looks unrealistic from study hours alone for {who}.")
    else:
        diff = need - r["Study_Hours"]
        msg = (f"**{who}** studies {r['Study_Hours']:.1f} h/day. To reach an average of {target} "
               f"at {r['Attendance']:.0f}% attendance, the model suggests about **{need:.1f} h/day**")
        st.success(msg + (f" ({diff:+.1f} h from now)." if diff > 0 else ". Already on track."))

# ================= Data =================
with tabs[5]:
    st.subheader("Cleaning log")
    for line in notes:
        st.markdown(f"- {line}")
    st.subheader("Processed data")
    st.dataframe(data, hide_index=True)
    d1, d2 = st.columns(2)
    d1.download_button("⬇️ Download results (.csv)", data.to_csv(index=False), file_name="student_results.csv",
                       mime="text/csv")
    template = "Student_ID,Name,Math,Science,English,Attendance,Study_Hours\nS001,Example Student,75,80,70,90,3.5\n"
    d2.download_button("⬇️ Download blank CSV template", template, file_name="template.csv", mime="text/csv")

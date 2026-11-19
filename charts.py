"""Module 5: interactive graph generation (Plotly). Every function returns a Figure."""
import numpy as np
import plotly.graph_objects as go

from analysis import get_subject_columns, PASS_MARK, predict_average

BURGUNDY, WINE, ROSE, GREY, RED, AMBER, GREEN = "#54263C", "#793D58", "#B77C91", "#A99B98", "#A94750", "#A66A27", "#32734D"
BLUE, TEAL = BURGUNDY, ROSE
RISK_COLORS = {"Low": GREEN, "Medium": AMBER, "High": RED}


def _style(fig, height=340, legend=True):
    """Shared look: transparent background, tight margins (good on phones)."""
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=dict(l=12, r=16, t=54, b=18),
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        font=dict(family="Manrope, sans-serif", size=11, color="#746A6D"),
        title=dict(font=dict(size=15, family="Manrope, sans-serif", color="#54263C"), x=0.025, xanchor="left"),
        xaxis=dict(gridcolor="#EEE7E3", zerolinecolor="#D9CECA", linecolor="#E8E0DB", ticks="outside"),
        yaxis=dict(gridcolor="#EEE7E3", zerolinecolor="#D9CECA", linecolor="#E8E0DB", ticks="outside"),
        showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=-0.28, x=0, font=dict(color="#746A6D")),
        hoverlabel=dict(font_size=12, bgcolor="#54263C", font_color="#FFFFFF", bordercolor="#54263C"),
    )
    return fig


def subject_averages(df):
    subjects = get_subject_columns(df)
    means = df[subjects].mean().sort_values()
    fig = go.Figure(go.Bar(
        x=means.values, y=means.index, orientation="h",
        marker_color=BLUE, text=[f"{v:.1f}" for v in means.values], textposition="outside",
        hovertemplate="%{y}: %{x:.1f}<extra></extra>"))
    fig.update_xaxes(range=[0, 105], title="Class average marks")
    fig.update_layout(title="Average marks by subject")
    return _style(fig, legend=False)


def grade_distribution(df):
    order = ["A+", "A", "B", "C", "D", "E", "F"]
    counts = df["Grade"].value_counts().reindex(order, fill_value=0)
    fig = go.Figure(go.Bar(x=counts.index, y=counts.values, marker_color=BLUE,
                           text=counts.values, textposition="outside",
                           hovertemplate="Grade %{x}: %{y} students<extra></extra>"))
    fig.update_yaxes(title="Students", range=[0, max(counts.max() + 1, 3)])
    fig.update_layout(title="Grade distribution")
    return _style(fig, legend=False)


def risk_donut(df):
    counts = df["Risk"].value_counts().reindex(["Low", "Medium", "High"], fill_value=0)
    fig = go.Figure(go.Pie(labels=counts.index, values=counts.values, hole=0.6,
                           marker_colors=[RISK_COLORS[k] for k in counts.index],
                           textinfo="label+value", sort=False))
    fig.update_layout(title="Students by risk level")
    return _style(fig, legend=False)


def _scatter_with_trend(df, xcol, xlabel, title):
    fig = go.Figure()
    for level in ["Low", "Medium", "High"]:
        d = df[df["Risk"] == level]
        if d.empty:
            continue
        fig.add_trace(go.Scatter(
            x=d[xcol], y=d["Average"], mode="markers", name=f"{level} risk",
            marker=dict(size=11, color=RISK_COLORS[level], line=dict(width=1, color="#FFFFFF")),
            text=d["Name"], hovertemplate="<b>%{text}</b><br>" + xlabel + ": %{x}<br>Average: %{y}<extra></extra>"))
    if len(df) >= 3 and df[xcol].nunique() > 1:
        m, b = np.polyfit(df[xcol], df["Average"], 1)
        xs = np.linspace(df[xcol].min(), df[xcol].max(), 50)
        fig.add_trace(go.Scatter(x=xs, y=m * xs + b, mode="lines", name="Trend",
                                 line=dict(color=GREY, dash="dash"), hoverinfo="skip"))
    fig.update_xaxes(title=xlabel)
    fig.update_yaxes(title="Average marks")
    fig.update_layout(title=title)
    return _style(fig, height=360)


def study_hours_scatter(df):
    return _scatter_with_trend(df, "Study_Hours", "Daily study hours", "Study hours vs average marks")


def attendance_scatter(df):
    return _scatter_with_trend(df, "Attendance", "Attendance %", "Attendance vs average marks")


def subject_boxplot(df):
    fig = go.Figure()
    for s in get_subject_columns(df):
        fig.add_trace(go.Box(y=df[s], name=s, boxpoints="all", jitter=0.4, pointpos=0,
                             marker=dict(size=5, color=BLUE), line=dict(color=BLUE),
                             fillcolor="rgba(183,124,145,0.18)", hovertext=df["Name"]))
    fig.add_hline(y=PASS_MARK, line_dash="dot", line_color=RED, annotation_text="Pass mark")
    fig.update_yaxes(title="Marks", range=[0, 102])
    fig.update_layout(title="Spread of marks by subject")
    return _style(fig, legend=False)


def correlation_heatmap(df):
    cols = get_subject_columns(df) + ["Attendance", "Study_Hours", "Average"]
    corr = df[cols].corr().round(2)
    fig = go.Figure(go.Heatmap(z=corr.values, x=cols, y=cols, zmin=-1, zmax=1,
                               colorscale=[[0,"#A94750"],[0.25,"#E8C9D3"],[0.5,"#FAF6F2"],[0.75,"#B77C91"],[1,"#54263C"]],
                               text=corr.values, texttemplate="%{text}",
                               hovertemplate="%{x} vs %{y}: %{z}<extra></extra>"))
    fig.update_layout(title="What moves together (correlation)")
    fig.update_yaxes(autorange="reversed")
    return _style(fig, height=420, legend=False)


def subject_distribution(df, subject):
    fig = go.Figure(go.Histogram(x=df[subject], xbins=dict(start=0, end=100, size=10),
                                 marker_color=BLUE, marker_line=dict(color="#FFFFFF", width=1),
                                 hovertemplate="Marks %{x}: %{y} students<extra></extra>"))
    fig.add_vline(x=df[subject].mean(), line_dash="dash", line_color=AMBER,
                  annotation_text="Mean", annotation_position="top")
    fig.add_vline(x=PASS_MARK, line_dash="dot", line_color=RED,
                  annotation_text="Pass", annotation_position="top left")
    fig.update_xaxes(title="Marks", range=[0, 100])
    fig.update_yaxes(title="Students")
    fig.update_layout(title=f"{subject}: score distribution", bargap=0.05)
    return _style(fig, legend=False)


def student_vs_class(df, student_name):
    subjects = get_subject_columns(df)
    row = df[df["Name"] == student_name].iloc[0]
    fig = go.Figure()
    fig.add_trace(go.Bar(x=subjects, y=[row[s] for s in subjects], name=student_name, marker_color=BLUE,
                         text=[f"{row[s]:.0f}" for s in subjects], textposition="outside"))
    fig.add_trace(go.Bar(x=subjects, y=df[subjects].mean().round(1).values, name="Class average",
                         marker_color=GREY))
    fig.add_hline(y=PASS_MARK, line_dash="dot", line_color=RED, annotation_text="Pass mark")
    fig.update_yaxes(range=[0, 110], title="Marks")
    fig.update_layout(title=f"{student_name} vs class average", barmode="group")
    return _style(fig, height=360)


def student_radar(df, student_name, compare=None):
    subjects = get_subject_columns(df)
    theta = subjects + [subjects[0]]

    def trace(values, name, color, fill=True, dash=None):
        v = list(values) + [values[0]]
        return go.Scatterpolar(r=v, theta=theta, name=name, line=dict(color=color, dash=dash),
                               fill="toself" if fill else None,
                               opacity=0.7 if fill else 1)

    row = df[df["Name"] == student_name].iloc[0]
    fig = go.Figure()
    fig.add_trace(trace([row[s] for s in subjects], student_name, BLUE))
    if compare and compare != student_name:
        other = df[df["Name"] == compare].iloc[0]
        fig.add_trace(trace([other[s] for s in subjects], compare, TEAL))
    fig.add_trace(trace(list(df[subjects].mean()), "Class average", GREY, fill=False, dash="dash"))
    fig.update_layout(title="Strengths at a glance",
                      polar=dict(radialaxis=dict(range=[0, 100], showline=False)))
    return _style(fig, height=380)


def predicted_gauge(value, grade):
    color = GREEN if value >= 70 else AMBER if value >= 50 else RED
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=round(value, 1),
        title=dict(text=f"Predicted average (grade {grade})"),
        gauge=dict(axis=dict(range=[0, 100]), bar=dict(color=color),
                   steps=[dict(range=[0, 40], color="#F6E4E5"),
                          dict(range=[40, 70], color="#FAEEDC"),
                          dict(range=[70, 100], color="#E5F0E8")])))
    return _style(fig, height=280, legend=False)


def hours_curve(model, attendance, current_hours=None):
    """Predicted average as study hours increase, at a fixed attendance."""
    hs =np.linspace(0, 8, 33)
    ys = [predict_average(model, h, attendance) for h in hs]
    fig = go.Figure(go.Scatter(x=hs, y=ys, mode="lines", line=dict(color=BLUE, width=3),
                               hovertemplate="%{x:.1f} h/day: %{y:.1f}<extra></extra>"))
    if current_hours is not None:
        fig.add_trace(go.Scatter(x=[current_hours], y=[predict_average(model, current_hours, attendance)],
                                 mode="markers", marker=dict(size=13, color=AMBER, line=dict(width=2, color="#FFFFFF")),
                                 name="Selected", hovertemplate="%{x:.1f} h/day: %{y:.1f}<extra></extra>"))
    fig.update_xaxes(title="Daily study hours")
    fig.update_yaxes(title="Predicted average", range=[0, 100])
    fig.update_layout(title=f"Study hours vs predicted marks (attendance {attendance:.0f}%)")
    return _style(fig, legend=False)

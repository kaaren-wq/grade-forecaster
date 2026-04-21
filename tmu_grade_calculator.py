
import math
from typing import Optional

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="TMU Grade Calculator",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------
# Theme
# ---------------------------
st.markdown(
    """
    <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(0,184,148,0.18), transparent 28%),
                radial-gradient(circle at top right, rgba(116,185,255,0.15), transparent 26%),
                linear-gradient(135deg, #071311 0%, #0d1d1a 42%, #101823 100%);
            color: #f4fffb;
        }
        .main .block-container {
            max-width: 1400px;
            padding-top: 1.4rem;
            padding-bottom: 2rem;
        }
        .hero-card, .glass-card, .metric-card {
            background: linear-gradient(180deg, rgba(9,24,22,0.96), rgba(12,18,26,0.96));
            border: 1px solid rgba(123, 237, 205, 0.16);
            border-radius: 24px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.24);
        }
        .hero-card {
            padding: 1.4rem 1.5rem 1.15rem 1.5rem;
            margin-bottom: 1rem;
        }
        .glass-card {
            padding: 1rem 1rem;
        }
        .metric-card {
            padding: 1rem 1rem 0.9rem 1rem;
            min-height: 120px;
        }
        .tiny-label {
            font-size: 0.82rem;
            color: #9de6d3;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        .big-number {
            font-size: 2rem;
            font-weight: 800;
            color: #effff9;
            line-height: 1.15;
        }
        .section-title {
            font-size: 1.15rem;
            font-weight: 700;
            color: #e8fff7;
            margin-bottom: 0.15rem;
        }
        .subtle {
            color: #a7cfc6;
        }
        .pill {
            display: inline-block;
            border: 1px solid rgba(123,237,205,0.20);
            color: #d7fff2;
            padding: 0.35rem 0.72rem;
            border-radius: 999px;
            font-size: 0.9rem;
            margin-right: 0.35rem;
            background: rgba(0,184,148,0.08);
        }
        .footer-note {
            color: #96bdb4;
            font-size: 0.92rem;
        }
        div[data-testid="stDataEditor"] {
            border-radius: 18px;
            overflow: hidden;
            border: 1px solid rgba(123,237,205,0.16);
        }
        .policy-box {
            border-radius: 18px;
            padding: 1rem 1rem;
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(123,237,205,0.12);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------
# TMU grading helpers
# ---------------------------
TMU_SCALE = [
    ("A+", 90, 100, 4.33),
    ("A", 85, 89, 4.00),
    ("A-", 80, 84, 3.67),
    ("B+", 77, 79, 3.33),
    ("B", 73, 76, 3.00),
    ("B-", 70, 72, 2.67),
    ("C+", 67, 69, 2.33),
    ("C", 63, 66, 2.00),
    ("C-", 60, 62, 1.67),
    ("D+", 57, 59, 1.33),
    ("D", 53, 56, 1.00),
    ("D-", 50, 52, 0.67),
    ("F", 0, 49, 0.00),
]

def round_standard(x: float) -> int:
    # standard mathematical rounding: .5 rounds up
    return int(math.floor(float(x) + 0.5))

def tmu_letter_and_gpa(percent: float):
    rounded = max(0, min(100, round_standard(percent)))
    for letter, low, high, gpa in TMU_SCALE:
        if low <= rounded <= high:
            return rounded, letter, gpa
    return rounded, "F", 0.0

def safe_float(x, default=0.0):
    try:
        if pd.isna(x):
            return default
        return float(x)
    except Exception:
        return default

def style_fig(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f3fffb"),
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(bgcolor="rgba(0,0,0,0)")
    )
    return fig

def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["Assessment"] = out["Assessment"].fillna("").astype(str)
    out["Category"] = out["Category"].fillna("Coursework").astype(str)
    out["Grade (%)"] = pd.to_numeric(out["Grade (%)"], errors="coerce").fillna(0.0).clip(0, 100)
    out["Weight (%)"] = pd.to_numeric(out["Weight (%)"], errors="coerce").fillna(0.0).clip(0, 100)
    return out

def compute_results(df: pd.DataFrame, final_exam_weight: float, final_exam_score: float):
    df = clean_df(df)
    coursework_weight = float(df["Weight (%)"].sum())
    weighted_earned = float((df["Grade (%)"] * df["Weight (%)"] / 100).sum())
    exam_contribution = float(final_exam_score * final_exam_weight / 100)
    projected_percent = weighted_earned + exam_contribution
    rounded_percent, letter, gpa = tmu_letter_and_gpa(projected_percent)

    needed = {}
    for target in [50, 60, 67, 70, 73, 77, 80, 85, 90]:
        if final_exam_weight <= 0:
            needed[target] = None
        else:
            raw = (target - weighted_earned) / final_exam_weight * 100
            needed[target] = max(0, min(100, raw))

    return {
        "df": df,
        "coursework_weight": coursework_weight,
        "total_weight": coursework_weight + final_exam_weight,
        "weighted_earned": weighted_earned,
        "exam_contribution": exam_contribution,
        "projected_percent": projected_percent,
        "rounded_percent": rounded_percent,
        "letter": letter,
        "gpa": gpa,
        "needed": needed,
        "grade_if_zero": weighted_earned,
        "grade_if_hundred": weighted_earned + final_exam_weight,
    }

# ---------------------------
# Charts
# ---------------------------
def gauge_chart(percent: float):
    rounded, letter, gpa = tmu_letter_and_gpa(percent)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=rounded,
        number={"suffix": "%", "font": {"size": 42}},
        title={"text": f"Rounded TMU Final Grade • {letter} • GPA {gpa:.2f}", "font": {"size": 20}},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#00b894"},
            "bgcolor": "rgba(255,255,255,0.03)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 50], "color": "rgba(255,107,107,0.20)"},
                {"range": [50, 67], "color": "rgba(253,203,110,0.18)"},
                {"range": [67, 80], "color": "rgba(116,185,255,0.16)"},
                {"range": [80, 100], "color": "rgba(85,239,196,0.16)"},
            ],
        }
    ))
    fig.update_layout(height=320)
    return style_fig(fig)

def scenario_chart(weighted_earned: float, final_exam_weight: float, chosen_score: float):
    x = np.arange(0, 101, 1)
    y = weighted_earned + (x * final_exam_weight / 100)
    rounded_y = np.array([tmu_letter_and_gpa(v)[0] for v in y])
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=rounded_y,
        mode="lines",
        name="Rounded TMU overall",
        line=dict(width=5, color="#00d1a4"),
        fill="tozeroy",
        fillcolor="rgba(0,184,148,0.12)"
    ))
    chosen_overall = weighted_earned + (chosen_score * final_exam_weight / 100)
    chosen_rounded, chosen_letter, chosen_gpa = tmu_letter_and_gpa(chosen_overall)
    fig.add_trace(go.Scatter(
        x=[chosen_score], y=[chosen_rounded],
        mode="markers+text",
        name="Your slider pick",
        marker=dict(size=14, color="#74b9ff", line=dict(width=2, color="#ecfeff")),
        text=[f"{chosen_rounded}% • {chosen_letter} • {chosen_gpa:.2f}"],
        textposition="top center"
    ))
    for target in [50, 60, 67, 70, 73, 77, 80, 85, 90]:
        fig.add_hline(y=target, line_dash="dot", line_color="rgba(255,255,255,0.18)")
    fig.update_layout(
        title="Final Exam What-If Simulator",
        xaxis_title="Final Exam Score (%)",
        yaxis_title="Rounded TMU Overall Grade (%)",
        xaxis=dict(range=[0, 100]),
        yaxis=dict(range=[0, 100]),
        height=380
    )
    return style_fig(fig)

def impact_chart(weighted_earned: float, exam_contribution: float):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[weighted_earned], y=["Overall Grade Build"], orientation="h",
        name="Earned so far", marker=dict(color="#00b894"), text=[f"{weighted_earned:.2f}%"], textposition="inside"
    ))
    fig.add_trace(go.Bar(
        x=[exam_contribution], y=["Overall Grade Build"], orientation="h",
        name="Final exam impact", marker=dict(color="#74b9ff"), text=[f"+{exam_contribution:.2f}%"], textposition="inside"
    ))
    for target in [50, 67, 70, 80, 90]:
        fig.add_vline(x=target, line_dash="dash", line_color="rgba(255,255,255,0.18)")
    fig.update_layout(
        barmode="stack",
        title="Current Grade + Final Exam Contribution",
        xaxis_title="Overall Grade (%)",
        xaxis=dict(range=[0, 100]),
        height=300
    )
    return style_fig(fig)

def assessment_chart(df: pd.DataFrame):
    plot_df = df.copy()
    plot_df["Weighted Contribution (%)"] = plot_df["Grade (%)"] * plot_df["Weight (%)"] / 100
    fig = px.bar(
        plot_df,
        x="Assessment",
        y=["Weighted Contribution (%)", "Weight (%)"],
        barmode="group",
        title="Assessment Breakdown"
    )
    fig.update_layout(height=390, yaxis_title="Percent")
    return style_fig(fig)

def weight_donut(df: pd.DataFrame, final_exam_weight: float):
    donut_df = df[["Assessment", "Weight (%)"]].copy()
    if final_exam_weight > 0:
        donut_df = pd.concat(
            [donut_df, pd.DataFrame([{"Assessment": "Final Exam", "Weight (%)": final_exam_weight}])],
            ignore_index=True
        )
    fig = px.pie(
        donut_df,
        names="Assessment",
        values="Weight (%)",
        hole=0.62,
        title="Course Weight Distribution"
    )
    fig.update_traces(textinfo="percent+label")
    fig.update_layout(height=390)
    return style_fig(fig)

def category_radar(df: pd.DataFrame):
    if df.empty:
        return None
    tmp = df.copy()
    tmp["Weighted Contribution"] = tmp["Grade (%)"] * tmp["Weight (%)"] / 100
    cat = tmp.groupby("Category", as_index=False)[["Weight (%)", "Weighted Contribution"]].sum()
    if len(cat) < 2:
        return None
    theta = cat["Category"].tolist()
    theta.append(theta[0])
    r1 = cat["Weight (%)"].tolist()
    r1.append(r1[0])
    r2 = cat["Weighted Contribution"].tolist()
    r2.append(r2[0])

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=r1, theta=theta, fill="toself", name="Weight", line=dict(color="#74b9ff", width=3)))
    fig.add_trace(go.Scatterpolar(r=r2, theta=theta, fill="toself", name="Earned", line=dict(color="#00d1a4", width=3)))
    fig.update_layout(
        title="Category Radar",
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0, max(100, max(r1))])
        ),
        height=420
    )
    return style_fig(fig)

# ---------------------------
# Session defaults
# ---------------------------
if "grade_data_tmu" not in st.session_state:
    st.session_state.grade_data_tmu = pd.DataFrame(
        [
            ["Quiz 1", 78, 10, "Quizzes"],
            ["Assignment 1", 84, 15, "Assignments"],
            ["Midterm", 72, 25, "Exams"],
            ["Project", 88, 20, "Projects"],
        ],
        columns=["Assessment", "Grade (%)", "Weight (%)", "Category"]
    )

if "final_exam_weight_tmu" not in st.session_state:
    st.session_state.final_exam_weight_tmu = 30

if "final_exam_score_tmu" not in st.session_state:
    st.session_state.final_exam_score_tmu = 70

# ---------------------------
# Header
# ---------------------------
st.markdown(
    """
    <div class="hero-card">
        <div class="pill">TMU grading system</div>
        <div class="pill">4.33 GPA conversion</div>
        <div class="pill">Rounded final percent</div>
        <h1 style="margin: 0.55rem 0 0.35rem 0; font-size: 3rem;">TMU Grade Calculator</h1>
        <div style="font-size: 1.08rem; color: #b7e7db; max-width: 980px;">
            Built specifically for Toronto Metropolitan University students. Track your grades during the semester,
            simulate your final exam with the slider, and instantly see your rounded TMU percentage, letter grade, and 4.33 GPA.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------
# Sidebar
# ---------------------------
with st.sidebar:
    st.markdown("## TMU Grade Calculator")
    course_name = st.text_input("Course name", value="TMU Course")
    student_name = st.text_input("Student name", value="")
    st.markdown("---")
    st.markdown("### Final Exam")
    st.session_state.final_exam_weight_tmu = st.slider(
        "Final exam weight (%)", 0, 100, int(st.session_state.final_exam_weight_tmu), 1
    )
    st.session_state.final_exam_score_tmu = st.slider(
        "Expected final exam score (%)", 0, 100, int(st.session_state.final_exam_score_tmu), 1
    )
    default_chart = st.selectbox(
        "Primary chart",
        ["Gauge", "Scenario Simulator", "Impact Bar", "Weight Donut", "Assessment Breakdown", "Category Radar"],
        index=0
    )
    st.markdown("---")
    if st.button("Load demo TMU course", use_container_width=True):
        st.session_state.grade_data_tmu = pd.DataFrame(
            [
                ["Quiz 1", 82, 10, "Quizzes"],
                ["Quiz 2", 76, 5, "Quizzes"],
                ["Lab 1", 91, 5, "Labs"],
                ["Assignment 1", 84, 12, "Assignments"],
                ["Assignment 2", 88, 13, "Assignments"],
                ["Midterm", 73, 25, "Exams"],
            ],
            columns=["Assessment", "Grade (%)", "Weight (%)", "Category"]
        )
        st.rerun()

# ---------------------------
# Data input + metrics
# ---------------------------
left, right = st.columns([1.45, 1], gap="large")

with left:
    st.markdown('<div class="section-title">Enter your TMU grades</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtle">Add each assessment name, the percentage you got, and its course weight.</div>', unsafe_allow_html=True)

    edited_df = st.data_editor(
        st.session_state.grade_data_tmu,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "Assessment": st.column_config.TextColumn("Name"),
            "Grade (%)": st.column_config.NumberColumn("Grade (%)", min_value=0.0, max_value=100.0, step=1.0, format="%.1f"),
            "Weight (%)": st.column_config.NumberColumn("Weight (%)", min_value=0.0, max_value=100.0, step=1.0, format="%.1f"),
            "Category": st.column_config.SelectboxColumn(
                "Category",
                options=["Assignments", "Quizzes", "Labs", "Projects", "Exams", "Participation", "Coursework"],
            ),
        },
        key="tmu_editor",
    )
    st.session_state.grade_data_tmu = edited_df

results = compute_results(
    st.session_state.grade_data_tmu,
    st.session_state.final_exam_weight_tmu,
    st.session_state.final_exam_score_tmu
)

with right:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="tiny-label">Projected overall</div>
                <div class="big-number">{results["projected_percent"]:.2f}%</div>
                <div class="subtle">Raw percentage before TMU rounding</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="tiny-label">Rounded TMU final</div>
                <div class="big-number">{results["rounded_percent"]}%</div>
                <div class="subtle">{results["letter"]} · GPA {results["gpa"]:.2f}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    c3, c4 = st.columns(2)
    with c3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="tiny-label">Earned so far</div>
                <div class="big-number">{results["weighted_earned"]:.2f}%</div>
                <div class="subtle">Before final exam contribution</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c4:
        total_weight = results["total_weight"]
        weight_msg = "Perfect 100%" if abs(total_weight - 100) < 1e-9 else f"{total_weight:.1f}% total"
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="tiny-label">Weights check</div>
                <div class="big-number">{weight_msg}</div>
                <div class="subtle">Coursework + final exam</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

if abs(results["total_weight"] - 100) > 0.001:
    st.warning(
        f"Your weights currently add up to {results['total_weight']:.1f}%. "
        "For an accurate course prediction, make the total exactly 100%."
    )

# ---------------------------
# Tabs
# ---------------------------
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Final Exam Simulator", "TMU Scale", "Breakdown"])

with tab1:
    if default_chart == "Gauge":
        st.plotly_chart(gauge_chart(results["projected_percent"]), use_container_width=True, key="overview_gauge")
    elif default_chart == "Scenario Simulator":
        st.plotly_chart(
            scenario_chart(results["weighted_earned"], st.session_state.final_exam_weight_tmu, st.session_state.final_exam_score_tmu),
            use_container_width=True,
            key="overview_scenario"
        )
    elif default_chart == "Impact Bar":
        st.plotly_chart(impact_chart(results["weighted_earned"], results["exam_contribution"]), use_container_width=True, key="overview_impact")
    elif default_chart == "Weight Donut":
        st.plotly_chart(weight_donut(results["df"], st.session_state.final_exam_weight_tmu), use_container_width=True, key="overview_donut")
    elif default_chart == "Assessment Breakdown":
        st.plotly_chart(assessment_chart(results["df"]), use_container_width=True, key="overview_breakdown")
    elif default_chart == "Category Radar":
        radar = category_radar(results["df"])
        if radar is not None:
            st.plotly_chart(radar, use_container_width=True, key="overview_radar")
        else:
            st.info("Add at least two categories to unlock the radar chart.")

    oc1, oc2 = st.columns(2)
    with oc1:
        st.plotly_chart(gauge_chart(results["projected_percent"]), use_container_width=True, key="overview_gauge_2")
    with oc2:
        st.plotly_chart(impact_chart(results["weighted_earned"], results["exam_contribution"]), use_container_width=True, key="overview_impact_2")

with tab2:
    st.markdown("### Final Exam What-If")
    st.markdown("Use the sidebar slider to test different final exam scores and see the rounded TMU result update.")
    st.plotly_chart(
        scenario_chart(results["weighted_earned"], st.session_state.final_exam_weight_tmu, st.session_state.final_exam_score_tmu),
        use_container_width=True,
        key="simulator_chart"
    )
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        need = results["needed"][50]
        st.metric("Need for D-", "N/A" if need is None else f"{need:.1f}%")
    with s2:
        need = results["needed"][67]
        st.metric("Need for C+", "N/A" if need is None else f"{need:.1f}%")
    with s3:
        need = results["needed"][80]
        st.metric("Need for A-", "N/A" if need is None else f"{need:.1f}%")
    with s4:
        need = results["needed"][90]
        st.metric("Need for A+", "N/A" if need is None else f"{need:.1f}%")

with tab3:
    st.markdown("### TMU Undergraduate Grade Scale")
    st.markdown(
        """
        <div class="policy-box">
            Final percentage grades are rounded to the nearest integer using standard mathematical rounding
            before converting to the TMU letter grade and 4.33 GPA scale.
            <br><br>
            Examples:
            <b>49.5%</b> becomes <b>50%</b> • <b>49.4%</b> becomes <b>49%</b>
        </div>
        """,
        unsafe_allow_html=True,
    )
    scale_df = pd.DataFrame(
        [
            ["A+", "90-100%", 4.33],
            ["A", "85-89%", 4.00],
            ["A-", "80-84%", 3.67],
            ["B+", "77-79%", 3.33],
            ["B", "73-76%", 3.00],
            ["B-", "70-72%", 2.67],
            ["C+", "67-69%", 2.33],
            ["C", "63-66%", 2.00],
            ["C-", "60-62%", 1.67],
            ["D+", "57-59%", 1.33],
            ["D", "53-56%", 1.00],
            ["D-", "50-52%", 0.67],
            ["F", "0-49%", 0.00],
            ["F-S", "nil", 0.00],
            ["FNA", "nil", 0.00],
        ],
        columns=["Letter Grade", "Percentage Range", "Grade Points"]
    )
    st.dataframe(scale_df, use_container_width=True, hide_index=True)
    st.info("FNA = Failure Non-Assessment. F-S = Failed, with the opportunity to write a supplemental exam.")

with tab4:
    bc1, bc2 = st.columns(2)
    with bc1:
        st.plotly_chart(assessment_chart(results["df"]), use_container_width=True, key="breakdown_chart")
    with bc2:
        radar = category_radar(results["df"])
        if radar is not None:
            st.plotly_chart(radar, use_container_width=True, key="breakdown_radar")
        else:
            st.plotly_chart(weight_donut(results["df"], st.session_state.final_exam_weight_tmu), use_container_width=True, key="breakdown_donut")

    breakdown = results["df"].copy()
    breakdown["Weighted Contribution (%)"] = breakdown["Grade (%)"] * breakdown["Weight (%)"] / 100
    st.dataframe(breakdown, use_container_width=True, hide_index=True)

st.markdown(
    f"""
    <div class="footer-note">
        TMU Grade Calculator • {course_name if course_name else "TMU Course"}{" • " + student_name if student_name else ""}
    </div>
    """,
    unsafe_allow_html=True,
)

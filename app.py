import streamlit as st
import pandas as pd
import plotly.express as px

# Page Setup
st.set_page_config(page_title="Grade Forecaster", page_icon="🎓", layout="wide")

# Custom Styling: Forest Green & Slate Gray
st.markdown("""
<style>
.stApp {
    background-color: #f7fcf7; /* Very light green background */
}
h1, h2, h3 {
    color: #1b5e20; /* Deep forest green */
}
</style>
""", unsafe_allow_html=True)

st.title("🎓 The Grade Forecaster")
st.write("Track your semester progress, visualize your performance, and calculate exactly what you need on the final.")

# 1. Name Section
student_name = st.text_input("Student Name:", placeholder="e.g., Kaaren")

st.header("1. Your Grades So Far")
st.write("Add your completed assignments below. You can click the table to add new rows or change the names. The app will calculate your remaining final exam weight automatically.")

# 2. Grade & Weight Section (Dynamic Table)
if 'grades' not in st.session_state:
    st.session_state.grades = pd.DataFrame({
        "Assignment Name": ["ACC100 Midterm", "QMS Assignment"],
        "Grade (%)": [75.0, 85.0],
        "Weight (%)": [25.0, 15.0]
    })

edited_df = st.data_editor(
    st.session_state.grades, 
    num_rows="dynamic", 
    use_container_width=True,
    column_config={
        "Grade (%)": st.column_config.NumberColumn("Grade (%)", min_value=0.0, max_value=100.0, format="%.1f"),
        "Weight (%)": st.column_config.NumberColumn("Weight (%)", min_value=0.0, max_value=100.0, format="%.1f")
    }
)

# Background Math
total_weight = edited_df["Weight (%)"].sum()
current_earned = (edited_df["Grade (%)"] * (edited_df["Weight (%)"] / 100)).sum()

if total_weight >= 100:
    st.error("Wait! Your weights add up to 100% or more. Please check your numbers.")
else:
    final_weight = 100 - total_weight
    st.info(f"Your remaining final exam weight is **{final_weight:.1f}%**.")

    # 3. The Final Exam Slider
    st.header("2. Final Exam Scenario")
    expected_final = st.slider("If I score this on my final exam...", min_value=0, max_value=100, value=60)

    overall_grade = current_earned + (expected_final * (final_weight / 100))

    display_name = student_name if student_name else "Your"
    st.metric(label=f"Predicted Overall Course Grade for {display_name}", value=f"{overall_grade:.2f}%")

    # 4. Visualizations Section
    st.header("3. Performance Breakdown")
    col1, col2 = st.columns(2) # Splits the layout into two halves

    with col1:
        # Bar chart for Grades
        fig_bar = px.bar(edited_df, x="Assignment Name", y="Grade (%)", title="Scores per Assignment")
        fig_bar.update_traces(marker_color='#2e7d32') # Forest Green
        fig_bar.update_yaxes(range=[0, 100])
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        # Pie chart for Weights
        pie_data = edited_df.copy()
        # Add the final exam to the pie chart dynamically
        pie_data = pd.concat([pie_data, pd.DataFrame({"Assignment Name": ["Final Exam"], "Weight (%)": [final_weight]})])
        
        fig_pie = px.pie(pie_data, values="Weight (%)", names="Assignment Name", title="Course Weight Distribution")
        # Custom color palette: Greens transitioning into Slate Gray
        fig_pie.update_traces(marker=dict(colors=['#2e7d32', '#4caf50', '#81c784', '#cfd8dc', '#607d8b'])) 
        st.plotly_chart(fig_pie, use_container_width=True)

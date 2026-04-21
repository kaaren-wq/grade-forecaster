import streamlit as st

# App Header
st.set_page_config(page_title="Grade Forecaster", page_icon="🎓")
st.title("🎓 The Grade Forecaster")
st.write("Calculate exactly what you need on your final exam to reach your goal.")

# Sidebar for inputs (keeps the UI clean)
st.sidebar.header("Current Progress")
current_earned = st.sidebar.number_input("Total points earned so far:", min_value=0.0, value=32.25, step=0.5)
final_weight = st.sidebar.number_input("Final exam weight (%):", min_value=0.0, max_value=100.0, value=45.0, step=1.0)

# Main interaction area
st.subheader("Final Exam Scenario")
expected_final_score = st.slider("Expected Final Exam Score (%)", min_value=0, max_value=100, value=60)

# The Math
points_from_final = expected_final_score * (final_weight / 100)
overall_grade = current_earned + points_from_final

# Display Results
st.metric(label="Predicted Overall Course Grade", value=f"{overall_grade:.2f}%")

# Dynamic Status Logic
if overall_grade < 50:
    st.error("Status: Failing 🚨")
elif overall_grade < 60:
    st.warning("Status: Pass ⚠️")
elif overall_grade < 70:
    st.success("Status: Satisfactory ✅")
else:
    st.info("Status: Good Standing 🌟")
    st.balloons() # Adds a fun visual effect for high scores

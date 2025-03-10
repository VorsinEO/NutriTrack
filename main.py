import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
from utils import load_data, save_data, calculate_daily_totals

# Page config
st.set_page_config(
    page_title="Nutrition Tracker",
    page_icon="🥗",
    layout="wide"
)

# Load custom CSS
with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Initialize session state
if 'goals' not in st.session_state:
    st.session_state.goals = {
        'calories': 2000,
        'protein': 150
    }

# Sidebar for goals
st.sidebar.title("Set Your Goals")
st.session_state.goals['calories'] = st.sidebar.number_input(
    "Daily Calorie Goal",
    min_value=1000,
    max_value=5000,
    value=st.session_state.goals['calories']
)
st.session_state.goals['protein'] = st.sidebar.number_input(
    "Daily Protein Goal (g)",
    min_value=30,
    max_value=300,
    value=st.session_state.goals['protein']
)

# Main content
st.title("🥗 Nutrition Tracker")

# Tabs
tab1, tab2, tab3 = st.tabs(["Log Entry", "Dashboard", "History"])

with tab1:
    st.header("Log Your Meal")

    # Date and time selection
    col1, col2 = st.columns(2)
    with col1:
        entry_date = st.date_input("Date", datetime.now())
    with col2:
        entry_time = st.time_input("Time", datetime.now().time())

    # Combine date and time
    entry_datetime = datetime.combine(entry_date, entry_time)

    col1, col2, col3 = st.columns(3)

    with col1:
        food_name = st.text_input("Food Name")
    with col2:
        calories = st.number_input("Calories", min_value=0, max_value=2000)
    with col3:
        protein = st.number_input("Protein (g)", min_value=0, max_value=200)

    if st.button("Add Entry"):
        if food_name and calories >= 0 and protein >= 0:
            new_entry = {
                'datetime': entry_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                'date': entry_datetime.strftime('%Y-%m-%d'),
                'food_name': food_name,
                'calories': calories,
                'protein': protein
            }
            df = load_data()
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            save_data(df)
            st.success("Entry added successfully!")
        else:
            st.error("Please fill in all fields correctly.")

with tab2:
    st.header("Daily Progress")

    # Load and process data
    df = load_data()
    today = datetime.now().strftime('%Y-%m-%d')
    daily_totals = calculate_daily_totals(df)
    today_totals = daily_totals.get(today, {'calories': 0, 'protein': 0})

    # Progress metrics
    col1, col2 = st.columns(2)

    with col1:
        calories_progress = (today_totals['calories'] / st.session_state.goals['calories']) * 100
        st.metric(
            "Calories",
            f"{today_totals['calories']}/{st.session_state.goals['calories']}",
            f"{calories_progress:.1f}% of daily goal"
        )

        # Calories gauge
        fig_calories = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = calories_progress,
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': "#28a745"},
                'steps': [
                    {'range': [0, 33], 'color': "lightgray"},
                    {'range': [33, 66], 'color': "gray"},
                    {'range': [66, 100], 'color': "darkgray"}
                ]
            }
        ))
        fig_calories.update_layout(height=200, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_calories, use_container_width=True)

    with col2:
        protein_progress = (today_totals['protein'] / st.session_state.goals['protein']) * 100
        st.metric(
            "Protein",
            f"{today_totals['protein']}/{st.session_state.goals['protein']}g",
            f"{protein_progress:.1f}% of daily goal"
        )

        # Protein gauge
        fig_protein = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = protein_progress,
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': "#007bff"},
                'steps': [
                    {'range': [0, 33], 'color': "lightgray"},
                    {'range': [33, 66], 'color': "gray"},
                    {'range': [66, 100], 'color': "darkgray"}
                ]
            }
        ))
        fig_protein.update_layout(height=200, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_protein, use_container_width=True)

with tab3:
    st.header("History")

    # Date and time range selector
    col1, col2 = st.columns(2)
    with col1:
        start_datetime = st.date_input(
            "Start Date",
            datetime.now() - timedelta(days=7)
        )
        start_time = st.time_input("Start Time", datetime.min.time())
        start = datetime.combine(start_datetime, start_time)
    with col2:
        end_datetime = st.date_input(
            "End Date",
            datetime.now()
        )
        end_time = st.time_input("End Time", datetime.max.time())
        end = datetime.combine(end_datetime, end_time)

    # Filter data by datetime range
    df['datetime'] = pd.to_datetime(df['datetime'])
    mask = (df['datetime'] >= pd.Timestamp(start)) & (df['datetime'] <= pd.Timestamp(end))
    filtered_df = df.loc[mask]

    # Timeline charts
    daily_calories = filtered_df.groupby('date')['calories'].sum().reset_index()
    daily_protein = filtered_df.groupby('date')['protein'].sum().reset_index()

    fig_timeline = px.line(
        daily_calories,
        x='date',
        y='calories',
        title='Daily Calorie Intake'
    )
    fig_timeline.add_hline(
        y=st.session_state.goals['calories'],
        line_dash="dash",
        annotation_text="Goal"
    )
    st.plotly_chart(fig_timeline, use_container_width=True)

    fig_protein = px.line(
        daily_protein,
        x='date',
        y='protein',
        title='Daily Protein Intake'
    )
    fig_protein.add_hline(
        y=st.session_state.goals['protein'],
        line_dash="dash",
        annotation_text="Goal"
    )
    st.plotly_chart(fig_protein, use_container_width=True)

    # Detailed log
    st.subheader("Detailed Log")
    st.dataframe(
        filtered_df.sort_values('datetime', ascending=False)[['datetime', 'food_name', 'calories', 'protein']],
        use_container_width=True
    )
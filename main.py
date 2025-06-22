import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
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
        'calories': 2200,
        'protein': 130
    }

# Initialize datetime session states
if 'entry_date' not in st.session_state:
    st.session_state.entry_date = datetime.now().date()
if 'entry_time' not in st.session_state:
    st.session_state.entry_time = datetime.now().time()
if 'start_date' not in st.session_state:
    st.session_state.start_date = (datetime.now() - timedelta(days=7)).date()
if 'end_date' not in st.session_state:
    st.session_state.end_date = datetime.now().date()
if 'start_time' not in st.session_state:
    st.session_state.start_time = datetime.min.time()
if 'end_time' not in st.session_state:
    st.session_state.end_time = datetime.max.time()
if 'editing_meal' not in st.session_state:
    st.session_state.editing_meal = None

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
        entry_date = st.date_input(
            "Date",
            value=st.session_state.entry_date,
            key="entry_date_input"
        )
        st.session_state.entry_date = entry_date
    with col2:
        entry_time = st.time_input(
            "Time",
            value=st.session_state.entry_time,
            key="entry_time_input"
        )
        st.session_state.entry_time = entry_time

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
        start_date = st.date_input(
            "Start Date",
            value=st.session_state.start_date,
            key="start_date_input"
        )
        st.session_state.start_date = start_date

        start_time = st.time_input(
            "Start Time",
            value=st.session_state.start_time,
            key="start_time_input"
        )
        st.session_state.start_time = start_time

        start = datetime.combine(start_date, start_time)

    with col2:
        end_date = st.date_input(
            "End Date",
            value=st.session_state.end_date,
            key="end_date_input"
        )
        st.session_state.end_date = end_date

        end_time = st.time_input(
            "End Time",
            value=st.session_state.end_time,
            key="end_time_input"
        )
        st.session_state.end_time = end_time

        end = datetime.combine(end_date, end_time)

    # Filter data by datetime range
    df['datetime'] = pd.to_datetime(df['datetime'])
    mask = (df['datetime'] >= pd.Timestamp(start)) & (df['datetime'] <= pd.Timestamp(end))
    filtered_df = df.loc[mask]
    
    # Export functionality
    st.subheader("Export Data")
    if not filtered_df.empty:
        # Prepare data for export
        export_df = filtered_df[['datetime', 'calories', 'protein', 'food_name']].copy()
        export_df.rename(columns={'calories': 'kcal'}, inplace=True)
        
        # Convert to CSV
        csv = export_df.to_csv(index=False)
        
        # Create download button
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"nutrition_data_{start_date}_to_{end_date}.csv",
            mime="text/csv",
            key="download-csv",
            help="Download the filtered data as a CSV file"
        )
    else:
        st.info("No data available to export in the selected date range.")

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

    # Detailed log with edit and delete functionality
    st.subheader("Detailed Log")

    # Get last 5 entries sorted by datetime
    sorted_df = filtered_df.sort_values('datetime', ascending=False).head(5)

    # Display each meal entry with edit and delete buttons
    for idx, row in sorted_df.iterrows():
        with st.container():
            col1, col2, col3, col4, col5, col6 = st.columns([2, 1, 1, 1, 0.5, 0.5])

            # If this meal is being edited, show input fields
            if st.session_state.editing_meal == idx:
                with col1:
                    new_food_name = st.text_input("Food Name", value=row['food_name'], key=f"edit_name_{idx}")
                with col2:
                    new_datetime = st.text_input("Datetime", value=row['datetime'], key=f"edit_datetime_{idx}")
                with col3:
                    new_calories = st.number_input("Calories", value=row['calories'], key=f"edit_calories_{idx}")
                with col4:
                    new_protein = st.number_input("Protein", value=row['protein'], key=f"edit_protein_{idx}")
                with col5:
                    if st.button("Save", key=f"save_{idx}"):
                        parsed_dt = pd.to_datetime(new_datetime, errors="coerce")
                        if pd.isna(parsed_dt):
                            st.error("Invalid datetime format. Use YYYY-MM-DD HH:MM:SS")
                        else:
                            df.loc[idx, 'food_name'] = new_food_name
                            df.loc[idx, 'datetime'] = parsed_dt.strftime('%Y-%m-%d %H:%M:%S')
                            df.loc[idx, 'calories'] = new_calories
                            df.loc[idx, 'protein'] = new_protein
                            df.loc[idx, 'date'] = parsed_dt.strftime('%Y-%m-%d')
                            save_data(df)
                            st.session_state.editing_meal = None
                            st.rerun()
                with col6:
                    if st.button("Cancel", key=f"cancel_{idx}"):
                        st.session_state.editing_meal = None
                        st.rerun()
            else:
                # Display meal information
                col1.write(row['food_name'])
                col2.write(row['datetime'])
                col3.write(f"{row['calories']} cal")
                col4.write(f"{row['protein']}g")

                # Edit button
                if col5.button("✏️", key=f"edit_{idx}"):
                    st.session_state.editing_meal = idx
                    st.rerun()

                # Delete button
                if col6.button("🗑️", key=f"delete_{idx}"):
                    if st.session_state.editing_meal is None:  # Prevent deletion while editing
                        df = df.drop(idx)
                        save_data(df)
                        st.rerun()

            st.divider()

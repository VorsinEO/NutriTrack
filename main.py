import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import altair as alt
from datetime import datetime, timedelta
from utils import load_data, save_data, calculate_daily_totals, load_today_data, load_history_data

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

# Function to load fresh data
def load_fresh_data():
    """Load fresh data from Supabase/CSV"""
    return load_data()

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

# Add refresh button in sidebar
if st.sidebar.button("🔄 Refresh Data"):
    st.rerun()

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
            
            # Save directly to Supabase
            try:
                from supabase_client import get_supabase_manager
                supabase = get_supabase_manager()
                supabase.insert_entry(new_entry)
                st.success("Entry added successfully to Supabase!")
                st.rerun()  # Refresh the page to show new data
            except Exception as e:
                st.error(f"Error saving to Supabase: {e}")
                # Fallback to CSV
                df = load_data()
                df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
                save_data(df)
                st.success("Entry added successfully (saved to CSV as fallback)!")
                st.rerun()
        else:
            st.error("Please fill in all fields correctly.")

with tab2:
    st.header("Daily Progress")

    # Load fresh data
    df = load_today_data()
    
    # Show data source info
    if not df.empty:
        st.info(f"📊 Loaded {len(df)} entries from database")
    else:
        st.warning("No data found. Add some entries in the Log Entry tab!")
    
    # Calculate today's totals - FIX: use proper date comparison
    today = datetime.now().date()
    
    # Ensure date column is in the right format for comparison
    if not df.empty and 'date' in df.columns:
        if df['date'].dtype == 'object':
            df['date'] = pd.to_datetime(df['date']).dt.date
        elif hasattr(df['date'], 'dt'):
            df['date'] = df['date'].dt.date
        
        # Filter data for today only
        today_data = df[df['date'] == today]
        
        # Calculate today's totals
        today_totals = {
            'calories': today_data['calories'].sum() if not today_data.empty else 0,
            'protein': today_data['protein'].sum() if not today_data.empty else 0
        }
    else:
        today_totals = {'calories': 0, 'protein': 0}

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
            mode = "gauge",
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
        fig_calories.add_annotation(
            x=0.5,
            y=0.35,
            text=f"{calories_progress:.1f}%",
            showarrow=False,
            font=dict(size=40, color="black"),
            align="center"
        )
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
            mode = "gauge",
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
        fig_protein.add_annotation(
            x=0.5,
            y=0.35,
            text=f"{protein_progress:.1f}%",
            showarrow=False,
            font=dict(size=40, color="black"),
            align="center"
        )
        st.plotly_chart(fig_protein, use_container_width=True)

    # Show today's entries only
    if not df.empty and 'date' in df.columns:
        today_entries = df[df['date'] == today].sort_values('datetime', ascending=False)
        
        if not today_entries.empty:
            st.subheader(f"Today's Entries ({len(today_entries)} meals)")
            for _, row in today_entries.iterrows():
                st.write(f"🕐 {row['datetime'].strftime('%H:%M')} - {row['food_name']} ({row['calories']} cal, {row['protein']}g protein)")
        else:
            st.subheader("Today's Entries")
            st.info("No entries for today yet. Add your first meal in the Log Entry tab!")
    else:
        st.subheader("Today's Entries")
        st.info("No data available. Add some entries in the Log Entry tab!")

with tab3:
    st.header("History")

    # Load fresh data
    df = load_fresh_data()

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

    # Load data based on the selected date range
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    df = load_history_data(start_str, end_str)

    # Filter data by datetime range
    if not df.empty:
        # Ensure datetime column is properly formatted and timezone-naive
        df['datetime'] = pd.to_datetime(df['datetime']).dt.tz_localize(None)
        
        # Convert start and end to timezone-naive timestamps
        start_ts = pd.Timestamp(start).tz_localize(None)
        end_ts = pd.Timestamp(end).tz_localize(None)
        
        mask = (df['datetime'] >= start_ts) & (df['datetime'] <= end_ts)
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

        # Charts for historical analysis
        if not filtered_df.empty:
            st.subheader("Historical Analysis")
            
            # Daily totals for the selected period
            daily_totals = filtered_df.groupby('date').agg({
                'calories': 'sum',
                'protein': 'sum'
            }).reset_index()
            
            # Sort by date to ensure the chart is in chronological order
            daily_totals = daily_totals.sort_values('date')

            if not daily_totals.empty:
                # Calories Chart using Altair
                st.write("#### Daily Calorie Intake")
                calories_chart = alt.Chart(daily_totals).mark_bar().encode(
                    x=alt.X('date:T', title='Date', axis=alt.Axis(format='%Y-%m-%d')),
                    y=alt.Y('calories:Q', title='Calories'),
                    tooltip=[alt.Tooltip('date:T', title='Date'), alt.Tooltip('calories:Q', title='Calories')]
                ).properties(
                    height=300
                )
                calories_goal_line = alt.Chart(pd.DataFrame({'goal': [st.session_state.goals['calories']]})).mark_rule(color='red', strokeDash=[5,5]).encode(y='goal:Q')
                st.altair_chart(calories_chart + calories_goal_line, use_container_width=True)

                # Protein Chart using Altair
                st.write("#### Daily Protein Intake")
                protein_chart = alt.Chart(daily_totals).mark_bar().encode(
                    x=alt.X('date:T', title='Date', axis=alt.Axis(format='%Y-%m-%d')),
                    y=alt.Y('protein:Q', title='Protein (g)'),
                    tooltip=[alt.Tooltip('date:T', title='Date'), alt.Tooltip('protein:Q', title='Protein (g)')]
                ).properties(
                    height=300
                )
                protein_goal_line = alt.Chart(pd.DataFrame({'goal': [st.session_state.goals['protein']]})).mark_rule(color='red', strokeDash=[5,5]).encode(y='goal:Q')
                st.altair_chart(protein_chart + protein_goal_line, use_container_width=True)
            
            # Meal distribution pie chart
            st.subheader("Meal Distribution")
            meal_counts = filtered_df['food_name'].value_counts().head(10)
            if not meal_counts.empty:
                fig_pie = px.pie(
                    values=meal_counts.values,
                    names=meal_counts.index,
                    title="Most Common Meals in Selected Period"
                )
                st.plotly_chart(fig_pie, use_container_width=True)

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
                                # Update in Supabase
                                try:
                                    from supabase_client import get_supabase_manager
                                    supabase = get_supabase_manager()
                                    
                                    updates = {
                                        'food_name': new_food_name,
                                        'datetime': parsed_dt.strftime('%Y-%m-%d %H:%M:%S'),
                                        'date': parsed_dt.strftime('%Y-%m-%d'),
                                        'calories': new_calories,
                                        'protein': new_protein
                                    }
                                    
                                    # Get the actual ID from Supabase
                                    entry_id = row.get('id')
                                    if entry_id:
                                        supabase.update_entry(entry_id, updates)
                                        st.success("Entry updated in Supabase!")
                                    else:
                                        st.error("Cannot update: missing entry ID")
                                    
                                    st.session_state.editing_meal = None
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error updating in Supabase: {e}")
                                    # Fallback to CSV
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
                            try:
                                from supabase_client import get_supabase_manager
                                supabase = get_supabase_manager()
                                
                                entry_id = row.get('id')
                                if entry_id:
                                    supabase.delete_entry(entry_id)
                                    st.success("Entry deleted from Supabase!")
                                else:
                                    st.error("Cannot delete: missing entry ID")
                                
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting from Supabase: {e}")
                                # Fallback to CSV
                                df = df.drop(idx)
                                save_data(df)
                                st.rerun()

                st.divider()
    else:
        st.warning("No data available. Add some entries in the Log Entry tab!")

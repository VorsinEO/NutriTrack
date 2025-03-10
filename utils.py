import pandas as pd
from datetime import datetime
import os

def load_data():
    """Load the food log data from CSV file"""
    if not os.path.exists('data'):
        os.makedirs('data')

    if os.path.exists('data/food_log.csv'):
        df = pd.read_csv('data/food_log.csv')
        # Convert datetime string to datetime object if it exists
        if 'datetime' in df.columns:
            try:
                df['datetime'] = pd.to_datetime(df['datetime'])
                df['date'] = df['datetime'].dt.date.astype(str)
            except Exception as e:
                print(f"Error converting datetime: {e}")
                # Create datetime from date if time is missing
                df['datetime'] = pd.to_datetime(df['date'] + ' 00:00:00')
        return df
    else:
        return pd.DataFrame(columns=['datetime', 'date', 'food_name', 'calories', 'protein'])

def save_data(df):
    """Save the food log data to CSV file"""
    # Create a copy to avoid modifying the original DataFrame
    df_save = df.copy()

    # Convert datetime column to string format for CSV storage
    if 'datetime' in df_save.columns:
        # Convert to datetime first to ensure proper formatting
        df_save['datetime'] = pd.to_datetime(df_save['datetime'])
        # Then convert to string
        df_save['datetime'] = df_save['datetime'].astype(str)

    df_save.to_csv('data/food_log.csv', index=False)

def calculate_daily_totals(df):
    """Calculate daily totals for calories and protein"""
    if df.empty:
        return {}

    daily_totals = {}
    for date in df['date'].unique():
        daily_data = df[df['date'] == date]
        daily_totals[date] = {
            'calories': daily_data['calories'].sum(),
            'protein': daily_data['protein'].sum()
        }

    return daily_totals
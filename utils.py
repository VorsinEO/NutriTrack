import pandas as pd
from datetime import datetime
import os

def load_data():
    """Load the food log data from CSV file"""
    if not os.path.exists('data'):
        os.makedirs('data')
    
    if os.path.exists('data/food_log.csv'):
        return pd.read_csv('data/food_log.csv')
    else:
        return pd.DataFrame(columns=['date', 'food_name', 'calories', 'protein'])

def save_data(df):
    """Save the food log data to CSV file"""
    df.to_csv('data/food_log.csv', index=False)

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

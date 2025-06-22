import pandas as pd
from datetime import datetime, timedelta
import os
from supabase_client import get_supabase_manager

def _process_df(df: pd.DataFrame) -> pd.DataFrame:
    """Helper function to process dataframe from Supabase."""
    if df.empty:
        return df
    # Convert datetime strings to datetime objects and normalize timezone
    df['datetime'] = pd.to_datetime(df['datetime']).dt.tz_localize(None)
    
    # Handle date column properly
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date']).dt.date
    else:
        # Create date column from datetime if it doesn't exist
        df['date'] = df['datetime'].dt.date
    return df

def load_data() -> pd.DataFrame:
    """Load data from Supabase and return as DataFrame."""
    try:
        supabase = get_supabase_manager()
        entries = supabase.get_all_entries()
        
        print(f"Loaded {len(entries)} entries from Supabase")
        
        if entries:
            df = pd.DataFrame(entries)
            # Convert datetime strings to datetime objects and normalize timezone
            df['datetime'] = pd.to_datetime(df['datetime']).dt.tz_localize(None)
            
            # Handle date column properly
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date']).dt.date
            else:
                # Create date column from datetime if it doesn't exist
                df['date'] = df['datetime'].dt.date
                
            print(f"DataFrame shape: {df.shape}")
            print(f"Columns: {df.columns.tolist()}")
            return df
        else:
            print("No entries found in Supabase")
            # Return empty DataFrame with correct columns
            return pd.DataFrame(columns=['id', 'datetime', 'date', 'food_name', 'calories', 'protein'])
    except Exception as e:
        print(f"Error loading data from Supabase: {e}")
        # Fallback to CSV if Supabase fails
        csv_path = 'data/food_log.csv'
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            df['datetime'] = pd.to_datetime(df['datetime'])
            df['date'] = pd.to_datetime(df['date']).dt.date
            print(f"Loaded {len(df)} entries from CSV fallback")
            return df
        return pd.DataFrame(columns=['datetime', 'date', 'food_name', 'calories', 'protein'])

def save_data(df: pd.DataFrame) -> bool:
    """Save data to Supabase."""
    try:
        supabase = get_supabase_manager()
        
        # Get the last entry to avoid duplicates
        existing_entries = supabase.get_all_entries()
        existing_count = len(existing_entries)
        
        # Only save new entries
        if len(df) > existing_count:
            new_entries = df.tail(len(df) - existing_count)
            
            for _, row in new_entries.iterrows():
                entry = {
                    'datetime': row['datetime'].strftime('%Y-%m-%d %H:%M:%S') if hasattr(row['datetime'], 'strftime') else str(row['datetime']),
                    'date': row['date'].strftime('%Y-%m-%d') if hasattr(row['date'], 'strftime') else str(row['date']),
                    'food_name': row['food_name'],
                    'calories': int(row['calories']),
                    'protein': int(row['protein'])
                }
                supabase.insert_entry(entry)
        
        return True
    except Exception as e:
        print(f"Error saving data to Supabase: {e}")
        # Fallback to CSV
        csv_path = 'data/food_log.csv'
        df.to_csv(csv_path, index=False)
        return False

def calculate_daily_totals(df: pd.DataFrame) -> dict:
    """Calculate daily totals for calories and protein."""
    if df.empty:
        return {}
    
    # Ensure date column is in the right format
    if 'date' in df.columns:
        if df['date'].dtype == 'object':
            df['date'] = pd.to_datetime(df['date']).dt.date
        elif hasattr(df['date'], 'dt'):
            df['date'] = df['date'].dt.date
    
    daily_totals = df.groupby('date').agg({
        'calories': 'sum',
        'protein': 'sum'
    }).to_dict('index')
    
    return daily_totals

def sync_csv_to_supabase(csv_file_path: str = 'data/food_log.csv') -> int:
    """Sync existing CSV data to Supabase."""
    try:
        supabase = get_supabase_manager()
        return supabase.sync_from_csv(csv_file_path)
    except Exception as e:
        print(f"Error syncing CSV to Supabase: {e}")
        return 0

def export_supabase_to_csv(csv_file_path: str = 'data/food_log_backup.csv') -> bool:
    """Export Supabase data to CSV as backup."""
    try:
        supabase = get_supabase_manager()
        return supabase.export_to_csv(csv_file_path)
    except Exception as e:
        print(f"Error exporting Supabase to CSV: {e}")
        return False

def load_today_data() -> pd.DataFrame:
    """Load data for today from Supabase."""
    try:
        supabase = get_supabase_manager()
        entries = supabase.get_entries_for_today()
        print(f"Optimized Load: Fetched {len(entries)} entries for today.")
        if entries:
            return _process_df(pd.DataFrame(entries))
        return pd.DataFrame(columns=['id', 'datetime', 'date', 'food_name', 'calories', 'protein'])
    except Exception as e:
        print(f"Error loading today's data from Supabase: {e}")
        # For simplicity, no CSV fallback on optimized loads
        return pd.DataFrame(columns=['id', 'datetime', 'date', 'food_name', 'calories', 'protein'])

def load_history_data(start_date: str, end_date: str) -> pd.DataFrame:
    """Load data for a date range from Supabase."""
    try:
        supabase = get_supabase_manager()
        entries = supabase.get_entries_by_date_range(start_date, end_date)
        print(f"Optimized Load: Fetched {len(entries)} entries for range {start_date} to {end_date}.")
        if entries:
            return _process_df(pd.DataFrame(entries))
        return pd.DataFrame(columns=['id', 'datetime', 'date', 'food_name', 'calories', 'protein'])
    except Exception as e:
        print(f"Error loading history data from Supabase: {e}")
        # For simplicity, no CSV fallback on optimized loads
        return pd.DataFrame(columns=['id', 'datetime', 'date', 'food_name', 'calories', 'protein'])

import os
from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SupabaseManager:
    def __init__(self):
        """Initialize Supabase client with credentials from environment variables."""
        self.url = os.getenv("SUPABASE_URL")
        self.anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.table_name = os.getenv("SUPABASE_TABLE_NAME", "food_log")
        
        if not self.url or not self.anon_key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env file")
        
        self.client: Client = create_client(self.url, self.anon_key)
    
    def insert_entry(self, entry: Dict) -> Dict:
        """Insert a single food log entry into Supabase."""
        try:
            # Ensure datetime is in the correct format
            if 'datetime' in entry:
                entry['datetime'] = pd.to_datetime(entry['datetime']).strftime('%Y-%m-%d %H:%M:%S')
            if 'date' in entry:
                entry['date'] = pd.to_datetime(entry['date']).strftime('%Y-%m-%d')
            
            response = self.client.table(self.table_name).insert(entry).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error inserting entry: {e}")
            raise
    
    def get_all_entries(self) -> List[Dict]:
        """Get all food log entries from Supabase."""
        try:
            response = self.client.table(self.table_name).select("*").order("datetime", desc=True).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching entries: {e}")
            return []
    
    def get_entries_for_today(self) -> List[Dict]:
        """Get entries for the current day."""
        try:
            today_str = datetime.now().strftime('%Y-%m-%d')
            response = self.client.table(self.table_name)\
                .select("*")\
                .eq("date", today_str)\
                .order("datetime", desc=True)\
                .execute()
            return response.data
        except Exception as e:
            print(f"Error fetching today's entries: {e}")
            return []
    
    def get_entries_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """Get entries within a date range."""
        try:
            response = self.client.table(self.table_name)\
                .select("*")\
                .gte("date", start_date)\
                .lte("date", end_date)\
                .order("datetime", desc=True)\
                .execute()
            return response.data
        except Exception as e:
            print(f"Error fetching entries by date range: {e}")
            return []
    
    def update_entry(self, entry_id: int, updates: Dict) -> Dict:
        """Update an existing entry."""
        try:
            # Ensure datetime is in the correct format
            if 'datetime' in updates:
                updates['datetime'] = pd.to_datetime(updates['datetime']).strftime('%Y-%m-%d %H:%M:%S')
            if 'date' in updates:
                updates['date'] = pd.to_datetime(updates['date']).strftime('%Y-%m-%d')
            
            response = self.client.table(self.table_name)\
                .update(updates)\
                .eq("id", entry_id)\
                .execute()
            
            if response.data:
                print(f"Successfully updated entry {entry_id}")
                return response.data[0]
            else:
                print(f"No entry found with id {entry_id}")
                return None
        except Exception as e:
            print(f"Error updating entry {entry_id}: {e}")
            raise
    
    def delete_entry(self, entry_id: int) -> bool:
        """Delete an entry by ID."""
        try:
            response = self.client.table(self.table_name)\
                .delete()\
                .eq("id", entry_id)\
                .execute()
            
            if response.data:
                print(f"Successfully deleted entry {entry_id}")
                return True
            else:
                print(f"No entry found with id {entry_id}")
                return False
        except Exception as e:
            print(f"Error deleting entry {entry_id}: {e}")
            return False
    
    def sync_from_csv(self, csv_file_path: str) -> int:
        """Sync data from CSV file to Supabase."""
        try:
            df = pd.read_csv(csv_file_path)
            inserted_count = 0
            
            for _, row in df.iterrows():
                entry = {
                    'datetime': pd.to_datetime(row['datetime']).strftime('%Y-%m-%d %H:%M:%S'),
                    'date': pd.to_datetime(row['date']).strftime('%Y-%m-%d'),
                    'food_name': row['food_name'],
                    'calories': int(row['calories']),
                    'protein': int(row['protein'])
                }
                self.insert_entry(entry)
                inserted_count += 1
            
            return inserted_count
        except Exception as e:
            print(f"Error syncing from CSV: {e}")
            raise
    
    def export_to_csv(self, csv_file_path: str) -> bool:
        """Export all data from Supabase to CSV."""
        try:
            entries = self.get_all_entries()
            df = pd.DataFrame(entries)
            df.to_csv(csv_file_path, index=False)
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False

# Global instance
supabase_manager = None

def get_supabase_manager() -> SupabaseManager:
    """Get or create a global Supabase manager instance."""
    global supabase_manager
    if supabase_manager is None:
        supabase_manager = SupabaseManager()
    return supabase_manager 
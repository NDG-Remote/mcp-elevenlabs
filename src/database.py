import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_path="tts_history.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize the database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create settings table for storing user preferences
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        # Create history table for storing audio entries
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audio_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                audio_file TEXT NOT NULL,
                voice_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()

    def get_setting(self, key, default=None):
        """Get a setting value from the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else default

    def set_setting(self, key, value):
        """Set a setting value in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value)
            VALUES (?, ?)
        ''', (key, value))
        conn.commit()
        conn.close()

    def save_audio_entry(self, text, audio_file, voice_name):
        """Save a new audio entry to the database."""
        # Convert to relative path
        rel_audio_file = os.path.relpath(audio_file)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO audio_history (text, audio_file, voice_name)
            VALUES (?, ?, ?)
        ''', (text, rel_audio_file, voice_name))
        conn.commit()
        conn.close()

    def get_audio_history(self, limit=10):
        """Get the most recent audio entries."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT text, audio_file, voice_name, created_at
            FROM audio_history
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        entries = cursor.fetchall()
        conn.close()
        return entries

    def delete_audio_entry(self, audio_file):
        """Delete an audio entry from the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM audio_history 
                    WHERE audio_file = ?
                """, (audio_file,))
                conn.commit()
        except Exception as e:
            print(f"Error deleting audio entry: {str(e)}")
            raise 
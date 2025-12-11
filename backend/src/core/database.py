import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional, List, Dict
from datetime import datetime
from dotenv import load_dotenv
from src.data.ingestion import clean_env_var

load_dotenv()

class Database:
    """Database client for Neon Postgres."""
    def __init__(self):
        # Use clean_env_var to properly clean DATABASE_URL
        self.connection_string = clean_env_var(os.getenv("DATABASE_URL", ""))
        
        if not self.connection_string:
            print("Warning: DATABASE_URL not set. Database features will be disabled.")
            self.conn = None
        else:
            self._init_tables()
    
    def _get_connection(self):
        """Get database connection."""
        if not self.connection_string:
            return None
        try:
            # Fix channel_binding issue - remove "require" completely
            # PostgreSQL only supports channel_binding=disable or allow, not require
            conn_str = self.connection_string
            
            # Remove channel_binding=require completely
            import re
            # Remove channel_binding parameter if it exists
            conn_str = re.sub(r'[&?]channel_binding=[^&\s]*', '', conn_str)
            
            # For Supabase, ensure sslmode is set
            # Supabase requires SSL, so use 'require' or 'prefer'
            if "sslmode=" not in conn_str:
                separator = "&" if "?" in conn_str else "?"
                conn_str = f"{conn_str}{separator}sslmode=require"
            # Supabase works with sslmode=require, so keep it as is
            
            # Set connection timeout to avoid hanging
            return psycopg2.connect(conn_str, connect_timeout=10)
        except Exception as e:
            # Don't print full error in production - just log connection issue
            print(f"Error connecting to database: {e}")
            # Return None gracefully - app will work without database
            return None
    
    def _init_tables(self):
        """Initialize database tables."""
        conn = self._get_connection()
        if not conn:
            return
        
        try:
            with conn.cursor() as cur:
                # Create users table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id VARCHAR(255) PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        email VARCHAR(255) UNIQUE NOT NULL,
                        password VARCHAR(255) NOT NULL,
                        background JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create conversations table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS conversations (
                        id VARCHAR(255) PRIMARY KEY,
                        user_id VARCHAR(255),
                        session_id VARCHAR(255),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create messages table
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id VARCHAR(255) PRIMARY KEY,
                        conversation_id VARCHAR(255) REFERENCES conversations(id),
                        query_id VARCHAR(255),
                        query_text TEXT,
                        response_text TEXT,
                        selected_text TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                conn.commit()
                print("Database tables initialized successfully")
        except Exception as e:
            print(f"Error initializing tables: {e}")
        finally:
            conn.close()
    
    def save_conversation(self, conversation_id: str, user_id: Optional[str] = None, session_id: Optional[str] = None):
        """Save a conversation."""
        conn = self._get_connection()
        if not conn:
            return
        
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO conversations (id, user_id, session_id, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        updated_at = CURRENT_TIMESTAMP
                """, (conversation_id, user_id, session_id, datetime.utcnow(), datetime.utcnow()))
                conn.commit()
        except Exception as e:
            print(f"Error saving conversation: {e}")
        finally:
            conn.close()
    
    def save_message(self, message_id: str, conversation_id: str, query_id: str, 
                     query_text: str, response_text: str, selected_text: Optional[str] = None):
        """Save a message."""
        conn = self._get_connection()
        if not conn:
            return
        
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO messages (id, conversation_id, query_id, query_text, response_text, selected_text, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (message_id, conversation_id, query_id, query_text, response_text, selected_text, datetime.utcnow()))
                conn.commit()
        except Exception as e:
            print(f"Error saving message: {e}")
        finally:
            conn.close()
    
    def get_conversation_history(self, conversation_id: str, limit: int = 50) -> List[Dict]:
        """Get conversation history."""
        conn = self._get_connection()
        if not conn:
            return []
        
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM messages
                    WHERE conversation_id = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (conversation_id, limit))
                return cur.fetchall()
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            return []
        finally:
            conn.close()


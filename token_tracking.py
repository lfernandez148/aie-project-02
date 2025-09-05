# token_tracking.py
"""
Token usage tracking module for the campaign assistant chatbot.
Handles token usage statistics, database initialization, and user analytics.
"""

import sqlite3
from loguru import logger
from typing import Dict, Any, Optional, List

class TokenTracker:
    """Handles token usage tracking and analytics."""
    
    def __init__(self, db_connection: sqlite3.Connection):
        """Initialize token tracker with database connection."""
        self.conn = db_connection
        self.init_token_tracking()
    
    def init_token_tracking(self):
        """Initialize token usage tracking table and chat history table."""
        try:
            cursor = self.conn.cursor()
            
            # Token usage table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS token_usage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    thread_id TEXT,
                    input_tokens INTEGER DEFAULT 0,
                    output_tokens INTEGER DEFAULT 0,
                    total_tokens INTEGER DEFAULT 0,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Chat history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    thread_id TEXT NOT NULL,
                    role TEXT NOT NULL,  -- 'user' or 'assistant'
                    content TEXT NOT NULL,
                    response_type TEXT,  -- 'text', 'chart', 'table', 'error'
                    chart_type TEXT,
                    table_data TEXT,  -- JSON string for table data
                    source TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index for better performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_history_user_thread 
                ON chat_history(user_id, thread_id, timestamp)
            """)
            
            self.conn.commit()
            logger.info("Token tracking and chat history tables initialized")
        except Exception as e:
            logger.error(f"Error initializing tracking tables: {e}")

    def save_token_usage(self, user_id: str, thread_id: str, input_tokens: int, output_tokens: int):
        """Save token usage to database (without query text for privacy)."""
        try:
            total_tokens = input_tokens + output_tokens
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO token_usage (user_id, thread_id, input_tokens, output_tokens, total_tokens)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, thread_id, input_tokens, output_tokens, total_tokens))
            self.conn.commit()
            logger.info(f"Token usage saved - User: {user_id}, Thread: {thread_id}, Total: {total_tokens}")
        except Exception as e:
            logger.error(f"Error saving token usage: {e}")

    def get_user_token_stats(self, user_id: str) -> Dict[str, Any]:
        """Get token usage statistics for a specific user."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_queries,
                    SUM(input_tokens) as total_input_tokens,
                    SUM(output_tokens) as total_output_tokens,
                    SUM(total_tokens) as total_tokens,
                    AVG(total_tokens) as avg_tokens_per_query
                FROM token_usage 
                WHERE user_id = ?
            """, (user_id,))
            
            result = cursor.fetchone()
            if result and result[0] > 0:
                return {
                    "user_id": user_id,
                    "total_queries": result[0],
                    "total_input_tokens": result[1] or 0,
                    "total_output_tokens": result[2] or 0,
                    "total_tokens": result[3] or 0,
                    "avg_tokens_per_query": round(result[4] or 0, 2)
                }
            return {"user_id": user_id, "total_queries": 0, "total_tokens": 0}
            
        except Exception as e:
            logger.error(f"Error getting token stats: {e}")
            return {"status": "error", "message": str(e)}

    def get_user_recent_activity(self, user_id: str, limit: int = 10) -> Dict[str, Any]:
        """Get recent token usage activity for a user."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT 
                    thread_id,
                    input_tokens,
                    output_tokens,
                    total_tokens,
                    timestamp
                FROM token_usage 
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (user_id, limit))
            
            results = cursor.fetchall()
            activities = []
            for row in results:
                activities.append({
                    "thread_id": row[0],
                    "input_tokens": row[1],
                    "output_tokens": row[2],
                    "total_tokens": row[3],
                    "timestamp": row[4]
                })
            
            return {
                "user_id": user_id,
                "recent_activities": activities,
                "count": len(activities)
            }
            
        except Exception as e:
            logger.error(f"Error getting recent activity for user {user_id}: {e}")
            return {"status": "error", "message": str(e)}

    def save_chat_message(self, user_id: str, thread_id: str, role: str, content: str, 
                         response_type: str = "text", chart_type: str = None, 
                         table_data: str = None, source: str = None):
        """Save a chat message to the database."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO chat_history 
                (user_id, thread_id, role, content, response_type, chart_type, table_data, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, thread_id, role, content, response_type, chart_type, table_data, source))
            self.conn.commit()
            logger.info(f"Chat message saved - User: {user_id}, Thread: {thread_id}, Role: {role}")
        except Exception as e:
            logger.error(f"Error saving chat message: {e}")

    def get_chat_history(self, user_id: str, thread_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get chat history for a user and thread."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT role, content, response_type, chart_type, table_data, source, timestamp
                FROM chat_history 
                WHERE user_id = ? AND thread_id = ?
                ORDER BY timestamp ASC
                LIMIT ?
            """, (user_id, thread_id, limit))
            
            results = cursor.fetchall()
            history = []
            for row in results:
                message = {
                    "role": row[0],
                    "content": row[1],
                    "response_type": row[2],
                    "timestamp": row[6]
                }
                
                # Add optional fields if they exist
                if row[3]:  # chart_type
                    message["chart_type"] = row[3]
                if row[4]:  # table_data
                    import json
                    try:
                        message["table_data"] = json.loads(row[4])
                    except json.JSONDecodeError:
                        pass
                if row[5] and row[5].strip():  # source
                    message["source"] = row[5]
                
                history.append(message)
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting chat history for user {user_id}, thread {thread_id}: {e}")
            return []

    def clear_chat_history(self, user_id: str, thread_id: str):
        """Clear chat history for a specific user and thread."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM chat_history WHERE user_id = ? AND thread_id = ?", 
                          (user_id, thread_id))
            deleted_count = cursor.rowcount
            self.conn.commit()
            logger.info(f"Cleared {deleted_count} chat messages for user: {user_id}, thread: {thread_id}")
            return {"status": "success", "deleted_messages": deleted_count}
        except Exception as e:
            logger.error(f"Error clearing chat history for user {user_id}, thread {thread_id}: {e}")
            return {"status": "error", "message": str(e)}

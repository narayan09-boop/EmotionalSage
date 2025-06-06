import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import List, Dict, Optional
import json

class DatabaseManager:
    def __init__(self):
        self.connection_string = os.getenv("DATABASE_URL")
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.connection_string)
    
    def init_database(self):
        """Initialize database tables"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Create users table
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS users (
                            id SERIAL PRIMARY KEY,
                            session_id VARCHAR(255) UNIQUE NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Create emotion_history table
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS emotion_history (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                            session_id VARCHAR(255) NOT NULL,
                            text_input TEXT NOT NULL,
                            primary_emotion VARCHAR(50) NOT NULL,
                            confidence FLOAT NOT NULL,
                            secondary_emotions JSON,
                            sentiment_scores JSON,
                            textblob_polarity FLOAT,
                            textblob_subjectivity FLOAT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Create recommendations table
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS recommendations (
                            id SERIAL PRIMARY KEY,
                            emotion_history_id INTEGER REFERENCES emotion_history(id) ON DELETE CASCADE,
                            recommendation_type VARCHAR(20) NOT NULL, -- 'movie' or 'youtube'
                            content_data JSON NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    # Create user_preferences table
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS user_preferences (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                            preferred_emotions JSON,
                            favorite_genres JSON,
                            content_preferences JSON,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    conn.commit()
                    print("Database tables initialized successfully")
                    
        except Exception as e:
            print(f"Error initializing database: {str(e)}")
    
    def get_or_create_user(self, session_id: str) -> int:
        """Get existing user or create new one"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Try to get existing user
                    cur.execute("SELECT id FROM users WHERE session_id = %s", (session_id,))
                    result = cur.fetchone()
                    
                    if result:
                        # Update last_active
                        cur.execute(
                            "UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE session_id = %s",
                            (session_id,)
                        )
                        conn.commit()
                        return result[0]
                    else:
                        # Create new user
                        cur.execute(
                            "INSERT INTO users (session_id) VALUES (%s) RETURNING id",
                            (session_id,)
                        )
                        result = cur.fetchone()
                        if result:
                            user_id = result[0]
                            conn.commit()
                            return user_id
                        
        except Exception as e:
            print(f"Error getting/creating user: {str(e)}")
            return 1  # Return default user ID
    
    def save_emotion_analysis(self, session_id: str, text_input: str, emotion_result: Dict) -> Optional[int]:
        """Save emotion analysis to database"""
        try:
            user_id = self.get_or_create_user(session_id)
            if not user_id:
                return None
                
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO emotion_history 
                        (user_id, session_id, text_input, primary_emotion, confidence, 
                         secondary_emotions, sentiment_scores, textblob_polarity, textblob_subjectivity)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        user_id,
                        session_id,
                        text_input,
                        emotion_result.get('primary_emotion'),
                        emotion_result.get('confidence'),
                        json.dumps(emotion_result.get('secondary_emotions', [])),
                        json.dumps(emotion_result.get('sentiment_scores', {})),
                        emotion_result.get('textblob_polarity'),
                        emotion_result.get('textblob_subjectivity')
                    ))
                    
                    result = cur.fetchone()
                    if result:
                        emotion_history_id = result[0]
                        conn.commit()
                        return emotion_history_id
                    
        except Exception as e:
            print(f"Error saving emotion analysis: {str(e)}")
            return None
    
    def save_recommendations(self, emotion_history_id: int, recommendations: Dict):
        """Save recommendations to database"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    # Save movie recommendations
                    if recommendations.get('movies'):
                        for movie in recommendations['movies']:
                            cur.execute("""
                                INSERT INTO recommendations (emotion_history_id, recommendation_type, content_data)
                                VALUES (%s, %s, %s)
                            """, (emotion_history_id, 'movie', json.dumps(movie)))
                    
                    # Save YouTube recommendations
                    if recommendations.get('youtube_videos'):
                        for video in recommendations['youtube_videos']:
                            cur.execute("""
                                INSERT INTO recommendations (emotion_history_id, recommendation_type, content_data)
                                VALUES (%s, %s, %s)
                            """, (emotion_history_id, 'youtube', json.dumps(video)))
                    
                    conn.commit()
                    
        except Exception as e:
            print(f"Error saving recommendations: {str(e)}")
    
    def get_emotion_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Get emotion history for a user"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT text_input, primary_emotion, confidence, secondary_emotions, created_at
                        FROM emotion_history 
                        WHERE session_id = %s 
                        ORDER BY created_at DESC 
                        LIMIT %s
                    """, (session_id, limit))
                    
                    results = cur.fetchall()
                    
                    # Convert to list of dicts
                    history = []
                    for row in results:
                        history.append({
                            'text': row['text_input'][:100] + "..." if len(row['text_input']) > 100 else row['text_input'],
                            'emotion': row['primary_emotion'],
                            'confidence': row['confidence'],
                            'timestamp': row['created_at']
                        })
                    
                    return history
                    
        except Exception as e:
            print(f"Error getting emotion history: {str(e)}")
            return []
    
    def get_emotion_stats(self, session_id: str) -> Dict:
        """Get emotion statistics for a user"""
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Get emotion frequency
                    cur.execute("""
                        SELECT primary_emotion, COUNT(*) as count
                        FROM emotion_history 
                        WHERE session_id = %s 
                        GROUP BY primary_emotion 
                        ORDER BY count DESC
                    """, (session_id,))
                    
                    emotion_counts = {row[0]: row[1] for row in cur.fetchall()}
                    
                    # Get average confidence
                    cur.execute("""
                        SELECT AVG(confidence) as avg_confidence
                        FROM emotion_history 
                        WHERE session_id = %s
                    """, (session_id,))
                    
                    result = cur.fetchone()
                    avg_confidence = result['avg_confidence'] if result and result['avg_confidence'] else 0
                    
                    return {
                        'emotion_counts': emotion_counts,
                        'avg_confidence': float(avg_confidence)
                    }
                    
        except Exception as e:
            print(f"Error getting emotion stats: {str(e)}")
            return {'emotion_counts': {}, 'avg_confidence': 0}
    
    def clear_user_history(self, session_id: str):
        """Clear all history for a user"""
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM emotion_history WHERE session_id = %s", (session_id,))
                    conn.commit()
                    
        except Exception as e:
            print(f"Error clearing user history: {str(e)}")
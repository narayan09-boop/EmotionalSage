import os
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import requests
from database import DatabaseManager

class PlaylistManager:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID", "")
        self.spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET", "")
        self.spotify_access_token = None
        
        # Emotion to content theme mapping
        self.emotion_themes = {
            'joy': {
                'name': 'Joyful Vibes',
                'description': 'Uplifting content to amplify your happiness',
                'music_genres': ['pop', 'dance', 'funk', 'reggae'],
                'music_moods': ['happy', 'energetic', 'uplifting', 'party'],
                'youtube_keywords': ['feel good music', 'upbeat songs', 'happy playlist', 'celebration music'],
                'movie_genres': ['comedy', 'musical', 'family', 'animation'],
                'color_theme': '#FFD700'  # Gold
            },
            'sadness': {
                'name': 'Comfort & Healing',
                'description': 'Gentle content for emotional support and catharsis',
                'music_genres': ['indie', 'folk', 'acoustic', 'ambient'],
                'music_moods': ['sad', 'melancholy', 'emotional', 'contemplative'],
                'youtube_keywords': ['sad songs', 'emotional music', 'healing music', 'comfort playlist'],
                'movie_genres': ['drama', 'romance'],
                'color_theme': '#4682B4'  # Steel Blue
            },
            'anger': {
                'name': 'Energy & Release',
                'description': 'Intense content to channel your energy positively',
                'music_genres': ['rock', 'metal', 'punk', 'rap'],
                'music_moods': ['aggressive', 'intense', 'powerful', 'energetic'],
                'youtube_keywords': ['rock music', 'intense workouts', 'powerful music', 'energy boost'],
                'movie_genres': ['action', 'thriller'],
                'color_theme': '#DC143C'  # Crimson
            },
            'fear': {
                'name': 'Calm & Comfort',
                'description': 'Soothing content to ease anxiety and bring peace',
                'music_genres': ['ambient', 'classical', 'new age', 'meditation'],
                'music_moods': ['calm', 'peaceful', 'relaxing', 'meditative'],
                'youtube_keywords': ['relaxing music', 'meditation', 'calming sounds', 'anxiety relief'],
                'movie_genres': ['family', 'documentary'],
                'color_theme': '#98FB98'  # Pale Green
            },
            'love': {
                'name': 'Romance & Connection',
                'description': 'Romantic content celebrating love and relationships',
                'music_genres': ['r&b', 'soul', 'jazz', 'indie'],
                'music_moods': ['romantic', 'loving', 'intimate', 'passionate'],
                'youtube_keywords': ['love songs', 'romantic music', 'couples playlist', 'heartwarming'],
                'movie_genres': ['romance', 'drama'],
                'color_theme': '#FF69B4'  # Hot Pink
            },
            'calm': {
                'name': 'Zen & Tranquility',
                'description': 'Peaceful content to maintain your serene state',
                'music_genres': ['ambient', 'classical', 'world', 'instrumental'],
                'music_moods': ['peaceful', 'tranquil', 'meditative', 'zen'],
                'youtube_keywords': ['meditation music', 'nature sounds', 'peaceful videos', 'zen music'],
                'movie_genres': ['documentary', 'drama'],
                'color_theme': '#E6E6FA'  # Lavender
            },
            'stress': {
                'name': 'Stress Relief & Fun',
                'description': 'Light-hearted content to help you unwind and relax',
                'music_genres': ['acoustic', 'indie', 'lo-fi', 'chill'],
                'music_moods': ['chill', 'relaxing', 'laid-back', 'soothing'],
                'youtube_keywords': ['stress relief', 'funny videos', 'relaxation', 'chill music'],
                'movie_genres': ['comedy', 'animation'],
                'color_theme': '#87CEEB'  # Sky Blue
            },
            'surprise': {
                'name': 'Wonder & Discovery',
                'description': 'Amazing content to keep you engaged and curious',
                'music_genres': ['electronic', 'experimental', 'world', 'fusion'],
                'music_moods': ['eclectic', 'experimental', 'surprising', 'unique'],
                'youtube_keywords': ['amazing discoveries', 'mind blowing', 'incredible facts', 'surprising'],
                'movie_genres': ['sci-fi', 'fantasy', 'mystery'],
                'color_theme': '#FF8C00'  # Dark Orange
            },
            'anticipation': {
                'name': 'Adventure & Excitement',
                'description': 'Thrilling content to match your anticipatory energy',
                'music_genres': ['electronic', 'rock', 'orchestral', 'soundtrack'],
                'music_moods': ['exciting', 'adventurous', 'epic', 'uplifting'],
                'youtube_keywords': ['adventure music', 'epic soundtracks', 'exciting videos', 'travel'],
                'movie_genres': ['adventure', 'action', 'sci-fi'],
                'color_theme': '#32CD32'  # Lime Green
            },
            'disgust': {
                'name': 'Fresh & Renewal',
                'description': 'Clean, refreshing content for a fresh perspective',
                'music_genres': ['indie', 'alternative', 'electronic', 'pop'],
                'music_moods': ['fresh', 'clean', 'uplifting', 'positive'],
                'youtube_keywords': ['satisfying videos', 'cleaning videos', 'fresh start', 'renewal'],
                'movie_genres': ['comedy', 'family'],
                'color_theme': '#00CED1'  # Dark Turquoise
            }
        }
    
    def get_spotify_access_token(self):
        """Get Spotify access token using client credentials flow"""
        if not self.spotify_client_id or not self.spotify_client_secret:
            return None
            
        try:
            auth_url = "https://accounts.spotify.com/api/token"
            auth_data = {
                'grant_type': 'client_credentials',
                'client_id': self.spotify_client_id,
                'client_secret': self.spotify_client_secret
            }
            
            response = requests.post(auth_url, data=auth_data, timeout=10)
            response.raise_for_status()
            
            token_data = response.json()
            self.spotify_access_token = token_data.get('access_token')
            return self.spotify_access_token
            
        except Exception as e:
            print(f"Error getting Spotify access token: {str(e)}")
            return None
    
    def search_spotify_tracks(self, emotion: str, limit: int = 10) -> List[Dict]:
        """Search for Spotify tracks based on emotion"""
        try:
            if not self.spotify_access_token:
                self.get_spotify_access_token()
            
            if not self.spotify_access_token:
                return []
            
            theme = self.emotion_themes.get(emotion.lower(), self.emotion_themes['calm'])
            
            # Search using genre and mood
            search_queries = []
            for genre in theme['music_genres'][:2]:
                for mood in theme['music_moods'][:2]:
                    search_queries.append(f"genre:{genre} mood:{mood}")
            
            tracks = []
            
            for query in search_queries[:3]:  # Limit to 3 searches
                url = "https://api.spotify.com/v1/search"
                params = {
                    'q': query,
                    'type': 'track',
                    'limit': limit // 3,
                    'market': 'US'
                }
                
                headers = {
                    'Authorization': f'Bearer {self.spotify_access_token}'
                }
                
                response = requests.get(url, params=params, headers=headers, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                
                for track in data.get('tracks', {}).get('items', []):
                    if len(tracks) >= limit:
                        break
                        
                    formatted_track = {
                        'id': track['id'],
                        'name': track['name'],
                        'artist': ', '.join([artist['name'] for artist in track['artists']]),
                        'album': track['album']['name'],
                        'duration_ms': track['duration_ms'],
                        'preview_url': track.get('preview_url'),
                        'external_url': track['external_urls'].get('spotify'),
                        'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None,
                        'popularity': track.get('popularity', 0)
                    }
                    tracks.append(formatted_track)
                
                if len(tracks) >= limit:
                    break
            
            return tracks[:limit]
            
        except Exception as e:
            print(f"Error searching Spotify tracks: {str(e)}")
            return []
    
    def create_mood_playlist(self, emotion: str, movies: List[Dict], youtube_videos: List[Dict], 
                           spotify_tracks: List[Dict] = None) -> Dict:
        """Create a comprehensive mood-based playlist"""
        try:
            theme = self.emotion_themes.get(emotion.lower(), self.emotion_themes['calm'])
            
            # Get Spotify tracks if not provided
            if spotify_tracks is None:
                spotify_tracks = self.search_spotify_tracks(emotion, limit=8)
            if spotify_tracks is None:
                spotify_tracks = []
            
            playlist = {
                'id': f"playlist_{emotion}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'emotion': emotion,
                'theme': theme,
                'created_at': datetime.now().isoformat(),
                'content': {
                    'movies': movies[:4],  # Limit to 4 movies
                    'youtube_videos': youtube_videos[:6],  # Limit to 6 videos
                    'spotify_tracks': spotify_tracks[:8],  # Limit to 8 tracks
                },
                'stats': {
                    'total_items': len(movies[:4]) + len(youtube_videos[:6]) + len(spotify_tracks[:8]),
                    'total_duration_estimate': self._calculate_total_duration(movies[:4], youtube_videos[:6], spotify_tracks[:8])
                }
            }
            
            return playlist
            
        except Exception as e:
            print(f"Error creating mood playlist: {str(e)}")
            return {}
    
    def _calculate_total_duration(self, movies: List[Dict], youtube_videos: List[Dict], 
                                spotify_tracks: List[Dict]) -> Dict:
        """Calculate estimated total duration of playlist content"""
        try:
            # Estimate movie duration (average 2 hours per movie)
            movie_duration = len(movies) * 120  # minutes
            
            # Estimate YouTube video duration (average 8 minutes per video)
            youtube_duration = len(youtube_videos) * 8  # minutes
            
            # Calculate Spotify tracks duration
            spotify_duration = 0
            for track in spotify_tracks:
                if track.get('duration_ms'):
                    spotify_duration += track['duration_ms'] / 1000 / 60  # Convert to minutes
            
            total_minutes = movie_duration + youtube_duration + spotify_duration
            
            return {
                'movies_minutes': movie_duration,
                'youtube_minutes': youtube_duration,
                'spotify_minutes': round(spotify_duration, 1),
                'total_minutes': round(total_minutes, 1),
                'total_hours': round(total_minutes / 60, 1)
            }
            
        except Exception as e:
            print(f"Error calculating duration: {str(e)}")
            return {'total_minutes': 0, 'total_hours': 0}
    
    def save_playlist_to_db(self, session_id: str, playlist: Dict) -> Optional[int]:
        """Save playlist to database"""
        try:
            user_id = self.db.get_or_create_user(session_id)
            
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO playlists 
                        (user_id, session_id, playlist_id, emotion, theme_data, content_data, stats_data)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        user_id,
                        session_id,
                        playlist['id'],
                        playlist['emotion'],
                        json.dumps(playlist['theme']),
                        json.dumps(playlist['content']),
                        json.dumps(playlist['stats'])
                    ))
                    
                    result = cur.fetchone()
                    if result:
                        playlist_db_id = result[0]
                        conn.commit()
                        return playlist_db_id
                        
        except Exception as e:
            print(f"Error saving playlist to database: {str(e)}")
            return None
    
    def get_user_playlists(self, session_id: str, limit: int = 10) -> List[Dict]:
        """Get user's saved playlists"""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT playlist_id, emotion, theme_data, content_data, stats_data, created_at
                        FROM playlists 
                        WHERE session_id = %s 
                        ORDER BY created_at DESC 
                        LIMIT %s
                    """, (session_id, limit))
                    
                    playlists = []
                    for row in cur.fetchall():
                        playlist = {
                            'id': row[0],
                            'emotion': row[1],
                            'theme': json.loads(row[2]),
                            'content': json.loads(row[3]),
                            'stats': json.loads(row[4]),
                            'created_at': row[5]
                        }
                        playlists.append(playlist)
                    
                    return playlists
                    
        except Exception as e:
            print(f"Error getting user playlists: {str(e)}")
            return []
    
    def create_playlist_tables(self):
        """Create playlist tables in database"""
        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS playlists (
                            id SERIAL PRIMARY KEY,
                            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                            session_id VARCHAR(255) NOT NULL,
                            playlist_id VARCHAR(255) UNIQUE NOT NULL,
                            emotion VARCHAR(50) NOT NULL,
                            theme_data JSON NOT NULL,
                            content_data JSON NOT NULL,
                            stats_data JSON NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    conn.commit()
                    print("Playlist tables created successfully")
                    
        except Exception as e:
            print(f"Error creating playlist tables: {str(e)}")
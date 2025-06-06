import os
import requests
import json
from typing import List, Dict, Optional

class MovieRecommender:
    def __init__(self):
        self.api_key = os.getenv("TMDB_API_KEY", "")
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p/w500"
        
        # Emotion to genre mapping
        self.emotion_genre_map = {
            'joy': [35, 10402, 10751, 16],  # Comedy, Music, Family, Animation
            'sadness': [18, 10749],  # Drama, Romance
            'anger': [28, 53, 80],  # Action, Thriller, Crime
            'fear': [27, 53, 9648],  # Horror, Thriller, Mystery
            'surprise': [878, 14, 12],  # Sci-Fi, Fantasy, Adventure
            'disgust': [27, 53],  # Horror, Thriller
            'love': [10749, 18, 35],  # Romance, Drama, Comedy
            'anticipation': [12, 878, 28],  # Adventure, Sci-Fi, Action
            'calm': [99, 18, 10402],  # Documentary, Drama, Music
            'stress': [35, 10751, 16]  # Comedy, Family, Animation (stress relief)
        }
        
        # Genre ID to name mapping
        self.genre_names = {
            28: "Action", 35: "Comedy", 80: "Crime", 99: "Documentary", 18: "Drama",
            10751: "Family", 14: "Fantasy", 36: "History", 27: "Horror", 10402: "Music",
            9648: "Mystery", 10749: "Romance", 878: "Science Fiction", 10770: "TV Movie",
            53: "Thriller", 10752: "War", 37: "Western", 12: "Adventure", 16: "Animation"
        }
    
    def get_recommendations(self, emotion: str, limit: int = 6) -> List[Dict]:
        """
        Get movie recommendations based on emotion
        """
        try:
            if not self.api_key:
                print("TMDB API key not found")
                return []
            
            # Get genre IDs for the emotion
            genre_ids = self.emotion_genre_map.get(emotion.lower(), [35])  # Default to comedy
            
            movies = []
            
            # Try to get movies for each relevant genre
            for genre_id in genre_ids[:2]:  # Limit to top 2 genres
                genre_movies = self._get_movies_by_genre(genre_id, limit=3)
                movies.extend(genre_movies)
                
                if len(movies) >= limit:
                    break
            
            # Remove duplicates and limit results
            seen_ids = set()
            unique_movies = []
            for movie in movies:
                if movie['id'] not in seen_ids:
                    seen_ids.add(movie['id'])
                    unique_movies.append(movie)
                    if len(unique_movies) >= limit:
                        break
            
            return unique_movies
            
        except Exception as e:
            print(f"Error getting movie recommendations: {str(e)}")
            return []
    
    def _get_movies_by_genre(self, genre_id: int, limit: int = 10) -> List[Dict]:
        """
        Get movies by genre ID
        """
        try:
            url = f"{self.base_url}/discover/movie"
            params = {
                'api_key': self.api_key,
                'with_genres': genre_id,
                'sort_by': 'popularity.desc',
                'vote_average.gte': 6.0,  # Minimum rating
                'vote_count.gte': 100,  # Minimum vote count
                'page': 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            movies = []
            
            for movie_data in data.get('results', [])[:limit]:
                movie = self._format_movie_data(movie_data)
                if movie:
                    movies.append(movie)
            
            return movies
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching movies for genre {genre_id}: {str(e)}")
            return []
        except Exception as e:
            print(f"Unexpected error in _get_movies_by_genre: {str(e)}")
            return []
    
    def _format_movie_data(self, movie_data: Dict) -> Optional[Dict]:
        """
        Format movie data from TMDB API response
        """
        try:
            # Get genre names
            genre_ids = movie_data.get('genre_ids', [])
            genres = [self.genre_names.get(gid, '') for gid in genre_ids if gid in self.genre_names]
            
            # Format release year
            release_date = movie_data.get('release_date', '')
            year = release_date.split('-')[0] if release_date else 'N/A'
            
            # Format poster URL
            poster_path = movie_data.get('poster_path')
            poster_url = f"{self.image_base_url}{poster_path}" if poster_path else None
            
            return {
                'id': movie_data.get('id'),
                'title': movie_data.get('title', 'Unknown Title'),
                'overview': movie_data.get('overview', 'No description available.'),
                'rating': round(movie_data.get('vote_average', 0), 1),
                'year': year,
                'genres': genres,
                'poster_url': poster_url,
                'tmdb_url': f"https://www.themoviedb.org/movie/{movie_data.get('id')}"
            }
            
        except Exception as e:
            print(f"Error formatting movie data: {str(e)}")
            return None
    
    def search_movies_by_keyword(self, keyword: str, limit: int = 5) -> List[Dict]:
        """
        Search movies by keyword (fallback method)
        """
        try:
            if not self.api_key:
                return []
            
            url = f"{self.base_url}/search/movie"
            params = {
                'api_key': self.api_key,
                'query': keyword,
                'page': 1
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            movies = []
            
            for movie_data in data.get('results', [])[:limit]:
                movie = self._format_movie_data(movie_data)
                if movie and movie['rating'] >= 6.0:  # Filter by rating
                    movies.append(movie)
            
            return movies
            
        except Exception as e:
            print(f"Error searching movies by keyword: {str(e)}")
            return []

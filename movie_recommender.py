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
                # Return curated static recommendations when API is not available
                return self._get_curated_recommendations(emotion, limit)
            
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
    
    def _get_curated_recommendations(self, emotion: str, limit: int = 6) -> List[Dict]:
        """
        Get curated movie recommendations when API is not available
        """
        curated_movies = {
            'joy': [
                {'id': 1, 'title': 'The Grand Budapest Hotel', 'overview': 'A whimsical comedy about the adventures of a legendary concierge and his protégé at a famous European hotel.', 'rating': 8.1, 'year': '2014', 'genres': ['Comedy', 'Drama'], 'poster_url': None, 'tmdb_url': '#'},
                {'id': 2, 'title': 'Paddington', 'overview': 'A young Peruvian bear travels to London in search of a home, finding himself caught up in a series of misadventures.', 'rating': 8.0, 'year': '2014', 'genres': ['Family', 'Comedy'], 'poster_url': None, 'tmdb_url': '#'},
                {'id': 3, 'title': 'La La Land', 'overview': 'A jazz musician and an aspiring actress meet and fall in love in Los Angeles while pursuing their dreams.', 'rating': 8.0, 'year': '2016', 'genres': ['Musical', 'Romance'], 'poster_url': None, 'tmdb_url': '#'},
            ],
            'sadness': [
                {'id': 4, 'title': 'Inside Out', 'overview': 'After moving to a new city, young Riley struggles with her emotions as they try to guide her through this difficult life change.', 'rating': 8.1, 'year': '2015', 'genres': ['Animation', 'Drama'], 'poster_url': None, 'tmdb_url': '#'},
                {'id': 5, 'title': 'Her', 'overview': 'A lonely writer develops an unlikely relationship with an operating system designed to meet his every need.', 'rating': 8.0, 'year': '2013', 'genres': ['Drama', 'Romance'], 'poster_url': None, 'tmdb_url': '#'},
                {'id': 6, 'title': 'Manchester by the Sea', 'overview': 'A depressed uncle is asked to take care of his teenage nephew after the boy\'s father dies.', 'rating': 7.8, 'year': '2016', 'genres': ['Drama'], 'poster_url': None, 'tmdb_url': '#'},
            ],
            'anger': [
                {'id': 7, 'title': 'Mad Max: Fury Road', 'overview': 'In a post-apocalyptic wasteland, Max teams up with a mysterious woman to flee from a warlord and his army.', 'rating': 8.1, 'year': '2015', 'genres': ['Action', 'Adventure'], 'poster_url': None, 'tmdb_url': '#'},
                {'id': 8, 'title': 'John Wick', 'overview': 'An ex-hitman comes out of retirement to track down the gangsters that took everything from him.', 'rating': 7.4, 'year': '2014', 'genres': ['Action', 'Thriller'], 'poster_url': None, 'tmdb_url': '#'},
                {'id': 9, 'title': 'The Raid', 'overview': 'A SWAT team becomes trapped in a tenement run by a ruthless mobster and his army of killers and thugs.', 'rating': 7.6, 'year': '2011', 'genres': ['Action', 'Thriller'], 'poster_url': None, 'tmdb_url': '#'},
            ],
            'fear': [
                {'id': 10, 'title': 'A Quiet Place', 'overview': 'A family lives in silence to avoid detection by alien creatures that hunt by sound.', 'rating': 7.5, 'year': '2018', 'genres': ['Horror', 'Thriller'], 'poster_url': None, 'tmdb_url': '#'},
                {'id': 11, 'title': 'Get Out', 'overview': 'A young African-American visits his white girlfriend\'s parents for the weekend, where his simmering uneasiness becomes a nightmare.', 'rating': 7.7, 'year': '2017', 'genres': ['Horror', 'Mystery'], 'poster_url': None, 'tmdb_url': '#'},
                {'id': 12, 'title': 'Hereditary', 'overview': 'A grieving family is haunted by tragedy and disturbing secrets.', 'rating': 7.3, 'year': '2018', 'genres': ['Horror', 'Mystery'], 'poster_url': None, 'tmdb_url': '#'},
            ],
            'love': [
                {'id': 13, 'title': 'The Princess Bride', 'overview': 'A bedridden boy\'s grandfather reads him the story of a farmboy-turned-pirate who encounters numerous obstacles and enemies in his quest to be reunited with his true love.', 'rating': 8.0, 'year': '1987', 'genres': ['Adventure', 'Romance'], 'poster_url': None, 'tmdb_url': '#'},
                {'id': 14, 'title': 'Before Sunset', 'overview': 'Nine years after their first encounter, Jesse and Celine meet again during Jesse\'s book tour in Paris.', 'rating': 8.1, 'year': '2004', 'genres': ['Drama', 'Romance'], 'poster_url': None, 'tmdb_url': '#'},
                {'id': 15, 'title': 'Eternal Sunshine of the Spotless Mind', 'overview': 'When their relationship turns sour, a couple undergoes a medical procedure to have each other erased from their memories.', 'rating': 8.3, 'year': '2004', 'genres': ['Drama', 'Romance'], 'poster_url': None, 'tmdb_url': '#'},
            ],
            'calm': [
                {'id': 16, 'title': 'My Neighbor Totoro', 'overview': 'When two girls move to the country to be near their ailing mother, they have adventures with the wondrous forest spirits who live nearby.', 'rating': 8.2, 'year': '1988', 'genres': ['Animation', 'Family'], 'poster_url': None, 'tmdb_url': '#'},
                {'id': 17, 'title': 'Lost in Translation', 'overview': 'A faded movie star and a neglected young woman form an unlikely bond after crossing paths in Tokyo.', 'rating': 7.7, 'year': '2003', 'genres': ['Drama'], 'poster_url': None, 'tmdb_url': '#'},
                {'id': 18, 'title': 'The Tree of Life', 'overview': 'The story of a family in 1950s Texas, told through the eyes of the eldest son, with glimpses of his adult life.', 'rating': 6.8, 'year': '2011', 'genres': ['Drama'], 'poster_url': None, 'tmdb_url': '#'},
            ],
            'stress': [
                {'id': 19, 'title': 'Spirited Away', 'overview': 'During her family\'s move to the suburbs, a sullen 10-year-old girl wanders into a world ruled by gods and witches.', 'rating': 9.3, 'year': '2001', 'genres': ['Animation', 'Adventure'], 'poster_url': None, 'tmdb_url': '#'},
                {'id': 20, 'title': 'Kiki\'s Delivery Service', 'overview': 'A young witch, on her mandatory year of independent life, finds fitting into a new community difficult.', 'rating': 7.9, 'year': '1989', 'genres': ['Animation', 'Family'], 'poster_url': None, 'tmdb_url': '#'},
                {'id': 21, 'title': 'The Grand Budapest Hotel', 'overview': 'A whimsical comedy about the adventures of a legendary concierge and his protégé at a famous European hotel.', 'rating': 8.1, 'year': '2014', 'genres': ['Comedy', 'Drama'], 'poster_url': None, 'tmdb_url': '#'},
            ]
        }
        
        # Get movies for the emotion, fallback to joy if emotion not found
        emotion_movies = curated_movies.get(emotion.lower(), curated_movies['joy'])
        return emotion_movies[:limit]

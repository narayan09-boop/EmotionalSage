import os
import requests
from typing import List, Dict
from datetime import datetime, timedelta

class YouTubeRecommender:
    def __init__(self):
        self.api_key = os.getenv("YOUTUBE_API_KEY", "")
        self.base_url = "https://www.googleapis.com/youtube/v3"
        
        # Emotion to search query mapping
        self.emotion_queries = {
            'joy': ['feel good music', 'happy songs', 'uplifting videos', 'comedy sketches', 'funny moments'],
            'sadness': ['sad songs', 'emotional music', 'comfort videos', 'healing music', 'therapeutic content'],
            'anger': ['rock music', 'intense workouts', 'motivational speeches', 'rage room', 'metal music'],
            'fear': ['relaxing music', 'meditation', 'calming sounds', 'anxiety relief', 'peaceful nature'],
            'surprise': ['amazing facts', 'mind blowing', 'incredible moments', 'wow videos', 'surprising discoveries'],
            'disgust': ['satisfying videos', 'cleaning videos', 'organizing', 'fresh content', 'renewal videos'],
            'love': ['romantic songs', 'love songs', 'relationship advice', 'heartwarming stories', 'couples content'],
            'anticipation': ['upcoming releases', 'exciting news', 'adventure videos', 'travel vlogs', 'new discoveries'],
            'calm': ['meditation music', 'nature sounds', 'peaceful videos', 'relaxing content', 'zen music'],
            'stress': ['stress relief', 'relaxation techniques', 'comedy videos', 'funny animals', 'meditation']
        }
    
    def get_recommendations(self, emotion: str, limit: int = 8) -> List[Dict]:
        """
        Get YouTube video recommendations based on emotion
        """
        try:
            if not self.api_key:
                print("YouTube API key not found")
                return []
            
            # Get search queries for the emotion
            queries = self.emotion_queries.get(emotion.lower(), ['relaxing music'])
            
            videos = []
            
            # Search for videos using different queries
            for query in queries[:3]:  # Use top 3 queries
                query_videos = self._search_videos(query, limit=3)
                videos.extend(query_videos)
                
                if len(videos) >= limit:
                    break
            
            # Remove duplicates and limit results
            seen_ids = set()
            unique_videos = []
            for video in videos:
                if video['id'] not in seen_ids:
                    seen_ids.add(video['id'])
                    unique_videos.append(video)
                    if len(unique_videos) >= limit:
                        break
            
            return unique_videos
            
        except Exception as e:
            print(f"Error getting YouTube recommendations: {str(e)}")
            return []
    
    def _search_videos(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search for videos using YouTube API
        """
        try:
            url = f"{self.base_url}/search"
            params = {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'key': self.api_key,
                'maxResults': limit,
                'order': 'relevance',
                'safeSearch': 'moderate',
                'videoEmbeddable': 'true',
                'videoSyndicated': 'true',
                'publishedAfter': (datetime.now() - timedelta(days=365)).isoformat() + 'Z'  # Last year
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            videos = []
            
            for item in data.get('items', []):
                video = self._format_video_data(item)
                if video:
                    videos.append(video)
            
            return videos
            
        except requests.exceptions.RequestException as e:
            print(f"Error searching YouTube videos: {str(e)}")
            return []
        except Exception as e:
            print(f"Unexpected error in _search_videos: {str(e)}")
            return []
    
    def _format_video_data(self, video_data: Dict) -> Dict:
        """
        Format video data from YouTube API response
        """
        try:
            snippet = video_data.get('snippet', {})
            video_id = video_data.get('id', {}).get('videoId', '')
            
            # Format published date
            published_at = snippet.get('publishedAt', '')
            try:
                pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                formatted_date = pub_date.strftime('%B %d, %Y')
            except:
                formatted_date = 'Unknown Date'
            
            # Get thumbnail URL
            thumbnails = snippet.get('thumbnails', {})
            thumbnail_url = None
            for quality in ['medium', 'default', 'high']:
                if quality in thumbnails:
                    thumbnail_url = thumbnails[quality].get('url')
                    break
            
            return {
                'id': video_id,
                'title': snippet.get('title', 'Unknown Title'),
                'description': snippet.get('description', 'No description available.'),
                'channel_title': snippet.get('channelTitle', 'Unknown Channel'),
                'published_at': formatted_date,
                'thumbnail_url': thumbnail_url,
                'url': f"https://www.youtube.com/watch?v={video_id}"
            }
            
        except Exception as e:
            print(f"Error formatting video data: {str(e)}")
            return {}
    
    def get_trending_videos(self, category_id: str = '0', limit: int = 10) -> List[Dict]:
        """
        Get trending videos (fallback method)
        """
        try:
            if not self.api_key:
                return []
            
            url = f"{self.base_url}/videos"
            params = {
                'part': 'snippet,statistics',
                'chart': 'mostPopular',
                'regionCode': 'US',
                'maxResults': limit,
                'key': self.api_key,
                'categoryId': category_id
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            videos = []
            
            for item in data.get('items', []):
                # Reformat for trending videos
                formatted_item = {
                    'id': {'videoId': item.get('id')},
                    'snippet': item.get('snippet', {})
                }
                video = self._format_video_data(formatted_item)
                if video:
                    videos.append(video)
            
            return videos
            
        except Exception as e:
            print(f"Error getting trending videos: {str(e)}")
            return []

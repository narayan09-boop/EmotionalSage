from typing import Dict, List, Optional
from movie_recommender import MovieRecommender
from youtube_recommender import YouTubeRecommender


class RecommendationEngine:

    def __init__(self):
        self.movie_recommender = MovieRecommender()
        self.youtube_recommender = YouTubeRecommender()

    def get_recommendations(self, emotion_result: Dict) -> Optional[Dict]:
        """
        Get comprehensive recommendations based on emotion analysis
        """
        try:
            primary_emotion = emotion_result.get('primary_emotion', 'calm')
            confidence = emotion_result.get('confidence', 0.5)
            secondary_emotions = emotion_result.get('secondary_emotions', [])

            recommendations = {
                'movies': [],
                'youtube_videos': [],
                'reasoning':
                self._generate_reasoning(primary_emotion, confidence,
                                         secondary_emotions)
            }

            # Get movie recommendations
            try:
                movies = self.movie_recommender.get_recommendations(
                    primary_emotion, limit=6)
                if movies:
                    recommendations['movies'] = movies
                else:
                    # Fallback: try secondary emotions
                    for emotion in secondary_emotions:
                        movies = self.movie_recommender.get_recommendations(
                            emotion, limit=3)
                        if movies:
                            recommendations['movies'].extend(movies)
                            break
            except Exception as e:
                print(f"Error getting movie recommendations: {str(e)}")

            # Get YouTube recommendations
            try:
                youtube_videos = self.youtube_recommender.get_recommendations(
                    primary_emotion, limit=8)
                if youtube_videos:
                    recommendations['youtube_videos'] = youtube_videos
                else:
                    # Fallback: try secondary emotions
                    for emotion in secondary_emotions:
                        youtube_videos = self.youtube_recommender.get_recommendations(
                            emotion, limit=4)
                        if youtube_videos:
                            recommendations['youtube_videos'].extend(
                                youtube_videos)
                            break
            except Exception as e:
                print(f"Error getting YouTube recommendations: {str(e)}")

            # If we still don't have any recommendations, try fallback methods
            if not recommendations['movies'] and not recommendations[
                    'youtube_videos']:
                recommendations = self._get_fallback_recommendations(
                    primary_emotion)

            return recommendations if (
                recommendations['movies']
                or recommendations['youtube_videos']) else None

        except Exception as e:
            print(f"Error in recommendation engine: {str(e)}")
            return None

    def _generate_reasoning(self, primary_emotion: str, confidence: float,
                            secondary_emotions: List[str]) -> str:
        """
        Generate explanation for why these recommendations were chosen
        """
        reasoning_templates = {
            'joy':
            "Since you're feeling joyful, we've selected uplifting content that will amplify your positive mood with comedies, feel-good stories, and energetic content.",
            'sadness':
            "We understand you're going through a tough time. Here's some content that can provide comfort, emotional catharsis, or gentle distraction.",
            'anger':
            "When feeling angry, sometimes you need an outlet. We've chosen intense action content and motivational material to help channel that energy positively.",
            'fear':
            "To help ease your anxiety, we've selected calming and reassuring content that can provide comfort and relaxation.",
            'surprise':
            "Since you're in a surprised state of mind, here's some amazing and mind-blowing content that will keep you engaged and wondering.",
            'disgust':
            "We've chosen refreshing and satisfying content to help cleanse your palate and shift your focus to more positive experiences.",
            'love':
            "Feeling the love! Here's romantic and heartwarming content that celebrates human connection and beautiful relationships.",
            'anticipation':
            "Your excitement is contagious! We've selected thrilling and adventure-filled content to match your anticipatory energy.",
            'calm':
            "Perfect time for some peaceful content. We've chosen relaxing and meditative material to maintain your zen state.",
            'stress':
            "Let's help you unwind. Here's some stress-relieving content including comedy and relaxation material to help you decompress."
        }

        base_reasoning = reasoning_templates.get(
            primary_emotion,
            "Based on your current emotional state, we've curated content that should resonate with how you're feeling."
        )

        if confidence > 0.8:
            confidence_note = " We're highly confident in this emotion detection."
        elif confidence > 0.6:
            confidence_note = " We're moderately confident in this assessment."
        else:
            confidence_note = " We've made our best guess based on your input."

        secondary_note = ""
        if secondary_emotions:
            secondary_note = f" We also detected hints of {', '.join(secondary_emotions)}, so some recommendations may reflect these mixed feelings."

        return base_reasoning + confidence_note + secondary_note

    def _get_fallback_recommendations(self, emotion: str) -> Dict:
        """
        Get fallback recommendations when primary methods fail
        """
        try:
            # Simple keyword-based fallback
            fallback_keywords = {
                'joy': 'comedy',
                'sadness': 'drama',
                'anger': 'action',
                'fear': 'meditation',
                'surprise': 'amazing',
                'disgust': 'satisfying',
                'love': 'romance',
                'anticipation': 'adventure',
                'calm': 'relaxing',
                'stress': 'funny'
            }

            keyword = fallback_keywords.get(emotion, 'entertainment')

            # Try movie search by keyword
            movies = []
            try:
                movies = self.movie_recommender.search_movies_by_keyword(
                    keyword, limit=3)
            except:
                pass

            # Try YouTube trending as last resort
            youtube_videos = []
            try:
                youtube_videos = self.youtube_recommender.get_trending_videos(
                    limit=5)
            except:
                pass

            return {
                'movies':
                movies,
                'youtube_videos':
                youtube_videos,
                'reasoning':
                f"We used fallback recommendations based on {emotion} emotion. Results may be more general but should still be relevant."
            }

        except Exception as e:
            print(f"Error in fallback recommendations: {str(e)}")
            return {
                'movies': [],
                'youtube_videos': [],
                'reasoning': 'Unable to generate recommendations at this time.'
            }

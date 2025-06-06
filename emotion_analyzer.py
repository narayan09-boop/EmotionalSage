import os
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re

class EmotionAnalyzer:
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer()
        self.emotion_keywords = {
            'joy': ['happy', 'excited', 'thrilled', 'joyful', 'elated', 'cheerful', 'delighted', 'euphoric', 'upbeat', 'optimistic'],
            'sadness': ['sad', 'depressed', 'down', 'melancholy', 'grief', 'sorrow', 'heartbroken', 'dejected', 'gloomy', 'blue'],
            'anger': ['angry', 'furious', 'irritated', 'mad', 'rage', 'frustrated', 'annoyed', 'outraged', 'livid', 'hostile'],
            'fear': ['scared', 'afraid', 'terrified', 'anxious', 'worried', 'nervous', 'panic', 'frightened', 'apprehensive', 'uneasy'],
            'surprise': ['surprised', 'shocked', 'amazed', 'astonished', 'stunned', 'bewildered', 'startled', 'astounded'],
            'disgust': ['disgusted', 'revolted', 'repulsed', 'sickened', 'nauseated', 'appalled', 'horrified'],
            'love': ['love', 'adore', 'cherish', 'romantic', 'affectionate', 'tender', 'passionate', 'devoted', 'infatuated'],
            'anticipation': ['excited', 'eager', 'looking forward', 'anticipating', 'hopeful', 'expectant', 'enthusiastic'],
            'calm': ['calm', 'peaceful', 'relaxed', 'serene', 'tranquil', 'content', 'balanced', 'centered', 'zen'],
            'stress': ['stressed', 'overwhelmed', 'pressure', 'burden', 'exhausted', 'burned out', 'tense', 'strained']
        }
    
    def analyze_emotion(self, text):
        """
        Analyze the emotion in the given text using multiple approaches
        """
        try:
            if not text or not text.strip():
                return None
            
            # Clean and normalize text
            clean_text = self._clean_text(text)
            
            # Get sentiment scores from VADER
            vader_scores = self.vader_analyzer.polarity_scores(clean_text)
            
            # Get TextBlob sentiment
            blob = TextBlob(clean_text)
            textblob_polarity = blob.sentiment.polarity
            textblob_subjectivity = blob.sentiment.subjectivity
            
            # Keyword-based emotion detection
            keyword_emotions = self._detect_keyword_emotions(clean_text)
            
            # Combine approaches to determine primary emotion
            primary_emotion = self._determine_primary_emotion(
                vader_scores, textblob_polarity, keyword_emotions
            )
            
            # Calculate confidence
            confidence = self._calculate_confidence(
                vader_scores, textblob_subjectivity, keyword_emotions
            )
            
            # Get secondary emotions
            secondary_emotions = self._get_secondary_emotions(keyword_emotions, primary_emotion)
            
            return {
                'primary_emotion': primary_emotion,
                'confidence': confidence,
                'secondary_emotions': secondary_emotions,
                'sentiment_scores': {
                    'compound': vader_scores['compound'],
                    'positive': vader_scores['pos'],
                    'negative': vader_scores['neg'],
                    'neutral': vader_scores['neu']
                },
                'textblob_polarity': textblob_polarity,
                'textblob_subjectivity': textblob_subjectivity
            }
            
        except Exception as e:
            print(f"Error in emotion analysis: {str(e)}")
            return None
    
    def _clean_text(self, text):
        """Clean and normalize the input text"""
        # Convert to lowercase
        text = text.lower()
        # Remove extra whitespaces
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        return text.strip()
    
    def _detect_keyword_emotions(self, text):
        """Detect emotions based on keyword matching"""
        emotion_scores = {}
        
        for emotion, keywords in self.emotion_keywords.items():
            score = 0
            for keyword in keywords:
                # Count occurrences of keywords
                count = len(re.findall(r'\b' + re.escape(keyword) + r'\b', text))
                score += count
            
            if score > 0:
                emotion_scores[emotion] = score
        
        return emotion_scores
    
    def _determine_primary_emotion(self, vader_scores, textblob_polarity, keyword_emotions):
        """Determine the primary emotion from all analysis methods"""
        
        # If we have strong keyword matches, prioritize them
        if keyword_emotions:
            max_keyword_emotion = max(keyword_emotions.items(), key=lambda x: x[1])
            if max_keyword_emotion[1] >= 2:  # Strong keyword presence
                return max_keyword_emotion[0]
        
        # Use sentiment analysis for basic emotion mapping
        compound_score = vader_scores['compound']
        
        # Strong positive sentiment
        if compound_score >= 0.5:
            if keyword_emotions:
                positive_emotions = ['joy', 'love', 'anticipation', 'surprise']
                for emotion in positive_emotions:
                    if emotion in keyword_emotions:
                        return emotion
            return 'joy'
        
        # Strong negative sentiment
        elif compound_score <= -0.5:
            if keyword_emotions:
                negative_emotions = ['sadness', 'anger', 'fear', 'disgust']
                for emotion in negative_emotions:
                    if emotion in keyword_emotions:
                        return emotion
            # Determine specific negative emotion based on additional analysis
            if vader_scores['neg'] > 0.3:
                return 'sadness' if textblob_polarity < -0.3 else 'anger'
            return 'sadness'
        
        # Neutral sentiment
        else:
            if keyword_emotions:
                return max(keyword_emotions.items(), key=lambda x: x[1])[0]
            
            # Check for stress or calm indicators
            if 'stress' in keyword_emotions or any(word in ['stress', 'overwhelm', 'pressure'] for word in keyword_emotions):
                return 'stress'
            elif any(word in ['calm', 'peace', 'relax'] for word in keyword_emotions):
                return 'calm'
            
            return 'calm'  # Default neutral emotion
    
    def _calculate_confidence(self, vader_scores, textblob_subjectivity, keyword_emotions):
        """Calculate confidence score for the emotion detection"""
        confidence_factors = []
        
        # VADER compound score strength
        compound_strength = abs(vader_scores['compound'])
        confidence_factors.append(min(compound_strength * 2, 1.0))
        
        # TextBlob subjectivity (higher subjectivity = more emotional content)
        confidence_factors.append(textblob_subjectivity)
        
        # Keyword presence
        if keyword_emotions:
            max_keyword_score = max(keyword_emotions.values())
            keyword_confidence = min(max_keyword_score / 5.0, 1.0)  # Normalize to 0-1
            confidence_factors.append(keyword_confidence)
        else:
            confidence_factors.append(0.3)  # Lower confidence without keywords
        
        # Average confidence
        avg_confidence = sum(confidence_factors) / len(confidence_factors)
        
        # Ensure minimum confidence
        return max(avg_confidence, 0.4)
    
    def _get_secondary_emotions(self, keyword_emotions, primary_emotion):
        """Get secondary emotions that were detected"""
        secondary = []
        
        for emotion, score in keyword_emotions.items():
            if emotion != primary_emotion and score > 0:
                secondary.append(emotion)
        
        # Return top 2 secondary emotions
        return sorted(secondary, key=lambda x: keyword_emotions[x], reverse=True)[:2]

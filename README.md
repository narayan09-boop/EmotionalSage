# Emotion-Aware Content Recommender

A web-based emotion detection and recommendation system that analyzes your feelings through text input and suggests relevant movies and YouTube videos based on your current emotional state.

## Features

- **Emotion Detection**: Uses TextBlob and VADER sentiment analysis to detect emotions like joy, sadness, anger, fear, love, calm, stress, and more
- **Movie Recommendations**: Curated movie suggestions based on detected emotions (expandable with TMDB API)
- **YouTube Integration**: Real-time video recommendations using YouTube Data API v3
- **Persistent Storage**: PostgreSQL database stores emotion history and analytics
- **Emotion Analytics**: Track your emotional patterns over time with statistics and insights
- **Session Management**: Unique session tracking for personalized experiences

## Installation

### Prerequisites
- Python 3.11+
- PostgreSQL database
- YouTube Data API v3 key
- TMDB API key (optional, app includes curated movies as fallback)

### Setup

1. **Install Dependencies**
```bash
pip install streamlit pandas psycopg2-binary textblob vadersentiment requests
```

2. **Environment Variables**
Set the following environment variables:
```bash
# Required
DATABASE_URL=postgresql://username:password@host:port/database
YOUTUBE_API_KEY=your_youtube_api_key

# Optional (app includes curated movies as fallback)
TMDB_API_KEY=your_tmdb_api_key
```

3. **Database Setup**
The app automatically creates the required PostgreSQL tables:
- `users` - User session management
- `emotion_history` - Emotion analysis records
- `recommendations` - Saved content recommendations
- `user_preferences` - User preference tracking

4. **Run the Application**
```bash
streamlit run app.py --server.port 5000
```

## API Keys Setup

### YouTube Data API v3
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable YouTube Data API v3
4. Create credentials (API key)
5. Add the key to your environment as `YOUTUBE_API_KEY`

### TMDB API (Optional)
1. Visit [The Movie Database](https://www.themoviedb.org/)
2. Create an account and go to Settings > API
3. Request an API key
4. Add the key to your environment as `TMDB_API_KEY`

## File Structure

```
emotion-recommender-app/
├── app.py                    # Main Streamlit application
├── emotion_analyzer.py       # Emotion detection logic
├── movie_recommender.py      # Movie recommendation engine
├── youtube_recommender.py    # YouTube video recommendations
├── recommendation_engine.py  # Combined recommendation logic
├── database.py              # PostgreSQL database manager
├── .streamlit/
│   └── config.toml          # Streamlit configuration
├── pyproject.toml           # Python dependencies
└── README.md               # This file
```

## Usage

1. **Enter Your Feelings**: Describe how you're feeling in the text area
2. **Get Analysis**: Click "Get Recommendations" to analyze your emotion
3. **View Results**: See detected emotions with confidence levels
4. **Browse Content**: Explore movie and video recommendations
5. **Track History**: Review your emotion patterns in the history section

## Emotion Categories

The system detects these primary emotions:
- **Joy**: Happy, excited, thrilled, optimistic
- **Sadness**: Sad, depressed, melancholy, grief
- **Anger**: Angry, frustrated, irritated, rage
- **Fear**: Scared, anxious, worried, nervous
- **Love**: Romantic, affectionate, tender, devoted
- **Calm**: Peaceful, relaxed, serene, tranquil
- **Stress**: Overwhelmed, pressured, exhausted, tense
- **Surprise**: Shocked, amazed, astonished, stunned
- **Anticipation**: Excited, eager, hopeful, expectant
- **Disgust**: Revolted, appalled, disgusted

## Technical Details

### Emotion Analysis
- **VADER Sentiment**: Compound sentiment scoring
- **TextBlob**: Polarity and subjectivity analysis
- **Keyword Matching**: Emotion-specific keyword detection
- **Confidence Scoring**: Multi-factor confidence calculation

### Content Matching
- **Movies**: Genre-based recommendations using emotion-to-genre mapping
- **YouTube**: Query-based search using emotion-specific search terms
- **Fallback System**: Curated recommendations when APIs are unavailable

### Database Schema
- Normalized PostgreSQL schema with foreign key relationships
- JSON storage for complex data structures
- Automatic timestamp tracking
- Session-based user management

## Customization

### Adding New Emotions
Edit `emotion_keywords` in `emotion_analyzer.py`:
```python
self.emotion_keywords = {
    'new_emotion': ['keyword1', 'keyword2', 'keyword3']
}
```

### Movie Genre Mapping
Modify `emotion_genre_map` in `movie_recommender.py`:
```python
self.emotion_genre_map = {
    'emotion': [genre_id1, genre_id2]
}
```

### YouTube Queries
Update `emotion_queries` in `youtube_recommender.py`:
```python
self.emotion_queries = {
    'emotion': ['search term 1', 'search term 2']
}
```

## Troubleshooting

### Database Connection Issues
- Verify DATABASE_URL format: `postgresql://user:password@host:port/database`
- Ensure PostgreSQL is running and accessible
- Check database permissions

### API Issues
- Verify API keys are correctly set in environment
- Check API quotas and rate limits
- Ensure APIs are enabled in respective consoles

### Performance
- Database queries are optimized with indexes
- API calls include timeouts and error handling
- Session state management minimizes redundant operations

## License

Open source - feel free to modify and distribute.

## Support

For issues or questions, check the console logs for detailed error messages. The app includes comprehensive error handling and logging.
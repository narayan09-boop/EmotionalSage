import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
from emotion_analyzer import EmotionAnalyzer
from recommendation_engine import RecommendationEngine
from database import DatabaseManager

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Initialize database
if 'db' not in st.session_state:
    st.session_state.db = DatabaseManager()

def main():
    st.title("🎭 Emotion-Aware Content Recommender")
    st.markdown("Tell us how you're feeling, and we'll suggest movies and videos that match your mood!")
    
    # Initialize components
    emotion_analyzer = EmotionAnalyzer()
    recommendation_engine = RecommendationEngine()
    
    # Text input section
    st.header("📝 How are you feeling today?")
    user_text = st.text_area(
        "Describe your current mood, what happened today, or how you're feeling:",
        placeholder="I'm feeling really excited about the weekend coming up, but also a bit stressed about work...",
        height=100
    )
    
    if st.button("🎯 Get Recommendations", type="primary"):
        if user_text.strip():
            with st.spinner("Analyzing your emotions..."):
                # Analyze emotion
                emotion_result = emotion_analyzer.analyze_emotion(user_text)
                
                if emotion_result:
                    # Save to database
                    emotion_history_id = st.session_state.db.save_emotion_analysis(
                        st.session_state.session_id, user_text, emotion_result
                    )
                    
                    # Display emotion analysis
                    st.success(f"**Detected Emotion:** {emotion_result['primary_emotion'].title()} "
                             f"(Confidence: {emotion_result['confidence']:.1%})")
                    
                    if emotion_result.get('secondary_emotions'):
                        st.info(f"**Secondary emotions detected:** {', '.join(emotion_result['secondary_emotions'])}")
                    
                    # Get recommendations
                    with st.spinner("Finding perfect content for your mood..."):
                        recommendations = recommendation_engine.get_recommendations(emotion_result)
                        
                        if recommendations:
                            # Save recommendations to database
                            if emotion_history_id:
                                st.session_state.db.save_recommendations(emotion_history_id, recommendations)
                            display_recommendations(recommendations, emotion_result)
                        else:
                            st.error("Sorry, we couldn't find recommendations right now. Please try again later.")
                else:
                    st.error("Unable to analyze emotion. Please try rephrasing your text.")
        else:
            st.warning("Please enter some text describing how you're feeling.")
    
    # Display emotion history
    display_emotion_history()

def display_recommendations(recommendations, emotion_result):
    st.header("🎬 Recommended Content")
    
    # Explanation
    st.markdown(f"**Why these recommendations?** Based on your {emotion_result['primary_emotion']} mood, "
               f"we've selected content that typically resonates with people feeling similar emotions.")
    
    # Movies section
    if recommendations.get('movies'):
        st.subheader("🍿 Movies")
        movie_cols = st.columns(min(3, len(recommendations['movies'])))
        
        for idx, movie in enumerate(recommendations['movies'][:3]):
            with movie_cols[idx % 3]:
                st.markdown(f"**{movie['title']}** ({movie.get('year', 'N/A')})")
                if movie.get('poster_url'):
                    st.image(movie['poster_url'], width=150)
                st.markdown(f"⭐ {movie.get('rating', 'N/R')}/10")
                st.markdown(f"📝 {movie.get('overview', 'No description available.')[:100]}...")
                if movie.get('genres'):
                    st.markdown(f"🎭 {', '.join(movie['genres'][:3])}")
                st.markdown("---")
    
    # YouTube videos section
    if recommendations.get('youtube_videos'):
        st.subheader("📺 YouTube Videos")
        
        for video in recommendations['youtube_videos'][:5]:
            col1, col2 = st.columns([1, 3])
            
            with col1:
                if video.get('thumbnail_url'):
                    st.image(video['thumbnail_url'], width=120)
            
            with col2:
                st.markdown(f"**[{video['title']}]({video.get('url', '#')})**")
                st.markdown(f"👤 {video.get('channel_title', 'Unknown Channel')}")
                st.markdown(f"📅 {video.get('published_at', 'Unknown Date')}")
                if video.get('description'):
                    st.markdown(f"📝 {video['description'][:150]}...")
            
            st.markdown("---")

def display_emotion_history():
    # Get emotion history from database
    emotion_history = st.session_state.db.get_emotion_history(st.session_state.session_id, limit=5)
    
    if emotion_history:
        st.header("📊 Your Emotion History")
        
        # Show recent emotions
        for entry in emotion_history:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"*{entry['text']}*")
            
            with col2:
                st.markdown(f"**{entry['emotion'].title()}**")
            
            with col3:
                st.markdown(f"{entry['timestamp'].strftime('%m/%d %H:%M')}")
        
        # Display emotion statistics
        stats = st.session_state.db.get_emotion_stats(st.session_state.session_id)
        if stats['emotion_counts']:
            st.subheader("📈 Emotion Analytics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Most Frequent Emotions:**")
                for emotion, count in list(stats['emotion_counts'].items())[:3]:
                    st.markdown(f"• {emotion.title()}: {count} times")
            
            with col2:
                st.markdown(f"**Average Confidence:** {stats['avg_confidence']:.1%}")
        
        if st.button("Clear History"):
            st.session_state.db.clear_user_history(st.session_state.session_id)
            st.rerun()

if __name__ == "__main__":
    main()

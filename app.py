import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
from emotion_analyzer import EmotionAnalyzer
from recommendation_engine import RecommendationEngine
from database import DatabaseManager
from playlist_manager import PlaylistManager

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Initialize database
if 'db' not in st.session_state:
    st.session_state.db = DatabaseManager()

# Initialize playlist manager
if 'playlist_manager' not in st.session_state:
    st.session_state.playlist_manager = PlaylistManager(st.session_state.db)

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
                            
                            # Create and display mood-based playlist
                            with st.spinner("Creating your personalized mood playlist..."):
                                playlist = st.session_state.playlist_manager.create_mood_playlist(
                                    emotion_result['primary_emotion'],
                                    recommendations.get('movies', []),
                                    recommendations.get('youtube_videos', [])
                                )
                                
                                if playlist:
                                    # Save playlist to database
                                    st.session_state.playlist_manager.save_playlist_to_db(
                                        st.session_state.session_id, playlist
                                    )
                                    display_mood_playlist(playlist)
                        else:
                            st.error("Sorry, we couldn't find recommendations right now. Please try again later.")
                else:
                    st.error("Unable to analyze emotion. Please try rephrasing your text.")
        else:
            st.warning("Please enter some text describing how you're feeling.")
    
    # Display emotion history
    display_emotion_history()
    
    # Display saved playlists
    display_saved_playlists()

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

def display_mood_playlist(playlist):
    """Display comprehensive mood-based playlist with multiple content types"""
    st.header(f"🎵 {playlist['theme']['name']} Playlist")
    
    # Playlist header with theme info
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"**{playlist['theme']['description']}**")
        st.markdown(f"*Created for your {playlist['emotion']} mood*")
    
    with col2:
        st.markdown(f"**Total Duration:** {playlist['stats']['total_duration_estimate']['total_hours']} hours")
        st.markdown(f"**Items:** {playlist['stats']['total_items']}")
    
    # Display content by type in tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🍿 Movies", "📺 Videos", "🎵 Music", "📊 Playlist Info"])
    
    with tab1:
        movies = playlist['content']['movies']
        if movies:
            st.subheader(f"Movies ({len(movies)})")
            movie_cols = st.columns(min(3, len(movies)))
            
            for idx, movie in enumerate(movies):
                with movie_cols[idx % 3]:
                    st.markdown(f"**{movie['title']}** ({movie.get('year', 'N/A')})")
                    if movie.get('poster_url'):
                        st.image(movie['poster_url'], width=150)
                    st.markdown(f"⭐ {movie.get('rating', 'N/R')}/10")
                    st.markdown(f"📝 {movie.get('overview', 'No description available.')[:100]}...")
                    if movie.get('genres'):
                        st.markdown(f"🎭 {', '.join(movie['genres'][:3])}")
                    st.markdown("---")
        else:
            st.info("No movies available for this playlist")
    
    with tab2:
        videos = playlist['content']['youtube_videos']
        if videos:
            st.subheader(f"YouTube Videos ({len(videos)})")
            
            for video in videos:
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
        else:
            st.info("No videos available for this playlist")
    
    with tab3:
        tracks = playlist['content']['spotify_tracks']
        if tracks:
            st.subheader(f"Music Tracks ({len(tracks)})")
            
            for track in tracks:
                col1, col2, col3 = st.columns([1, 3, 1])
                
                with col1:
                    if track.get('image_url'):
                        st.image(track['image_url'], width=80)
                
                with col2:
                    if track.get('external_url'):
                        st.markdown(f"**[{track['name']}]({track['external_url']})**")
                    else:
                        st.markdown(f"**{track['name']}**")
                    st.markdown(f"👤 {track.get('artist', 'Unknown Artist')}")
                    st.markdown(f"💿 {track.get('album', 'Unknown Album')}")
                
                with col3:
                    if track.get('duration_ms'):
                        duration_min = track['duration_ms'] // 60000
                        duration_sec = (track['duration_ms'] % 60000) // 1000
                        st.markdown(f"⏱️ {duration_min}:{duration_sec:02d}")
                    
                    if track.get('preview_url'):
                        st.audio(track['preview_url'])
                
                st.markdown("---")
        else:
            # Show music recommendations based on emotion theme
            st.subheader("Music Recommendations")
            theme = playlist['theme']
            st.markdown(f"**Suggested Genres:** {', '.join(theme['music_genres'])}")
            st.markdown(f"**Mood Keywords:** {', '.join(theme['music_moods'])}")
            st.info("Connect Spotify API for personalized music recommendations")
    
    with tab4:
        st.subheader("Playlist Statistics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Content Breakdown:**")
            st.markdown(f"• Movies: {len(playlist['content']['movies'])} items")
            st.markdown(f"• Videos: {len(playlist['content']['youtube_videos'])} items")
            st.markdown(f"• Music: {len(playlist['content']['spotify_tracks'])} items")
        
        with col2:
            st.markdown("**Duration Estimates:**")
            duration = playlist['stats']['total_duration_estimate']
            st.markdown(f"• Movies: {duration.get('movies_minutes', 0)} min")
            st.markdown(f"• Videos: {duration.get('youtube_minutes', 0)} min")
            st.markdown(f"• Music: {duration.get('spotify_minutes', 0)} min")
        
        st.subheader("Emotion Theme")
        st.markdown(f"**Primary Emotion:** {playlist['emotion'].title()}")
        st.markdown(f"**Theme Color:** {playlist['theme']['color_theme']}")
        
        # Display theme as colored badge
        st.markdown(
            f"<div style='background-color: {playlist['theme']['color_theme']}; "
            f"color: white; padding: 10px; border-radius: 5px; text-align: center;'>"
            f"<strong>{playlist['theme']['name']}</strong></div>",
            unsafe_allow_html=True
        )

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

def display_saved_playlists():
    """Display user's saved mood-based playlists"""
    playlists = st.session_state.playlist_manager.get_user_playlists(st.session_state.session_id, limit=5)
    
    if playlists:
        st.header("🎵 Your Saved Playlists")
        
        for playlist in playlists:
            with st.expander(f"{playlist['theme']['name']} - {playlist['emotion'].title()} ({playlist['created_at'].strftime('%m/%d %H:%M')})"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**{playlist['theme']['description']}**")
                    st.markdown(f"• Movies: {len(playlist['content']['movies'])}")
                    st.markdown(f"• Videos: {len(playlist['content']['youtube_videos'])}")
                    st.markdown(f"• Music tracks: {len(playlist['content']['spotify_tracks'])}")
                
                with col2:
                    st.markdown(f"**Duration:** {playlist['stats']['total_duration_estimate']['total_hours']} hours")
                    st.markdown(
                        f"<div style='background-color: {playlist['theme']['color_theme']}; "
                        f"color: white; padding: 5px; border-radius: 3px; text-align: center; font-size: 12px;'>"
                        f"{playlist['theme']['name']}</div>",
                        unsafe_allow_html=True
                    )
                
                if st.button(f"View Full Playlist", key=f"view_{playlist['id']}"):
                    display_mood_playlist(playlist)

if __name__ == "__main__":
    main()

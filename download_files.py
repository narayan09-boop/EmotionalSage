"""
Script to display all app files for easy copying
Run this to see all the code files you need for the emotion recommender app
"""

import os

def display_file(filename):
    """Display file content with clear headers"""
    if os.path.exists(filename):
        print(f"\n{'='*60}")
        print(f"FILE: {filename}")
        print(f"{'='*60}")
        
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            print(content)
        
        print(f"\n{'='*60}")
        print(f"END OF {filename}")
        print(f"{'='*60}\n")
    else:
        print(f"File {filename} not found")

def main():
    print("EMOTION-AWARE CONTENT RECOMMENDER - ALL FILES")
    print("=" * 60)
    print("Copy each file section below to recreate the application")
    print("=" * 60)
    
    files_to_display = [
        'app.py',
        'emotion_analyzer.py', 
        'movie_recommender.py',
        'youtube_recommender.py',
        'recommendation_engine.py',
        'database.py',
        'playlist_manager.py',
        '.streamlit/config.toml',
        'setup_requirements.txt',
        'README.md'
    ]
    
    for filename in files_to_display:
        display_file(filename)
    
    print("\nPYTHON DEPENDENCIES:")
    print("-" * 30)
    print("streamlit>=1.28.0")
    print("pandas>=2.0.0") 
    print("psycopg2-binary>=2.9.0")
    print("textblob>=0.17.0")
    print("vaderSentiment>=3.3.0")
    print("requests>=2.31.0")
    
    print("\nREQUIRED ENVIRONMENT VARIABLES:")
    print("-" * 30)
    print("DATABASE_URL=postgresql://user:password@host:port/database")
    print("YOUTUBE_API_KEY=your_youtube_api_key")
    print("TMDB_API_KEY=your_tmdb_api_key (optional)")
    print("SPOTIFY_CLIENT_ID=your_spotify_client_id (optional)")
    print("SPOTIFY_CLIENT_SECRET=your_spotify_client_secret (optional)")

if __name__ == "__main__":
    main()
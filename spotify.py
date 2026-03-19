import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

load_dotenv()

def get_spotify_client():
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        scope="user-top-read"
    ))

def get_music_profile(sp, limit=20):
    results = sp.current_user_top_tracks(limit=limit, time_range="medium_term")
    tracks = []
    for item in results['items']:
        track = {
            'name': item['name'],
            'artist': item['artists'][0]['name'],
            'id': item['id'],
            'genres': []
        }
        try:
            artist = sp.artist(item['artists'][0]['id'])
            track['genres'] = artist.get('genres', [])
        except Exception:
            pass
        tracks.append(track)
    return tracks
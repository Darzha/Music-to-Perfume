# Music to Perfume

A web app that analyzes your Spotify listening history and uses AI to translate your music vibe into perfumes.

---

## What It Does

Connect your Spotify account and the app pulls your top tracks, analyzes the mood, energy, and personality of your listening history, then uses Claude AI to suggest 5 perfumes that match your vibe — with a score, description, and atmospheric mood image for each.

The tone is esoteric and specific. Not "you like pop so here's a floral." More like: *"you'd wear this at 2am in a city you don't live in anymore."*

---

## Demo

> App is currently in Spotify development mode. To try it, contact me to be added as a test user.

---

## Tech Stack

- **Python** + **Flask** — backend and routing
- **Spotipy** — Spotify API integration (top tracks, artist genres)
- **Anthropic Claude API** — AI-powered perfume matching and descriptions
- **Unsplash API** — mood-matched atmospheric images
- **HTML / CSS / JavaScript** — custom editorial frontend, no frameworks

---

## Features

- Spotify OAuth login
- Pulls your top 20 tracks and artist genres
- AI analyzes music personality and mood
- Returns 5 perfume recommendations with scores out of 10
- Click-through detail pages with full-screen mood images
- Animated loading screen with progress steps
- Editorial UI inspired by fashion and fragrance magazines

---

## Setup

1. Clone the repo
```bash
git clone https://github.com/Darzha/Music-to-Perfume
cd Music-to-Perfume
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory
```
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
ANTHROPIC_API_KEY=your_anthropic_key
UNSPLASH_ACCESS_KEY=your_unsplash_key
SECRET_KEY=your_secret_key
```

4. Run the app
```bash
python app.py
```

5. Open `http://127.0.0.1:8888` in your browser

---

## API Keys Required

| Service | Link | Free Tier |
|---|---|---|
| Spotify | [developer.spotify.com](https://developer.spotify.com) | Yes |
| Anthropic | [console.anthropic.com](https://console.anthropic.com) | Paid (cheap) |
| Unsplash | [unsplash.com/developers](https://unsplash.com/developers) | Yes |

---

## Note on Spotify Access

Spotify's API is currently in development mode, which limits access to manually approved users. If you want to try the app, reach out and I'll add you.

---

*Built as a personal project — a small experiment in cross-domain AI translation.*

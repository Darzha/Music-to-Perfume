import anthropic
import json
import re
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def analyze_and_match(tracks):
    track_lines = []
    for t in tracks[:15]:
        genres = ', '.join(t.get('genres', [])[:3]) or 'unknown'
        track_lines.append(f"- {t['name']} by {t['artist']} | genres: {genres}")

    track_summary = '\n'.join(track_lines)

    prompt = f"""Based on this person's Spotify listening history, suggest 5 perfumes that match their vibe.

Their top tracks:
{track_summary}

For each perfume give:
- Name and brand
- A score out of 10 for how well it matches
- 1-2 sentence explanation of why it fits their music personality. Use an esoteric, gen z, and sarcastic tone. Think like a fragrantica commenter who is also a music snob.
- A vibe keyword for image search (2-3 words max, evocative, e.g. "dark amber night" or "fresh coastal morning")

Be specific and creative. Think mood, texture, emotion, specific scenarios — not just genre. Use your knowledge of what these perfumes actually smell like.

Respond ONLY with a valid JSON array, no markdown, no extra text:
[
  {{
    "name": "Perfume Name",
    "brand": "Brand Name",
    "score": 8,
    "description": "1-2 sentence description",
    "vibe_keyword": "mood keyword"
  }}
]"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text
    raw = re.sub(r'```json|```', '', raw).strip()

    try:
        return json.loads(raw)
    except Exception:
        return []
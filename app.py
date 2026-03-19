from flask import Flask, redirect, request, render_template_string, session
from spotify import get_spotify_client, get_music_profile
from vibe import analyze_and_match
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallbacksecret999")

UNSPLASH_KEY = os.getenv("UNSPLASH_ACCESS_KEY")


def get_unsplash_image(keyword):
    try:
        url = "https://api.unsplash.com/search/photos"
        params = {"query": keyword, "per_page": 1, "orientation": "landscape", "client_id": UNSPLASH_KEY}
        res = requests.get(url, params=params, timeout=5)
        data = res.json()
        if data.get("results"):
            return data["results"][0]["urls"]["regular"]
    except Exception:
        pass
    return "https://images.unsplash.com/photo-1541643600914-78b084683702?w=800"


INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>What Do You Smell Like?</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,700&family=DM+Mono:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
  :root { --black: #0a0a0a; --white: #f5f3ef; --gray: #444240; --accent: #c4a882; --border: #ddd9d3; }
  html, body { background: var(--white); color: var(--black); font-family: 'DM Mono', monospace; height: 100%; overflow: hidden; }
  .page { width: 100vw; height: 100vh; display: flex; flex-direction: column; justify-content: center; align-items: flex-start; padding: 80px 100px; position: relative; }
  .label { font-size: 11px; letter-spacing: 0.25em; text-transform: uppercase; color: var(--gray); margin-bottom: 48px; font-weight: 500; }
  h1 { font-family: 'Playfair Display', serif; font-size: clamp(52px, 8vw, 110px); font-weight: 700; line-height: 0.95; letter-spacing: -0.02em; margin-bottom: 48px; max-width: 800px; }
  h1 em { font-style: italic; font-weight: 400; color: var(--gray); }
  .connect-btn { display: inline-block; padding: 14px 40px; background: var(--black); color: var(--white); font-family: 'DM Mono', monospace; font-size: 11px; font-weight: 500; letter-spacing: 0.2em; text-transform: uppercase; text-decoration: none; transition: background 0.2s, color 0.2s; }
  .connect-btn:hover { background: var(--accent); color: var(--black); }
  .corner-text { position: absolute; bottom: 40px; right: 60px; font-size: 10px; font-weight: 500; color: var(--gray); letter-spacing: 0.15em; text-transform: uppercase; }
  .corner-tl { position: absolute; top: 40px; left: 100px; font-size: 11px; font-weight: 500; color: var(--gray); letter-spacing: 0.2em; text-transform: uppercase; }
</style>
</head>
<body>
<div class="page">
  <span class="corner-tl">What Do You Smell Like?</span>
  <div class="label">A Scent Profile Based On Your Music</div>
  <h1>Your music taste<br>translated into<br><em>perfumes.</em></h1>
  <a href="/login" class="connect-btn">Connect Spotify</a>
  <span class="corner-text">(scroll)</span>
</div>
</body>
</html>
"""

LOADING_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Analyzing...</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;1,400&family=DM+Mono:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
  :root { --black: #0a0a0a; --white: #f5f3ef; --gray: #444240; --border: #ddd9d3; }
  body { background: var(--white); font-family: 'DM Mono', monospace; }
  .loading-page { width: 100vw; height: 100vh; display: flex; flex-direction: column; justify-content: center; align-items: center; }
  .loading-title { font-family: 'Playfair Display', serif; font-size: 24px; font-weight: 400; margin-bottom: 40px; letter-spacing: 0.03em; }
  .loading-bar-wrap { width: 220px; height: 1px; background: var(--border); overflow: hidden; }
  .loading-bar { height: 1px; background: var(--black); width: 0%; animation: load 35s ease-in-out forwards; }
  @keyframes load { 0%{width:0%} 85%{width:88%} 100%{width:95%} }
  .loading-sub { margin-top: 24px; font-size: 10px; font-weight: 500; letter-spacing: 0.2em; color: var(--gray); text-transform: uppercase; }
  .step { margin-top: 16px; font-size: 10px; font-weight: 400; letter-spacing: 0.15em; color: var(--gray); text-transform: uppercase; min-height: 16px; transition: opacity 0.4s; }
  .dots::after { content: ''; animation: dots 1.5s steps(3, end) infinite; }
  @keyframes dots { 0%{content:''} 33%{content:'.'} 66%{content:'..'} 100%{content:'...'} }
</style>
</head>
<body>
<div class="loading-page">
  <div class="loading-title">Reading your taste<span class="dots"></span></div>
  <div class="loading-bar-wrap"><div class="loading-bar"></div></div>
  <div class="loading-sub">This takes about 30 seconds</div>
  <div class="step" id="step">Connecting to Spotify</div>
</div>
<script>
  var steps = ["Connecting to Spotify","Fetching your top tracks","Translating your vibe","Matching to perfumes","Finding mood images","Almost there"];
  var i = 0;
  var el = document.getElementById('step');
  function nextStep() {
    if (i < steps.length - 1) {
      i++;
      el.style.opacity = 0;
      setTimeout(function() { el.textContent = steps[i]; el.style.opacity = 1; }, 400);
      setTimeout(nextStep, 5000);
    }
  }
  setTimeout(nextStep, 3000);
  fetch('/process').then(function() { window.location.href = '/results'; });
</script>
</body>
</html>
"""

RESULTS_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>What Do You Smell Like?</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,700&family=DM+Mono:wght@300;400;500&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
  :root { --black: #0a0a0a; --white: #f5f3ef; --gray: #444240; --accent: #c4a882; --border: #ddd9d3; }
  html { scroll-behavior: smooth; }
  body { color: var(--black); font-family: 'DM Mono', monospace; background-color: var(--white); background-image: url('{{ perfumes[0].image if perfumes else "" }}'); background-size: cover; background-position: center; background-attachment: fixed; }
  body::before { content: ''; position: fixed; inset: 0; background: rgba(245,243,239,0.93); z-index: 0; pointer-events: none; }
  nav, #results-view, .detail-page { position: relative; z-index: 1; }
  nav { position: fixed; top: 0; left: 0; right: 0; z-index: 100; display: flex; justify-content: space-between; align-items: center; padding: 28px 60px; background: rgba(245,243,239,0.95); border-bottom: 1px solid var(--border); backdrop-filter: blur(8px); }
  .nav-brand { font-size: 11px; font-weight: 500; letter-spacing: 0.2em; text-transform: uppercase; }
  .nav-right { font-size: 10px; font-weight: 500; color: var(--gray); letter-spacing: 0.15em; }
  .nav-right a { color: var(--gray); text-decoration: none; }
  .nav-right a:hover { color: var(--black); }
  .hero { padding: 160px 100px 80px; border-bottom: 1px solid var(--border); display: grid; grid-template-columns: 1fr 1fr; gap: 60px; align-items: end; }
  .hero-label { font-size: 11px; font-weight: 500; letter-spacing: 0.25em; text-transform: uppercase; color: var(--gray); margin-bottom: 24px; }
  .hero-title { font-family: 'Playfair Display', serif; font-size: clamp(36px, 5vw, 64px); font-weight: 700; line-height: 1.05; letter-spacing: -0.02em; }
  .hero-title em { font-style: italic; font-weight: 400; color: var(--gray); }
  .tracks-list { font-size: 11px; line-height: 2.2; font-weight: 400; color: var(--gray); border-left: 1px solid var(--border); padding-left: 40px; }
  .tracks-list span { display: block; }
  .tracks-label { font-size: 10px; font-weight: 500; letter-spacing: 0.2em; text-transform: uppercase; color: var(--black); margin-bottom: 16px; }
  .perfume-list { padding: 0 100px 120px; }
  .perfume-row { display: grid; grid-template-columns: 80px 1fr 1fr 120px; align-items: center; gap: 40px; padding: 32px 0; border-bottom: 1px solid var(--border); cursor: pointer; transition: background 0.15s; position: relative; }
  .perfume-row:hover { background: rgba(0,0,0,0.02); }
  .perfume-row:hover .row-arrow { opacity: 1; transform: translateX(0); }
  .row-num { font-size: 11px; font-weight: 500; color: var(--gray); letter-spacing: 0.1em; }
  .row-name { font-family: 'Playfair Display', serif; font-size: 22px; font-weight: 700; }
  .row-brand { font-size: 11px; font-weight: 400; color: var(--gray); margin-top: 4px; letter-spacing: 0.05em; }
  .row-desc { font-size: 12px; font-weight: 400; color: var(--gray); line-height: 1.7; }
  .row-score { font-family: 'Playfair Display', serif; font-size: 36px; font-weight: 700; text-align: right; color: var(--black); }
  .row-score span { font-size: 14px; font-weight: 400; color: var(--gray); font-family: 'DM Mono', monospace; }
  .row-arrow { position: absolute; right: 0; font-size: 20px; opacity: 0; transform: translateX(-8px); transition: opacity 0.2s, transform 0.2s; color: var(--accent); }
  .detail-page { display: none; }
  .detail-page.active { display: block; }
  .detail-hero { height: 60vh; overflow: hidden; position: relative; }
  .detail-img { width: 100%; height: 100%; object-fit: cover; filter: grayscale(15%); }
  .detail-overlay { position: absolute; bottom: 0; left: 0; right: 0; padding: 60px 100px; background: linear-gradient(transparent, rgba(245,243,239,0.97)); }
  .detail-label { font-size: 10px; font-weight: 500; letter-spacing: 0.25em; text-transform: uppercase; color: var(--gray); margin-bottom: 12px; }
  .detail-name { font-family: 'Playfair Display', serif; font-size: clamp(36px, 6vw, 80px); font-weight: 700; line-height: 1; letter-spacing: -0.02em; }
  .detail-body { padding: 60px 100px 120px; display: grid; grid-template-columns: 1fr 1fr; gap: 80px; }
  .detail-score-label { font-size: 10px; font-weight: 500; letter-spacing: 0.2em; text-transform: uppercase; color: var(--gray); margin-bottom: 16px; }
  .detail-score-num { font-family: 'Playfair Display', serif; font-size: 100px; font-weight: 900; line-height: 1; color: var(--black); }
  .detail-score-denom { font-size: 20px; color: var(--gray); font-family: 'DM Mono', monospace; font-weight: 400; }
  .detail-desc { font-size: 17px; line-height: 1.9; color: var(--black); margin-top: 40px; font-family: 'Playfair Display', serif; font-style: italic; font-weight: 400; }
  .detail-mood { font-family: 'Playfair Display', serif; font-size: 28px; font-style: italic; font-weight: 400; color: var(--gray); margin-top: 16px; }
  @keyframes fadeUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
  .perfume-row { animation: fadeUp 0.4s ease both; }
  {% for i in range(5) %}.perfume-row:nth-child({{ i+1 }}) { animation-delay: {{ i * 0.08 }}s; }
  {% endfor %}
</style>
</head>
<body>
<nav>
  <span class="nav-brand">What Do You Smell Like?</span>
  <span class="nav-right"><a href="/" id="nav-link">← Start Over</a></span>
</nav>
<div id="results-view">
  <div class="hero">
    <div>
      <div class="hero-label">Your Scent Profile — Based On Spotify</div>
      <h1 class="hero-title">You smell like<br><em>this.</em></h1>
    </div>
    <div class="tracks-list">
      <div class="tracks-label">Listening To</div>
      {% for t in tracks %}<span>{{ t }}</span>{% endfor %}
    </div>
  </div>
  <div class="perfume-list">
    {% for p in perfumes %}
    <div class="perfume-row" onclick="showDetail({{ loop.index0 }})">
      <div class="row-num">(0{{ loop.index }})</div>
      <div><div class="row-name">{{ p.name }}</div><div class="row-brand">{{ p.brand }}</div></div>
      <div class="row-desc">{{ p.description }}</div>
      <div class="row-score">{{ p.score }}<span>/10</span></div>
      <div class="row-arrow">↗</div>
    </div>
    {% endfor %}
  </div>
</div>
{% for p in perfumes %}
<div class="detail-page" id="detail-{{ loop.index0 }}">
  <div style="padding-top: 80px;">
    <div class="detail-hero">
      <img class="detail-img" src="{{ p.image }}" alt="{{ p.name }}">
      <div class="detail-overlay">
        <div class="detail-label">{{ p.brand }}</div>
        <div class="detail-name">{{ p.name }}</div>
      </div>
    </div>
    <div class="detail-body">
      <div>
        <div class="detail-score-label">Match Score</div>
        <div class="detail-score-num">{{ p.score }}<span class="detail-score-denom">/10</span></div>
        <div class="detail-desc">{{ p.description }}</div>
      </div>
      <div>
        <div class="detail-score-label">Mood</div>
        <div class="detail-mood">{{ p.vibe_keyword }}</div>
      </div>
    </div>
  </div>
</div>
{% endfor %}
<script>
  function showDetail(i) {
    document.getElementById('results-view').style.display = 'none';
    document.querySelectorAll('.detail-page').forEach(d => d.classList.remove('active'));
    document.getElementById('detail-' + i).classList.add('active');
    var link = document.getElementById('nav-link');
    link.textContent = '← Back To Results';
    link.href = '#';
    link.onclick = function(e) { e.preventDefault(); showResults(); };
    window.scrollTo(0, 0);
  }
  function showResults() {
    document.querySelectorAll('.detail-page').forEach(d => d.classList.remove('active'));
    document.getElementById('results-view').style.display = 'block';
    var link = document.getElementById('nav-link');
    link.textContent = '← Start Over';
    link.href = '/';
    link.onclick = null;
    window.scrollTo(0, 0);
  }
</script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(INDEX_HTML)


@app.route("/login")
def login():
    sp = get_spotify_client()
    auth_url = sp.auth_manager.get_authorize_url()
    return redirect(auth_url)


@app.route("/callback")
def callback():
    code = request.args.get("code")
    session['spotify_code'] = code
    return render_template_string(LOADING_HTML)


@app.route("/process")
def process():
    code = session.get('spotify_code')
    if not code:
        return "no code", 400

    sp = get_spotify_client()
    sp.auth_manager.get_access_token(code)
    tracks = get_music_profile(sp)
    perfumes = analyze_and_match(tracks)

    for p in perfumes:
        p['image'] = get_unsplash_image(p.get('vibe_keyword', 'perfume abstract'))

    track_display = [f"{t['name']} — {t['artist']}" for t in tracks[:8]]
    session['perfumes'] = perfumes
    session['tracks'] = track_display
    return "ok", 200


@app.route("/results")
def results():
    perfumes = session.get('perfumes', [])
    tracks = session.get('tracks', [])
    if not perfumes:
        return redirect('/')
    return render_template_string(RESULTS_HTML, perfumes=perfumes, tracks=tracks)


if __name__ == "__main__":
    app.run(port=8888, debug=True)
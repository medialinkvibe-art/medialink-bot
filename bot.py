# -*- coding: utf-8 -*-
import feedparser
from datetime import datetime, timedelta
from supabase import create_client
import re

# --- CONFIGURARE SUPABASE (Datele tale extrase din imagine) ---
SUPABASE_URL = "https://hdzbcjljqdkricyunaten.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhkemJjbGpxZGtyaWN5dW5hdGVuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM2MDAxMDcsImV4cCI6MjA4OTE3NjEwN30.nS1eXCy10Q6r8hi9CAP-RUZfo9-YsNNjx5yNA9jvNzM"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

RSS_SOURCES = {
    "Agerpres": "https://www.agerpres.ro/rss",
    "Digi24": "https://www.digi24.ro/rss",
    "Hotnews": "https://hotnews.ro/feed",
    "G4Media": "https://www.g4media.ro/feed",
    "Ziarul Financiar": "https://www.zf.ro/rss"
}

CAT_IMAGES = {
    "Politica": "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?q=80&w=800",
    "Economie": "https://images.unsplash.com/photo-1611974714014-4b52adac300e?q=80&w=800",
    "Sport": "https://images.unsplash.com/photo-1504450758481-7338eba7524a?q=80&w=800",
    "Monden": "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?q=80&w=800",
    "Actualitate": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=800"
}

def detect_category(t, s):
    txt = (t + " " + s).lower()
    if any(w in txt for w in ["pib", "curs", "bursa", "euro", "profit", "economie"]): return "Economie"
    if any(w in txt for w in ["guvern", "parlament", "psd", "pnl", "vot", "lege"]): return "Politica"
    if any(w in txt for w in ["fotbal", "meci", "liga", "tenis", "gol", "echipa", "sport"]): return "Sport"
    if any(w in txt for w in ["vedete", "showbiz", "monden", "actor"]): return "Monden"
    return "Actualitate"

def get_image(entry, cat):
    img = None
    if 'media_content' in entry: img = entry.media_content[0]['url']
    elif 'summary' in entry:
        match = re.search(r'<img [^>]*src="([^"]+)"', entry.summary)
        if match: img = match.group(1)
    return img if img else CAT_IMAGES.get(cat)

def sync():
    # Stergem stiri > 48h
    limita = (datetime.now() - timedelta(hours=48)).isoformat()
    try: supabase.table("stiri").delete().lt("created_at", limita).execute()
    except: pass
    
    count = 0
    for name, url in RSS_SOURCES.items():
        try:
            f = feedparser.parse(url)
            for e in f.entries[:15]:
                t = getattr(e, 'title', '').strip()
                l = getattr(e, 'link', '#')
                if not t or l == '#': continue
                cat = detect_category(t, getattr(e, 'summary', ''))
                img = get_image(e, cat)
                data = {"titlu": t, "url_sursa": l, "sursa_nume": name, "imagine_url": img, "category_name": cat}
                supabase.table("stiri").upsert(data, on_conflict="titlu").execute()
                count += 1
        except: continue
    print(f"✅ Sincronizare reusita: {count} stiri in baza de date.")

if __name__ == "__main__":
    sync()

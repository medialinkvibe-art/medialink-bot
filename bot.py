import feedparser
import time
import re
from supabase import create_client
from bs4 import BeautifulSoup

# --- CONFIGURARE ---
URL = "https://hdzbcjljqdkricyunaten.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhkemJjbGpxZGtyaWN5dW5hdGVuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM2MDAxMDcsImV4cCI6MjA4OTE3NjEwN30.nS1eXCy10Q6r8hi9CAP-RUZfo9-YsNNjx5yNA9jvNzM"
supabase = create_client(URL, KEY)

SURSE = {
    "Digi24": "https://www.digi24.ro/rss",
    "Hotnews": "https://www.hotnews.ro/rss",
    "Agerpres": "https://www.agerpres.ro/rss",
    "ZF": "https://www.zf.ro/rss",
    "G4Media": "https://www.g4media.ro/feed"
}

def detect_cat(t):
    t = t.lower()
    if any(x in t for x in ["sport", "fotbal", "tenis"]): return "Sport"
    if any(x in t for x in ["euro", "bnr", "bursa", "economie"]): return "Economie"
    if any(x in t for x in ["guvern", "parlament", "psd", "pnl"]): return "Politica"
    if any(x in t for x in ["vedete", "monden", "cancan"]): return "Monden"
    return "Actualitate"

def sync():
    print("🚀 Sincronizare Intelligence Hub...")
    for nume, url in SURSE.items():
        try:
            f = feedparser.parse(url)
            for e in f.entries[:15]:
                titlu = e.get('title', '').strip()
                if not titlu: continue
                
                img = "https://images.unsplash.com/photo-1585829365234-781f8c48e225?q=80&w=1200"
                if 'media_content' in e: img = e.media_content[0]['url']
                elif 'enclosures' in e and e.enclosures: img = e.enclosures[0]['href']
                
                data = {
                    "titlu": titlu,
                    "url_sursa": e.link,
                    "sursa_nume": nume,
                    "imagine_url": img,
                    "rezumat": BeautifulSoup(e.get('summary', ''), "html.parser").get_text()[:180],
                    "categorie": detect_cat(titlu),
                    "is_breaking": any(x in titlu.upper() for x in ["BREAKING", "ALERTĂ", "ULTIMA ORĂ"])
                }
                supabase.table("stiri").upsert(data, on_conflict="titlu").execute()
        except: continue
    print("✅ Flux actualizat.")

if __name__ == "__main__":
    sync()

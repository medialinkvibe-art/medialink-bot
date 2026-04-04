import feedparser
import time
import re
from supabase import create_client
from bs4 import BeautifulSoup

# --- DATE CONEXIUNE ---
URL = "https://hdzbcjljqdkricyunaten.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhkemJjbGpxZGtyaWN5dW5hdGVuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM2MDAxMDcsImV4cCI6MjA4OTE3NjEwN30.nS1eXCy10Q6r8hi9CAP-RUZfo9-YsNNjx5yNA9jvNzM"
supabase = create_client(URL, KEY)

SURSE = {
    "Digi24": "https://www.digi24.ro/rss",
    "Hotnews": "https://www.hotnews.ro/rss",
    "Agerpres": "https://www.agerpres.ro/rss",
    "BBC World": "https://feeds.bbci.co.uk/news/world/rss.xml",
    "Ziarul Financiar": "https://www.zf.ro/rss"
}

def get_category(titlu):
    t = titlu.lower()
    if any(x in t for x in ["sport", "fotbal", "meci"]): return "Sport"
    if any(x in t for x in ["euro", "bnr", "bursa", "economie", "profit"]): return "Economie"
    if any(x in t for x in ["guvern", "parlament", "vot", "lege"]): return "Politica"
    if any(x in t for x in ["vedete", "monden", "showbiz"]): return "Monden"
    return "Actualitate"

def sync():
    print("📊 Actualizare flux Intelligence Hub...")
    for nume, url in SURSE.items():
        try:
            f = feedparser.parse(url)
            for e in f.entries[:12]:
                titlu = e.get('title', '').strip()
                if not titlu: continue
                
                sumar = e.get('summary', '')
                clean_text = BeautifulSoup(sumar, "html.parser").get_text()[:200]
                
                # Imagine
                img = "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=1200"
                if 'media_content' in e: img = e.media_content[0]['url']
                elif 'enclosures' in e and e.enclosures: img = e.enclosures[0]['href']
                
                data = {
                    "titlu": titlu,
                    "url_sursa": e.link,
                    "sursa_nume": nume,
                    "imagine_url": img,
                    "rezumat": clean_text,
                    "categorie": get_category(titlu),
                    "is_breaking": any(x in titlu.upper() for x in ["BREAKING", "ALERTĂ", "URGENT"])
                }
                supabase.table("stiri").upsert(data, on_conflict="titlu").execute()
        except: continue
    print("✅ Flux sincronizat.")

if __name__ == "__main__":
    sync()

import feedparser
import time
from supabase import create_client
from bs4 import BeautifulSoup
import requests

# DATE CONEXIUNE REALE (Verificate din screenshot-ul tău)
URL = "https://hdzbcjljqdkricyunaten.supabase.co"
KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhkemJjbGpxZGtyaWN5dW5hdGVuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM2MDAxMDcsImV4cCI6MjA4OTE3NjEwN30.nS1eXCy10Q6r8hi9CAP-RUZfo9-YsNNjx5yNA9jvNzM"
supabase = create_client(URL, KEY)

SURSE = {
    "Digi24": "https://www.digi24.ro/rss",
    "Hotnews": "https://www.hotnews.ro/rss",
    "Agerpres": "https://www.agerpres.ro/rss",
    "ProTV": "https://stirileprotv.ro/rss",
    "G4Media": "https://www.g4media.ro/feed",
    "Cancan": "https://www.cancan.ro/feed",
    "Ziarul Financiar": "https://www.zf.ro/rss"
}

def gaseste_poza(e):
    if 'enclosures' in e and e.enclosures: return e.enclosures[0].get('href')
    if 'media_content' in e: return e.media_content[0].get('url')
    soup = BeautifulSoup(e.get('summary', ''), 'html.parser')
    img = soup.find('img')
    return img.get('src') if img else "https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=800"

def sync():
    print("🔄 Sincronizare cele 7 surse...")
    for nume, url in SURSE.items():
        try:
            r = requests.get(url, timeout=10)
            f = feedparser.parse(r.content)
            for e in f.entries[:10]:
                data = {
                    "titlu": e.get('title', '').strip(),
                    "url_sursa": e.link,
                    "sursa_nume": nume,
                    "imagine_url": gaseste_poza(e),
                    "rezumat": BeautifulSoup(e.get('summary', ''), "html.parser").get_text()[:150],
                    "categorie": "Actualitate",
                    "is_breaking": any(x in e.get('title', '').upper() for x in ["BREAKING", "ALERTĂ"])
                }
                supabase.table("stiri").upsert(data, on_conflict="titlu").execute()
        except: continue
    print("✅ Finalizat.")

if __name__ == "__main__":
    sync()

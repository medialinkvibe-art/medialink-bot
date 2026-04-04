import feedparser
import time
import re
from supabase import create_client
from bs4 import BeautifulSoup
import requests

# --- CONFIGURARE DIRECTĂ ---
SUPABASE_URL = "https://hdzbcjljqdkricyunaten.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImhkemJjbGpxZGtyaWN5dW5hdGVuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM2MDAxMDcsImV4cCI6MjA4OTE3NjEwN30.nS1eXCy10Q6r8hi9CAP-RUZfo9-YsNNjx5yNA9jvNzM"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

SURSE = {
    "Digi24": "https://www.digi24.ro/rss",
    "Hotnews": "https://www.hotnews.ro/rss",
    "Agerpres": "https://www.agerpres.ro/rss",
    "G4Media": "https://www.g4media.ro/feed",
    "Ziarul Financiar": "https://www.zf.ro/rss"
}

def detecteaza_categoria(titlu):
    t = titlu.lower()
    if any(x in t for x in ["sport", "fotbal", "tenis", "echipa"]): return "Sport"
    if any(x in t for x in ["euro", "bnr", "bursa", "economie", "pib", "zf"]): return "Economie"
    if any(x in t for x in ["guvern", "parlament", "psd", "pnl", "vot"]): return "Politica"
    if any(x in t for x in ["vedete", "showbiz", "monden", "cancan"]): return "Monden"
    return "Actualitate"

def curata_stiri_vechi():
    try:
        # Supabase folosește format ISO pentru timestamp
        prag_iso = (datetime.now() - timedelta(hours=48)).isoformat()
        supabase.table("stiri").delete().lt("created_at", prag_iso).execute()
        print(f"🧹 Curățenie efectuată.")
    except: pass

def gaseste_poza(e):
    fallback = "https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=800"
    try:
        if 'media_content' in e: return e.media_content[0]['url']
        summary = e.get('summary', '')
        match = re.search(r'src="([^"]+)"', summary)
        if match: return match.group(1)
    except: pass
    return fallback

def colecteaza():
    print(f"🔄 Pornire scanare live...")
    stiri_noi = 0
    
    for nume, url in SURSE.items():
        try:
            feed = feedparser.parse(url)
            for e in feed.entries[:10]:
                link = e.link
                
                # Verificăm dacă există deja după titlu pentru a evita duplicatele
                titlu = e.get('title', '').strip()
                if not titlu: continue

                # Verificăm dacă titlul conține cuvinte de alertă pentru coloana is_breaking
                is_breaking = any(x in titlu.upper() for x in ["BREAKING", "ALERTĂ", "ULTIMA ORĂ"])
                
                rezumat_raw = e.get('summary', '')
                rezumat_clean = BeautifulSoup(rezumat_raw, "html.parser").get_text()[:200]

                data_insert = {
                    "titlu": titlu,
                    "url_sursa": link,
                    "sursa_nume": nume,
                    "imagine_url": gaseste_poza(e),
                    "is_breaking": is_breaking,
                    "categorie": detecteaza_categoria(titlu),
                    "rezumat": rezumat_clean
                }
                
                # Folosim upsert pentru a nu avea erori la duplicate
                supabase.table("stiri").upsert(data_insert, on_conflict="titlu").execute()
                stiri_noi += 1
                    
        except Exception as err:
            print(f"⚠️ Eroare sursa {nume}: {err}")
            
    print(f"✅ Finalizat! {stiri_noi} articole procesate.")

if __name__ == "__main__":
    from datetime import datetime, timedelta # Avem nevoie de acestea pentru curățare
    colecteaza()

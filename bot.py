# -*- coding: utf-8 -*-
import feedparser
from datetime import datetime, timedelta
from supabase import create_client
import re

# --- CONFIGURARE SUPABASE ---
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

def detect_category(t, s):
    txt = (t + " " + s).lower()
    if any(w in txt for w in ["pib", "curs", "bursa", "euro", "profit", "economie"]): return "Economie"
    if any(w in txt for w in ["guvern", "parlament", "psd", "pnl", "vot", "lege"]): return "Politica"
    if any(w in txt for w in ["fotbal", "meci", "liga", "tenis", "gol", "echipa"]): return "Sport"
    if any(w in txt for w in ["vedete", "showbiz", "monden", "actor"]): return "Monden"
    return "Actualitate"

def sync():
    # Stergem ce e mai vechi de 48h
    limita = (datetime.now() - timedelta(hours=48)).isoformat()
    try: supabase.table("stiri").delete().lt("created_at", limita).execute()
    except: pass
    
    count = 0
    for name, url in RSS_SOURCES.items():
        try:
            f = feedparser.parse(url)
            for e in f.entries[:10]:
                titlu = getattr(e, 'title', '').strip()
                link = getattr(e, 'link', '#')
                if not titlu or link == '#': continue
                
                sumar_raw = getattr(e, 'summary', '')
                # Curatam sumarul de tag-uri HTML pentru coloana 'rezumat'
                rezumat = re.sub('<[^<]+?>', '', sumar_raw)[:250] 
                cat = detect_category(titlu, sumar_raw)
                
                # Cautam imaginea in RSS
                img = None
                if 'media_content' in e: img = e.media_content[0]['url']
                else:
                    match = re.search(r'<img [^>]*src="([^"]+)"', sumar_raw)
                    if match: img = match.group(1)
                
                # CONSTRUCTIA DATELOR (exact ca in schema ta din imagine)
                data = {
                    "titlu": titlu,
                    "url_sursa": link,
                    "sursa_nume": name,
                    "imagine_url": img if img else "https://images.unsplash.com/photo-1504711434969-e33886168f5c",
                    "rezumat": rezumat,
                    "categorie": cat,
                    "is_breaking": False
                }
                
                supabase.table("stiri").upsert(data, on_conflict="titlu").execute()
                count += 1
        except Exception as err: 
            print(f"Eroare la {name}: {err}")
            continue
            
    print(f"✅ Sincronizare reusita: {count} stiri.")

if __name__ == "__main__":
    sync()

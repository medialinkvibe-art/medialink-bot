import feedparser
import os
import time
from supabase import create_client
from bs4 import BeautifulSoup
import requests

# --- CONFIGURARE ---
# Asigură-te că aceste variabile sunt setate în mediul tău (GitHub Actions sau local)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ EROARE: Lipsesc cheile Supabase!")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

SURSE = {
    "Digi24": "https://www.digi24.ro/rss",
    "Hotnews": "https://www.hotnews.ro/rss",
    "Agerpres": "https://www.agerpres.ro/rss",
    "ProTV": "https://stirileprotv.ro/rss",
    "G4Media": "https://www.g4media.ro/feed",
    "Cancan": "https://www.cancan.ro/feed",
    "Ziarul Financiar": "https://www.zf.ro/rss"
}

def detecteaza_categoria(titlu):
    """Atribuie o categorie în funcție de cuvintele cheie din titlu"""
    t = titlu.lower()
    if any(x in t for x in ["sport", "fotbal", "simona halep", "liga 1", "tenis", "echipa națională"]):
        return "Sport"
    if any(x in t for x in ["euro", "curs valutar", "bnr", "bursa", "economie", "pib", "inflatie", "zf"]):
        return "Economie"
    if any(x in t for x in ["guvern", "parlament", "psd", "pnl", "alegeri", "senat", "usr", "vot"]):
        return "Politica"
    if any(x in t for x in ["vedete", "showbiz", "monden", "cancan", "horoscop", "wowbiz"]):
        return "Monden"
    return "Actualitate"

def curata_stiri_vechi():
    """Șterge automat știrile mai vechi de 48 ore pentru a păstra baza de date curată"""
    try:
        prag_secunde = time.time() - (48 * 3600)
        prag_iso = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(prag_secunde))
        supabase.table("stiri").delete().lt("created_at", prag_iso).execute()
        print(f"🧹 Curățenie: S-au șters datele mai vechi de {prag_iso}")
    except Exception as e:
        print(f"⚠️ Notă curățare: {e}")

def gaseste_poza(entry):
    """Încearcă să extragă o imagine din feed-ul RSS"""
    fallback = "https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=800"
    try:
        if 'enclosures' in entry and entry.enclosures:
            return entry.enclosures[0].get('href')
        if 'media_content' in entry:
            return entry.media_content[0].get('url')
        html = entry.get('summary', '') or entry.get('description', '')
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            img = soup.find('img')
            if img and img.get('src'): return img.get('src')
    except: pass
    return fallback

def colecteaza():
    print(f"🔄 [{time.strftime('%H:%M:%S')}] Pornire scanare live...")
    stiri_noi = 0
    
    for nume, url in SURSE.items():
        try:
            resp = requests.get(url, timeout=15)
            feed = feedparser.parse(resp.content)
            
            for e in feed.entries:
                link = e.link
                
                # Verificare dacă știrea există deja (după URL)
                verif = supabase.table("stiri").select("id").eq("url_sursa", link).execute()
                
                if not verif.data:
                    titlu = e.get('title', 'Fără titlu')
                    
                    # Detectie ALERT (pentru secțiunea roșie din site)
                    is_breaking = any(x in titlu.upper() for x in ["BREAKING", "ALERTĂ", "URGENT", "NEWS ALERT", "ULTIMA ORĂ"])
                    
                    data_insert = {
                        "titlu": titlu,
                        "url_sursa": link,
                        "sursa_nume": nume,
                        "imagine_url": gaseste_poza(e),
                        "is_breaking": is_breaking,
                        "categorie": detecteaza_categoria(titlu),
                        "rezumat": BeautifulSoup(e.get('summary', ''), "html.parser").get_text()[:200] if e.get('summary') else None
                    }
                    
                    supabase.table("stiri").insert(data_insert).execute()
                    stiri_noi += 1
                    
        except Exception as err:
            print(f"⚠️ Eroare sursa {nume}: {err}")
            
    print(f"✅ Finalizat! {stiri_noi} știri noi adăugate în bază.")

if __name__ == "__main__":
    curata_stiri_vechi()
    colecteaza()

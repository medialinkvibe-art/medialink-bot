# -*- coding: utf-8 -*-
import feedparser
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import time

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
    if any(w in txt for w in ["fotbal", "meci", "liga", "tenis", "gol", "echipa"]): return "Sport"
    if any(w in txt for w in ["cancan", "showbiz", "vedeta", "monden"]): return "Monden"
    return "Actualitate"

def generate_feed():
    rss = ET.Element("rss", version="2.0")
    rss.set("xmlns:media", "http://search.yahoo.com/mrss/")
    ch = ET.SubElement(rss, "channel")
    
    # Limita de timp: 48 de ore
    limita_timp = datetime.now() - timedelta(hours=48)
    
    seen_titles = set()

    for name, url in RSS_SOURCES.items():
        try:
            f = feedparser.parse(url)
            for e in f.entries:
                title = getattr(e, 'title', '').strip()
                # Verificare data si duplicate
                dt_pub = datetime(*(e.published_parsed[:6])) if hasattr(e, 'published_parsed') else datetime.now()
                
                if title in seen_titles or dt_pub < limita_timp:
                    continue
                
                seen_titles.add(title)
                desc = getattr(e, 'summary', '').strip()
                cat = detect_category(title, desc)
                
                item = ET.SubElement(ch, "item")
                ET.SubElement(item, "title").text = title
                ET.SubElement(item, "link").text = getattr(e, 'link', '#')
                # Salvare data in format ISO pentru sortare usoara in JS
                ET.SubElement(item, "pubDate").text = dt_pub.isoformat()
                ET.SubElement(item, "source_name").text = name
                ET.SubElement(item, "category_name").text = cat
                media = ET.SubElement(item, "{http://search.yahoo.com/mrss/}content")
                media.set("url", CAT_IMAGES[cat])
        except: continue
    
    ET.ElementTree(rss).write("feed.xml", encoding="utf-8", xml_declaration=True)
    print("✅ feed.xml generat (doar ultimele 48h)!")

if __name__ == "__main__": generate_feed()

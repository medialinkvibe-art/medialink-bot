# -*- coding: utf-8 -*-
import feedparser
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

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
    return "Actualitate"

def generate_feed():
    rss = ET.Element("rss", version="2.0")
    rss.set("xmlns:media", "http://search.yahoo.com/mrss/")
    ch = ET.SubElement(rss, "channel")
    # Punem o limita mare (20 zile) doar ca sa verificam ca apar stirile
    limita = datetime.now() - timedelta(hours=480)
    seen = set()
    count = 0

    for name, url in RSS_SOURCES.items():
        try:
            f = feedparser.parse(url)
            for e in f.entries[:15]:
                t = getattr(e, 'title', '').strip()
                d = datetime(*(e.published_parsed[:6])) if hasattr(e, 'published_parsed') else datetime.now()
                if t in seen or d < limita: continue
                seen.add(t)
                item = ET.SubElement(ch, "item")
                ET.SubElement(item, "title").text = t
                ET.SubElement(item, "link").text = getattr(e, 'link', '#')
                ET.SubElement(item, "pubDate").text = d.isoformat()
                ET.SubElement(item, "source_name").text = name
                cat = detect_category(t, getattr(e, 'summary', ''))
                ET.SubElement(item, "category_name").text = cat
                m = ET.SubElement(item, "{http://search.yahoo.com/mrss/}content")
                m.set("url", CAT_IMAGES[cat])
                count += 1
        except: continue
    ET.ElementTree(rss).write("feed.xml", encoding="utf-8", xml_declaration=True)
    print(f"✅ Gata! {count} stiri in feed.xml")

if __name__ == "__main__": generate_feed()

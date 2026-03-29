# -*- coding: utf-8 -*-
import feedparser
import xml.etree.ElementTree as ET
from datetime import datetime

# SURSE MARI SI SERIOASE
RSS_SOURCES = {
    "Agerpres": "https://www.agerpres.ro/rss",
    "Digi24": "https://www.digi24.ro/rss",
    "Hotnews": "https://hotnews.ro/feed",
    "G4Media": "https://www.g4media.ro/feed",
    "Ziarul Financiar": "https://www.zf.ro/rss",
    "Europa FM": "https://www.europafm.ro/feed/",
    "Profit.ro": "https://www.profit.ro/rss"
}

# IMAGINI REPREZENTATIVE PE CATEGORII
CAT_IMAGES = {
    "Politica": "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?q=80&w=800",
    "Economie": "https://images.unsplash.com/photo-1611974714014-4b52adac300e?q=80&w=800",
    "Sport": "https://images.unsplash.com/photo-1504450758481-7338eba7524a?q=80&w=800",
    "Monden": "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?q=80&w=800",
    "Actualitate": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=800"
}

def detect_category(title, summary):
    text = (title + " " + summary).lower()
    if any(w in text for w in ["guvern", "parlament", "psd", "pnl", "usr", "vot", "lege", "ministru", "politician"]): return "Politica"
    if any(w in text for w in ["pib", "curs", "bursa", "euro", "dolar", "profit", "economie", "pret", "banca"]): return "Economie"
    if any(w in text for w in ["fotbal", "meci", "liga", "tenis", "halep", "gol", "echipa", "campionat"]): return "Sport"
    if any(w in text for w in ["cancan", "showbiz", "vedeta", "monden", "actor", "concert"]): return "Monden"
    return "Actualitate"

def generate_feed():
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "MediaLink Intelligence Hub"
    
    for name, url in RSS_SOURCES.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:12]:
                item = ET.SubElement(channel, "item")
                title = getattr(entry, 'title', 'Fara titlu')
                desc = getattr(entry, 'summary', '')
                cat = detect_category(title, desc)
                
                ET.SubElement(item, "title").text = title
                ET.SubElement(item, "link").text = getattr(entry, 'link', '#')
                ET.SubElement(item, "description").text = desc
                ET.SubElement(item, "pubDate").text = getattr(entry, 'published', datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000"))
                ET.SubElement(item, "source_name").text = name
                ET.SubElement(item, "category_name").text = cat
                ET.SubElement(item, "category_image").text = CAT_IMAGES[cat]
        except:
            continue

    tree = ET.ElementTree(rss)
    tree.write("feed.xml", encoding="utf-8", xml_declaration=True)
    print("✅ feed.xml actualizat cu surse noi si imagini!")

if __name__ == "__main__":
    generate_feed()

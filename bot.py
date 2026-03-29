# -*- coding: utf-8 -*-
import feedparser
import xml.etree.ElementTree as ET
from datetime import datetime

# Configurare Surse
RSS_SOURCES = [
    "https://www.digi24.ro/rss",
    "https://hotnews.ro/feed",
    "https://www.adevarul.ro/rss"
]

def generate_feed():
    print("--- Pornesc colectarea stirilor ---")
    
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "MediaLink"
    ET.SubElement(channel, "link").text = "https://medialink.ro"
    ET.SubElement(channel, "description").text = "Stiri colectate local"
    ET.SubDate = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")

    count = 0
    for url in RSS_SOURCES:
        try:
            print(f"Verific sursa: {url}")
            feed = feedparser.parse(url)
            # Luam pana la 50 de stiri de la fiecare sursa
            for entry in feed.entries[:50]:
                item = ET.SubElement(channel, "item")
                ET.SubElement(item, "title").text = entry.title
                ET.SubElement(item, "link").text = entry.link
                desc = getattr(entry, 'summary', 'Fara descriere')
                ET.SubElement(item, "description").text = desc
                pub = getattr(entry, 'published', datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000"))
                ET.SubElement(item, "pubDate").text = pub
                count += 1
        except Exception as e:
            print(f"Eroare la {url}: {e}")

    # Salvare fisier
    tree = ET.ElementTree(rss)
    tree.write("feed.xml", encoding="utf-8", xml_declaration=True)
    print(f"Gata! Am salvat {count} stiri in feed.xml")

if __name__ == "__main__":
    generate_feed()

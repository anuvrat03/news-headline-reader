import feedparser
import json
import os
import openai
from datetime import datetime

client = openai.OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)

def summarize_headline(title, source):
    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Rewrite this news headline to be clean and punchy. Keep it under 90 chars. Return ONLY the headline."},
                {"role": "user", "content": f"Source: {source}. Headline: {title}"}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"AI error: {e}")
        return title

def fetch_group(group_name, feeds):
    items = []
    for feed_info in feeds:
        try:
            feed = feedparser.parse(feed_info["url"])
            for entry in feed.entries[:4]:
                items.append({
                    "title": summarize_headline(entry.title, feed_info["name"]),
                    "link": entry.link,
                    "source": feed_info["name"],
                    "group": group_name
                })
        except Exception as e:
            print(f"Error fetching {feed_info['name']}: {e}")
    return items

def main():
    with open("config.json", "r") as f:
        config = json.load(f)
    
    all_news = []
    for group, feeds in config.items():
        print(f"Fetching {group}...")
        all_news.extend(fetch_group(group, feeds))
    
    os.makedirs("data", exist_ok=True)
    with open("data/news.json", "w") as f:
        json.dump({"updated": str(datetime.now()), "headlines": all_news}, f, indent=2)

if __name__ == "__main__":
    main()

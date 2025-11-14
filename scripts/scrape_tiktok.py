#!/usr/bin/env python3
"""
TikTok Trend Scraper for Career Advice Content
Scrapes trending videos weekly and saves to JSON
"""

import os
import json
from datetime import datetime
from apify_client import ApifyClient

def scrape_tiktok_trends():
    """
    Scrapes TikTok for trending career advice videos
    Returns: List of top videos with scripts and metrics
    """
    
    api_key = os.environ.get('APIFY_API_KEY')
    if not api_key:
        print("❌ Error: APIFY_API_KEY not found in environment")
        return []
    
    client = ApifyClient(api_key)
    
    # Search queries optimized for career/professional advice
    search_queries = [
        "salary negotiation tips 2024",
        "career advice professional growth",
        "LinkedIn message templates",
        "interview questions answers",
        "resume tips ATS beat",
        "meeting control phrases",
        "email subject lines professional",
        "promotion strategy workplace",
        "networking tips career",
        "professional development hacks"
    ]
    
    all_videos = []
    
    print("🔍 Starting TikTok scrape...")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔑 API Key found: {api_key[:10]}...")
    print()
    
    for i, query in enumerate(search_queries, 1):
        print(f"[{i}/{len(search_queries)}] Scraping: '{query}'")
        
        try:
            # Configure scraper
            run_input = {
                "searchQueries": [query],
                "resultsPerPage": 10,
                "shouldDownloadVideos": False,
                "shouldDownloadCovers": False,
                "shouldDownloadSlideshowImages": False
            }
            
            # Run the TikTok scraper actor
            run = client.actor("clockworks/free-tiktok-scraper").call(run_input=run_input)
            
            # Process results
            videos_found = 0
            for item in client.dataset(run["defaultDatasetId"]).iterate_items():
                video_data = {
                    'query': query,
                    'text': item.get('text', ''),
                    'authorName': item.get('authorMeta', {}).get('name', 'Unknown'),
                    'authorUsername': item.get('authorMeta', {}).get('name', ''),
                    'views': item.get('playCount', 0),
                    'likes': item.get('diggCount', 0),
                    'shares': item.get('shareCount', 0),
                    'comments': item.get('commentCount', 0),
                    'url': item.get('webVideoUrl', ''),
                    'hashtags': [tag.get('name', '') for tag in item.get('hashtags', [])],
                    'createdTime': item.get('createTime', ''),
                    'engagement_score': calculate_engagement(item)
                }
                all_videos.append(video_data)
                videos_found += 1
            
            print(f"   ✅ Found {videos_found} videos")
            
        except Exception as e:
            print(f"   ❌ Error scraping '{query}': {str(e)}")
            continue
    
    print()
    print(f"📊 Total videos scraped: {len(all_videos)}")
    
    # Sort by engagement score
    all_videos.sort(key=lambda x: x['engagement_score'], reverse=True)
    
    # Get top 20 most engaging videos
    top_videos = all_videos[:20]
    
    # Save to file with timestamp
    output = {
        'scraped_at': datetime.now().isoformat(),
        'total_videos': len(all_videos),
        'top_videos': top_videos
    }
    
    with open('trending_content.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"✅ Saved top {len(top_videos)} trending videos to trending_content.json")
    print()
    print("📈 Top 5 Videos by Engagement:")
    for i, video in enumerate(top_videos[:5], 1):
        print(f"{i}. @{video['authorUsername']}")
        print(f"   Views: {video['views']:,} | Likes: {video['likes']:,}")
        print(f"   Text: {video['text'][:100]}...")
        print()
    
    return top_videos

def calculate_engagement(item):
    """Calculate engagement score for sorting"""
    views = item.get('playCount', 0)
    likes = item.get('diggCount', 0)
    shares = item.get('shareCount', 0)
    comments = item.get('commentCount', 0)
    
    # Weighted engagement formula
    # Shares and comments are worth more than likes
    score = (views * 0.1) + (likes * 1) + (shares * 5) + (comments * 3)
    return score

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 TikTok Career Content Scraper")
    print("=" * 60)
    print()
    
    videos = scrape_tiktok_trends()
    
    if videos:
        print("=" * 60)
        print("✅ Scraping Complete!")
        print("=" * 60)
    else:
        print("=" * 60)
        print("❌ Scraping Failed - Check logs above")
        print("=" * 60)

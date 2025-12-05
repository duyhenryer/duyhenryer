#!/usr/bin/env python3
"""
Script to parse RSS feed and update README.md with latest blog posts.
This script is designed to run in GitHub Actions.
"""

import os
import re
import feedparser
from datetime import datetime

# Configuration
RSS_FEED_URL = os.getenv('RSS_FEED_URL', 'https://duyne.me/dailydiary/index.xml')
MAX_POSTS = int(os.getenv('MAX_POSTS', '10'))
README_PATH = 'README.md'
SECTION_START = '<!-- BLOG_POSTS_START -->'
SECTION_END = '<!-- BLOG_POSTS_END -->'

def parse_rss_feed(url):
    """Parse RSS feed and return list of posts."""
    try:
        feed = feedparser.parse(url)
        posts = []
        
        for entry in feed.entries[:MAX_POSTS]:
            # Extract date
            pub_date = entry.get('published_parsed') or entry.get('updated_parsed')
            if pub_date:
                date_str = datetime(*pub_date[:6]).strftime('%b %d, %Y')
            else:
                date_str = 'Date unknown'
            
            posts.append({
                'title': entry.title,
                'link': entry.link,
                'date': date_str
            })
        
        return posts
    except Exception as e:
        print(f"Error parsing RSS feed: {e}")
        return []

def format_posts_markdown(posts):
    """Format posts list as markdown with smaller font size."""
    if not posts:
        return "No posts available."
    
    lines = []
    for post in posts:
        # Use HTML with smaller font size (85% of normal size)
        lines.append(f"- <span style=\"font-size: 85%\">[{post['title']}]({post['link']}) - {post['date']}</span>")
    
    return '\n'.join(lines)

def update_readme(posts_markdown):
    """Update README.md with new blog posts section."""
    try:
        with open(README_PATH, 'r', encoding='utf-8') as f:
            readme_content = f.read()
        
        # Check if section markers exist
        if SECTION_START not in readme_content or SECTION_END not in readme_content:
            print(f"Warning: Section markers not found in README.md")
            print(f"Please add {SECTION_START} and {SECTION_END} markers in your README.md")
            return False
        
        # Create new section content
        new_section = f"{SECTION_START}\n{posts_markdown}\n{SECTION_END}"
        
        # Replace section content
        pattern = f"{re.escape(SECTION_START)}.*?{re.escape(SECTION_END)}"
        updated_content = re.sub(
            pattern,
            new_section,
            readme_content,
            flags=re.DOTALL
        )
        
        # Write updated content
        with open(README_PATH, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        # Count posts (split by newline and filter empty lines)
        post_count = len([line for line in posts_markdown.split('\n') if line.strip()])
        print(f"Successfully updated README.md with {post_count} posts")
        return True
        
    except FileNotFoundError:
        print(f"Error: {README_PATH} not found")
        return False
    except Exception as e:
        print(f"Error updating README.md: {e}")
        return False

def main():
    print(f"Fetching RSS feed from: {RSS_FEED_URL}")
    posts = parse_rss_feed(RSS_FEED_URL)
    
    if not posts:
        print("No posts found in RSS feed")
        return
    
    print(f"Found {len(posts)} posts")
    posts_markdown = format_posts_markdown(posts)
    
    if update_readme(posts_markdown):
        print("README.md updated successfully")
    else:
        print("Failed to update README.md")
        exit(1)

if __name__ == '__main__':
    main()


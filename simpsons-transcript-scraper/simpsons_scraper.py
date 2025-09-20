#!/usr/bin/env python3
"""
Simpsons Episode Transcript Scraper

Scrapes episode transcripts from Springfield! Springfield! website.
"""

import os
import re
import time
import json
import argparse
from pathlib import Path
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional

import requests
from bs4 import BeautifulSoup


class SimpsonsTranscriptScraper:
    def __init__(self, base_url: str = "https://www.springfieldspringfield.co.uk", delay: float = 1.0):
        self.base_url = base_url
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; rv:91.0) Gecko/20100101 Firefox/91.0'
        })
        
    def get_episode_list(self) -> List[Dict[str, str]]:
        """Extract all episode links from the main episodes page."""
        episodes_url = f"{self.base_url}/episode_scripts.php?tv-show=the-simpsons"
        
        print(f"Fetching episode list from: {episodes_url}")
        response = self.session.get(episodes_url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        episodes = []
        
        # Find all episode links
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href and 'view_episode_scripts.php' in href and 'the-simpsons' in href:
                episode_url = urljoin(self.base_url, href)
                title = link.get_text(strip=True)
                
                # Extract season and episode numbers from URL
                match = re.search(r'episode=s(\d+)e(\d+)', href)
                if match:
                    season = int(match.group(1))
                    episode = int(match.group(2))
                    
                    episodes.append({
                        'title': title,
                        'url': episode_url,
                        'season': season,
                        'episode': episode
                    })
        
        return sorted(episodes, key=lambda x: (x['season'], x['episode']))
    
    def get_transcript(self, episode_url: str) -> Optional[str]:
        """Download transcript from episode URL."""
        try:
            print(f"Downloading: {episode_url}")
            response = self.session.get(episode_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the transcript content - look for common transcript containers
            transcript_selectors = [
                '.episode_script',
                '.transcript',
                '#transcript',
                '.script-text',
                'div[class*="script"]',
                'div[class*="transcript"]'
            ]
            
            transcript_text = None
            for selector in transcript_selectors:
                element = soup.select_one(selector)
                if element:
                    transcript_text = element.get_text(separator='\n', strip=True)
                    break
            
            # If no specific container found, try to find the main content area
            if not transcript_text:
                # Look for the largest text block that likely contains the transcript
                content_divs = soup.find_all('div')
                longest_text = ""
                for div in content_divs:
                    text = div.get_text(separator='\n', strip=True)
                    if len(text) > len(longest_text) and len(text) > 500:  # Minimum length filter
                        longest_text = text
                
                if longest_text:
                    transcript_text = longest_text
            
            return transcript_text
            
        except requests.RequestException as e:
            print(f"Error downloading {episode_url}: {e}")
            return None
    
    def save_transcript(self, episode_info: Dict[str, str], transcript: str, output_dir: str):
        """Save transcript to organized file structure."""
        season_dir = Path(output_dir) / f"season_{episode_info['season']:02d}"
        season_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"s{episode_info['season']:02d}e{episode_info['episode']:02d}_{self.sanitize_filename(episode_info['title'])}.txt"
        filepath = season_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Title: {episode_info['title']}\n")
            f.write(f"Season: {episode_info['season']}\n")
            f.write(f"Episode: {episode_info['episode']}\n")
            f.write(f"URL: {episode_info['url']}\n")
            f.write("=" * 50 + "\n\n")
            f.write(transcript)
        
        return filepath
    
    def sanitize_filename(self, filename: str) -> str:
        """Remove invalid characters from filename."""
        return re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    def scrape_all(self, output_dir: str = "transcripts", start_season: int = 1, end_season: int = None):
        """Scrape all available episode transcripts."""
        print("Starting Simpsons transcript scraper...")
        
        # Create output directory
        Path(output_dir).mkdir(exist_ok=True)
        
        # Get episode list
        episodes = self.get_episode_list()
        print(f"Found {len(episodes)} episodes")
        
        # Filter by season range
        if end_season:
            episodes = [ep for ep in episodes if start_season <= ep['season'] <= end_season]
        else:
            episodes = [ep for ep in episodes if ep['season'] >= start_season]
        
        print(f"Scraping {len(episodes)} episodes (seasons {start_season}-{end_season or 'latest'})")
        
        # Track progress
        success_count = 0
        error_count = 0
        
        for i, episode in enumerate(episodes, 1):
            print(f"\n[{i}/{len(episodes)}] Season {episode['season']} Episode {episode['episode']}: {episode['title']}")
            
            # Download transcript
            transcript = self.get_transcript(episode['url'])
            
            if transcript:
                filepath = self.save_transcript(episode, transcript, output_dir)
                print(f"Saved to: {filepath}")
                success_count += 1
            else:
                print("Failed to download transcript")
                error_count += 1
            
            # Rate limiting
            if i < len(episodes):  # Don't delay after the last episode
                time.sleep(self.delay)
        
        # Summary
        print(f"\n" + "=" * 50)
        print(f"Scraping completed!")
        print(f"Successfully downloaded: {success_count} transcripts")
        print(f"Failed downloads: {error_count}")
        print(f"Output directory: {Path(output_dir).absolute()}")


def main():
    parser = argparse.ArgumentParser(description="Scrape Simpsons episode transcripts")
    parser.add_argument("-o", "--output", default="transcripts", help="Output directory (default: transcripts)")
    parser.add_argument("-s", "--start-season", type=int, default=1, help="Start season (default: 1)")
    parser.add_argument("-e", "--end-season", type=int, help="End season (default: all available)")
    parser.add_argument("-d", "--delay", type=float, default=1.0, help="Delay between requests in seconds (default: 1.0)")
    
    args = parser.parse_args()
    
    scraper = SimpsonsTranscriptScraper(delay=args.delay)
    scraper.scrape_all(
        output_dir=args.output,
        start_season=args.start_season,
        end_season=args.end_season
    )


if __name__ == "__main__":
    main()
# Simpsons Episode Transcript Scraper

A Python scraper to download all Simpsons episode transcripts from Springfield! Springfield!

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic usage (scrape all episodes):
```bash
python simpsons_scraper.py
```

### Scrape specific seasons:
```bash
# Scrape seasons 1-5
python simpsons_scraper.py --start-season 1 --end-season 5

# Scrape from season 10 onwards
python simpsons_scraper.py --start-season 10
```

### Custom output directory:
```bash
python simpsons_scraper.py --output my_transcripts
```

### Adjust request delay (be respectful to the server):
```bash
python simpsons_scraper.py --delay 2.0
```

## Output Structure

```
transcripts/
├── season_01/
│   ├── s01e01_Simpsons_Roasting_on_an_Open_Fire.txt
│   ├── s01e02_Bart_the_Genius.txt
│   └── ...
├── season_02/
│   └── ...
```

## Options

- `--output, -o`: Output directory (default: transcripts)
- `--start-season, -s`: Start season (default: 1)
- `--end-season, -e`: End season (default: all available)
- `--delay, -d`: Delay between requests in seconds (default: 1.0)

## Notes

- The scraper includes rate limiting to be respectful to the server
- Failed downloads are logged and counted
- Transcripts are saved with metadata (title, season, episode, URL)
- File names are sanitized for cross-platform compatibility
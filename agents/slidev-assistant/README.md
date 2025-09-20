# Slidev Assistant

A PocketFlow-based AI assistant that generates professional Slidev presentations from simple text descriptions.

## Features

- 🎯 **Text-to-Presentation**: Convert simple text descriptions into full Slidev presentations
- 🔍 **Intelligent Research**: Automatically search and crawl web content for relevant information
- 🎨 **Custom Components**: Utilize nuclear hacker theme with Terminal and Warning components
- 🤖 **Agent-Based**: Smart research agent decides when to search, crawl, or generate
- 📊 **Full Slidev Support**: Leverages all Slidev capabilities including animations, layouts, and code highlighting

## Quick Start

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Install PocketFlow (if not available via pip)
pip install git+https://github.com/the-pocket/PocketFlow.git

# For web crawling, you may need playwright
python -m playwright install
```

### Basic Usage

```bash
# Generate presentation with research (full mode)
python main.py

# Generate presentation without research (faster)
python main.py --simple

# Custom input file
python main.py -i my_presentation.txt -o my_slides.md

# Debug mode
python main.py --debug --simple
```

## Input Format

Create a `presentation.txt` file with this structure:

```
Title: Your Presentation Title
Tone: funny, exaggerated
Content: Brief description of your presentation content

---

About 10 slides of your topic description
Slide1: Cover slide
Slide2: About me section
Slide3: Main content overview
Slide Last: Conclusion with Q&A
```

## Architecture

The system uses PocketFlow with the following workflow:

1. **ParseInputNode** - Parse presentation requirements
2. **LoadComponentsNode** - Extract custom components and Slidev capabilities
3. **ResearchAgentNode** - Intelligent research decisions
4. **SearchWebNode** - DuckDuckGo web searches
5. **CrawlWebNode** - Deep content extraction
6. **GenerateOutlineNode** - Structured presentation planning
7. **GenerateSlidesNode** - Final Slidev markdown generation

## Custom Components Available

- **Terminal** - Interactive terminal simulations with typing animations
- **Warning** - Security alert boxes (nuclear, danger, security, hack, info, warning)
- **Special CSS Classes** - radioactive, d-oh, glitch, cursor effects
- **Layouts** - terminal, intro, and all standard Slidev layouts

## Configuration

LLM settings in `assets/llm.env`:
```
api_key="your-api-key",
base_url="https://openrouter.ai/api/v1",
model="deepseek/deepseek-chat-v3.1:free"
```

## Examples

The system can generate presentations about:
- Technical topics with code examples
- AI/ML fails and security breaches
- Research topics with web-sourced content
- Educational content with interactive elements

## File Structure

```
slidev-assistant/
├── main.py                 # Entry point
├── flow.py                # Flow orchestration
├── nodes.py               # Node definitions
├── requirements.txt       # Dependencies
├── utils/
│   ├── call_llm.py       # LLM integration
│   ├── search_web.py     # DuckDuckGo search
│   ├── web_crawler.py    # Web crawling (existing)
│   └── parse_components.py # Component parsing
├── assets/
│   ├── presentation.txt   # Input example
│   ├── demo.md           # Custom components demo
│   ├── slides.md         # Standard Slidev capabilities
│   └── llm.env           # LLM configuration
└── docs/
    └── design.md         # Design documentation
```

## Development

The project follows PocketFlow patterns:
- **Agent Pattern** for intelligent research decisions
- **Workflow Pattern** for sequential processing
- **Utility Functions** for external integrations
- **Shared Store** for data communication between nodes

See `docs/design.md` for detailed architecture documentation.

## Troubleshooting

1. **Missing pocketflow**: Install from GitHub if not available via pip
2. **LLM errors**: Check `assets/llm.env` configuration
3. **Search errors**: Verify duckduckgo-search installation
4. **Crawl errors**: Install playwright browsers

## License

This project uses the PocketFlow framework and integrates with various AI services.

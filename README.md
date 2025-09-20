# Computer Kill Flanders in 2025

A comprehensive AI/Offensive Security research project exploring offensive AI use cases, featuring multiple specialized agents and a custom Slidev presentation theme.

## Project Overview

This project combines AI agents, data collection, and presentation systems into a unified offensive security research platform, themed around a "Computer Kill Flanders" cybersecurity narrative.

## Main Components

### 🤖 AI Agent Framework (`agents/`)

#### PocketFlow Template
- **Agentic Coding Framework**: 100-line LLM framework for building AI workflows
- **Multi-LLM Support**: OpenAI, Claude, local endpoints
- **Developer Tools**: Rules files for Cursor, Cline, Windsurf, Goose, GitHub Copilot
- **Quick Start**: `pip install -r requirements.txt`

#### Multi-MCP Agent
- **Multi-Server Support**: Connect to multiple MCP servers simultaneously using FastMCP
- **Standard Configuration**: Uses wellknown JSON format (Claude Desktop/VS Code compatible)
- **Diverse Server Types**: Supports npx, uvx, Docker/Podman-based MCP servers
- **Production Ready**: Zero async warnings, robust error handling, graceful degradation
- **Quick Start**: `python main_fastmcp.py`

#### Universal MCP-TAO Agent
- **TAO Pattern Implementation**: Thought-Action-Observation loop for complex reasoning
- **Universal Compatibility**: Works with any MCP servers across any domain
- **Async Architecture**: FastMCP-based for superior performance and reliability
- **Multi-Step Workflows**: Intelligent tool selection and execution chains
- **Quick Start**: `python main.py`

#### OSINT Agent
- **Autonomous IRC Integration**: Connects to IRC channels for natural language investigations
- **Comprehensive OSINT Tools**: 
  - Social media intelligence (500+ platforms via Maigret)
  - Network reconnaissance (DNS, WHOIS, port scanning)
  - Domain investigation and infrastructure analysis
- **Containerized Security**: Podman/Docker support with dynamic tool spawning
- **Quick Start**: `docker-compose up -d` or `make -f Makefile.podman up`

#### Slidev Assistant
- **AI-Powered Presentation Generation**: Converts text descriptions to full Slidev presentations
- **Intelligent Research**: Automatic web search and content crawling
- **Custom Components**: Nuclear hacker theme with Terminal and Warning components
- **Quick Start**: `python main.py`

### 📺 Simpsons Transcript Scraper (`simpsons-transcript-scraper/`)
- **Web Scraping**: Python scraper for Springfield! Springfield! transcripts
- **Extensive Collection**: 5 seasons (32-36) with 100+ episode transcripts
- **Rich Metadata**: Each transcript includes title, season, episode, and source URL
- **Quick Start**: `python simpsons_scraper.py`

### 🎨 Custom Slidev Theme & Presentation (`presentation/`)
- **slidev-theme-talk-simpsonsai**: Custom dark theme with nuclear/hacker aesthetics
- **Complete Presentation**: "Computer Kill Flanders in 2025" - Offensive AI use cases
- **Interactive Components**: 
  - Terminal simulations with typing animations
  - Security alert boxes (nuclear, danger, security, hack, info, warning)
  - Custom CSS effects (radioactive, d-oh, glitch, cursor)
- **Professional Assets**: 20+ custom images and graphics
- **Quick Start**: `npm run prod` or `npm run demo`

## Key Technical Features

### AI Capabilities
- **Multi-Agent Architecture**: Specialized agents for different tasks
- **Natural Language Processing**: Advanced LLM integration for intelligent responses
- **Autonomous Operations**: Self-directing agents with decision-making capabilities
- **Tool Integration**: Dynamic tool selection and execution

### Security & OSINT Tools
- **Network Analysis**: nmap, masscan, DNS utilities, WHOIS
- **Web Intelligence**: DuckDuckGo search, web crawling, content extraction
- **Social Media OSINT**: Maigret integration for 500+ platform searches
- **Container Security**: Isolated execution environments for safe tool usage

### Presentation System
- **Custom Theme Development**: Complete Slidev theme with custom layouts
- **Interactive Elements**: Vue.js components for dynamic presentations
- **Professional Design**: Dark theme optimized for technical presentations
- **Documentation**: Comprehensive guides for theme customization

## Project Structure

```
computer-kill-flanders-ai-2025/
├── agents/                          # AI agent implementations
│   ├── PocketFlow-Template-Python/  # Agentic coding framework
│   ├── PocketFlow/                  # MCP-based agents
│   │   ├── mcp/                     # Multi-MCP Agent (FastMCP-based)
│   │   └── mcp-tao/                 # Universal MCP-TAO Agent
│   ├── osint/                       # Autonomous OSINT IRC agent
│   └── slidev-assistant/            # AI presentation generator
├── simpsons-transcript-scraper/     # Episode transcript collection
├── presentation/                    # Custom Slidev theme & talk
├── .gitignore                       # Multi-language development ignore rules
└── README.md                        # This file
```

## License

This project is for educational and research purposes. Users are responsible for compliance with applicable laws and regulations.

## Support

For issues and questions:
- Check individual component README files
- Review documentation in `docs/` directories
- Examine configuration examples in `.env.example` files

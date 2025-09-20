# Autonomous OSINT IRC Agent 🕵️‍♂️

A fully autonomous OSINT (Open Source Intelligence) investigation agent that connects to IRC channels and conducts intelligent investigations through natural conversation. Built with the Agno framework for blazing-fast agent performance and comprehensive OSINT capabilities.

![OSINT Agent Demo](https://img.shields.io/badge/Demo-Ready-brightgreen) ![Docker](https://img.shields.io/badge/Docker-Supported-blue) ![Podman](https://img.shields.io/badge/Podman-Supported-orange) ![IRC](https://img.shields.io/badge/IRC-Compatible-purple)

## 🎯 Features

### 🤖 Autonomous AI Investigation
- **Natural Language Interface**: Just talk to the agent in plain English
- **Intelligent Tool Selection**: Agent automatically chooses the best tools for each investigation
- **Multi-step Reasoning**: Chains multiple investigation techniques together
- **Contextual Memory**: Remembers previous investigations and builds on findings
- **Real-time Analysis**: Provides comprehensive reports within seconds

### 🔍 OSINT Capabilities
- **Social Media Intelligence**: Username searches across 500+ platforms via Maigret
- **Network Reconnaissance**: DNS analysis, port scanning, SSL inspection, GeoIP lookup
- **Domain Investigation**: WHOIS lookups, subdomain discovery, web fingerprinting
- **Infrastructure Analysis**: HTTP headers, certificate inspection, service enumeration
- **Unlimited Tool Access**: Can install and use any OSINT tool within the container
- **Report Generation**: Creates structured investigation reports with actionable intelligence

### 💬 IRC Integration
- **Multi-channel Support**: Join multiple IRC channels simultaneously
- **Private Messages**: Direct investigation requests via PM
- **Channel Mentions**: Respond when mentioned in channels
- **Rate Limiting**: Intelligent message splitting for IRC compatibility
- **Command Interface**: Simple `!help` and `!investigate` commands
- **Persistent Connections**: Automatic reconnection and error handling

## 🏗️ System Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          🌐 IRC Network (irc.libera.chat)                       │
│                                   #osint-test                                   │
└─────────────────┬───────────────────────────────────────────────────────────────┘
                  │ IRC Protocol
                  ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           📦 Single Container Agent                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │                        🚀 main.py (Entry Point)                        │    │
│  │                     • Environment setup                                │    │
│  │                     • Configuration validation                         │    │
│  │                     • Logging initialization                           │    │
│  └─────────────────────────┬───────────────────────────────────────────────┘    │
│                            │                                                    │
│  ┌─────────────────────────▼───────────────────────────────────────────────┐    │
│  │                   🌐 irc_client.py (IRC Layer)                         │    │
│  │                     • IRC3 framework integration                       │    │
│  │                     • Connection management                             │    │
│  │                     • Channel/PM handling                               │    │
│  │                     • Plugin architecture                               │    │
│  └─────────────────────────┬───────────────────────────────────────────────┘    │
│                            │                                                    │
│  ┌─────────────────────────▼───────────────────────────────────────────────┐    │
│  │                 🔌 osint_plugin.py (Message Handler)                   │    │
│  │                     • Command parsing (!help, !investigate)            │    │
│  │                     • Message routing                                   │    │
│  │                     • Threading management                              │    │
│  │                     • Error handling                                    │    │
│  └─────────────────────────┬───────────────────────────────────────────────┘    │
│                            │                                                    │
│  ┌─────────────────────────▼───────────────────────────────────────────────┐    │
│  │                   🧠 agent.py (AI Brain)                               │    │
│  │                     • Agno framework integration                       │    │
│  │                     • LLM orchestration                                 │    │
│  │                     • Tool selection & execution                        │    │
│  │                     • Dynamic container spawning                        │    │
│  └─────────────────┬───────┬───────┬───────┬───────┬─────────────────────────┘    │
│                    │       │       │       │       │                            │
│     ┌──────────────▼─┐ ┌───▼───┐ ┌─▼───┐ ┌─▼───┐ ┌▼──────────────┐                 │
│     │🔧 shell_tool  │ │🔍 net │ │📁file│ │📦mai│ │⚡ Additional  │                 │
│     │               │ │work   │ │_tool │ │gret │ │Tools (Runtime)│                 │
│     │• Command exec │ │_tool  │ │      │ │_tool│ │               │                 │
│     │• Tool install │ │       │ │      │ │     │ │• theHarvester │                 │
│     │• System access│ │• DNS  │ │• R/W │ │•Cont│ │• Shodan       │                 │
│     └───────────────┘ │• WHOIS│ │• Logs│ │ainer│ │• Custom tools │                 │
│                       │• Ports│ │• Rpts│ │Spawn│ │• Go binaries  │                 │
│                       └───────┘ └──────┘ └─────┘ └───────────────┘                 │
│                                           │                                        │
│                                           ▼                                        │
│                               🐳 Dynamic Tool Containers                          │
│                               • soxoj/maigret:latest                               │
│                               • Custom OSINT containers                           │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
                         ┌──────────────▼──────────────┐
                         │    🌐 External Resources    │
                         │                             │
                         │ • LLM API (OpenAI/Claude)   │
                         │ • Agno Cloud Memory Service │
                         │ • OSINT Data Sources        │
                         │ • Network Infrastructure    │
                         └─────────────────────────────┘
```

### Data Flow Architecture

```
👤 User Message                                           📨 Investigation Report
    │                                                          ▲
    ▼                                                          │
┌─────────┐    ┌──────────────┐    ┌─────────────┐    ┌───────────────┐
│IRC Input├───►│Message Parser├───►│Agent Brain  ├───►│Response Formatter│
└─────────┘    └──────────────┘    └─────────────┘    └───────────────┘
                       │                   │
                       ▼                   ▼
              ┌─────────────────┐ ┌────────────────────┐
              │Command Validation│ │Tool Selection Logic│
              └─────────────────┘ └────────────────────┘
                                         │
                                         ▼
                   ┌────────────────────────────────────────┐
                   │           OSINT Tool Execution         │
                   │                                        │
                   │  Maigret ─── Network ─── File ─── Shell │
                   │     │          │         │        │    │
                   │     ▼          ▼         ▼        ▼    │
                   │  Social     DNS/Port  Reports  Custom  │
                   │  Media      Scanning   Gen.    Tools   │
                   └────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- **Docker**: Docker and Docker Compose **OR**
- **Podman**: Podman and podman-compose (see [README-PODMAN.md](README-PODMAN.md))
- IRC server access  
- OpenAI API key (or other supported LLM provider)

### Setup

1. **Clone and configure:**
   ```bash
   git clone <repository>
   cd osint
   cp .env.example .env
   # Edit .env with your IRC and API key settings
   ```

2. **Start the stack:**
   
   **Docker:**
   ```bash
   docker-compose up -d
   ```
   
   **Podman:**
   ```bash
   make -f Makefile.podman up
   ```

3. **Check logs:**
   
   **Docker:**
   ```bash
   docker-compose logs -f osint-agent
   ```
   
   **Podman:**
   ```bash
   make -f Makefile.podman logs
   ```

4. **Test the agent:**
   
   Join your configured IRC channel and try:
   ```
   !help
   !investigate username example_user
   !investigate domain example.com
   @OSINT-Agent check 1.1.1.1
   ```

### Environment Configuration

Edit `.env` file with your settings:

```bash
# IRC Configuration
IRC_SERVER=irc.libera.chat
IRC_PORT=6667
IRC_CHANNELS=#osint-test
IRC_NICK=OSINT-TestBot
IRC_SSL=false

# LLM Provider Configuration
LLM_PROVIDER=openai
LLM_MODEL=gpt-4
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_BASE_URL=http://127.0.0.1:4000  # For local LLM endpoints
```

## 🎮 Usage Examples

### Natural Conversation Interface

**Username Investigation:**
```
User: "Hey OSINT-Agent, can you investigate the username 'darkweb_trader'?"
Agent: 🔍 Starting comprehensive investigation of 'darkweb_trader'...
       
       📊 Investigation Report: Username 'darkweb_trader'
       
       🎯 Key Findings:
       • Primary account found with significant open-source activity
       • Repository themes: Security tools, OSINT projects, Python development
       • Twitter/X: Active account with security-related content
       • HackerOne: Bug bounty hunter profile with disclosed vulnerabilities
       • Keybase: Verified cryptographic identity with PGP keys
       
       🔍 Platform Distribution:
       4 major platforms - GitHub, Twitter/X, HackerOne, Keybase
       2 blogging/documentation platforms - 1 cryptocurrency-related service
       2 instant messaging platforms
       
       ⚡ Conclusion: You're looking at one of the most trusted public DNS services
       on the internet. Perfectly safe to use!
```

**Domain Analysis:**
```
User: "Check out suspicious-site.com, seems fishy"
Agent: 🔍 Analyzing suspicious-site.com for potential threats...
       
       📊 Investigation Report: suspicious-site.com
       
       🌍 Geographic Location:
       Country: United States, City: Los Angeles, Region: California
       Coordinates: 34.0522°N, 118.2437°W, ISP: Cloudflare Inc.
       
       🔍 Port Scan Results:
       - Port 53 (DNS) - OPEN ✅
       - Port 80 (HTTP) - OPEN ✅  
       - Port 443 (HTTPS) - OPEN ✅
       
       🔒 Security Headers: All properly configured with modern TLS and CSP
       📊 Service: Cloudflare's DNS service
       🎯 Threat Assessment: LEGITIMATE - No suspicious activities detected
```

**IP Investigation:**
```
User: "OSINT-Agent check 1.1.1.1"
Agent: 🔍 Investigating '1.1.1.1'...
       
       📊 Investigation Report: 1.1.1.1
       
       🌍 Geographic Location: Los Angeles, California (Cloudflare Inc.)
       🔍 Reverse DNS: one.one.one.one
       📊 Port Analysis: DNS (53), HTTP (80), HTTPS (443) - All legitimate services
       🔒 Security: Modern TLS, proper CSP configuration
       ⚡ Conclusion: Cloudflare's public DNS resolver - completely safe!
```

### IRC Commands

- **`!help`** - Show agent capabilities and usage
- **`!investigate <request>`** - Explicit investigation command
- **Private messages** - Any PM is treated as investigation request
- **Mentions** - "OSINT-Agent: check this domain example.com"

## 🛠️ Available Tools & Capabilities

### Pre-installed OSINT Arsenal
- **Network Tools**: nmap, masscan, dnsutils, whois, netcat, traceroute
- **Web Analysis**: curl, wget, openssl (SSL inspection)
- **Intelligence Gathering**: theHarvester, Shodan CLI
- **Social Media**: Maigret (500+ platform support)
- **Development**: git, jq, xmlstarlet, sqlite3
- **Text Processing**: Advanced parsing and correlation tools

### Autonomous Capabilities
- **Dynamic Tool Installation**: Agent can install any additional tools on demand
- **Custom Script Execution**: Can download and run specialized OSINT scripts
- **Go Binary Support**: Automatic compilation and execution of Go tools
- **Data Correlation**: Cross-references findings across multiple sources
- **Intelligence Reporting**: Generates structured, actionable reports
- **Pattern Recognition**: Identifies suspicious activities and correlations

### Tool Integration Examples

```python
# The agent can dynamically execute commands like:
dns_lookup("example.com")           # DNS resolution
whois_lookup("example.com")         # Domain registration info  
port_scan_basic("1.1.1.1")        # Network service enumeration
maigret_search("username")         # Social media investigation
geoip_lookup("8.8.8.8")          # Geographic location
http_headers("https://site.com")   # Web server fingerprinting
```

## 🔧 Development

### Project Structure
```
osint/
├── osint-agent/                 # Single-container OSINT agent
│   ├── src/
│   │   ├── main.py             # 🚀 Entry point & environment setup
│   │   ├── irc_client.py       # 🌐 IRC3 integration & connection mgmt
│   │   ├── osint_plugin.py     # 🔌 Message handling & command parsing
│   │   ├── agent.py            # 🧠 Agno AI agent & tool orchestration
│   │   └── tools/              # 🔧 OSINT tool implementations
│   │       ├── network_tool.py # DNS, WHOIS, port scanning
│   │       ├── maigret_tool.py # Dynamic Maigret container execution
│   │       ├── file_tool.py    # Report generation & file ops
│   │       └── shell_tool.py   # System access & tool installation
│   ├── Dockerfile.podman       # Container definition
│   └── requirements.txt        # Python dependencies
├── docker-compose.podman.yml   # Single-service orchestration
├── .env.example               # Configuration template
└── workspace/                 # Investigation workspace
```

### Component Interactions

1. **`main.py`** → Initializes environment and starts `irc_client.py`
2. **`irc_client.py`** → Creates IRC3 bot and loads `osint_plugin.py`
3. **`osint_plugin.py`** → Handles messages and delegates to `agent.py`
4. **`agent.py`** → Uses Agno framework to orchestrate OSINT tools
5. **`tools/*.py`** → Execute specific OSINT operations and return results

### Building & Testing

```bash
# Build entire stack
docker-compose -f docker-compose.podman.yml build

# Build with host networking (for local LLM endpoints)
podman run --rm --env-file .env --network host localhost/osint_osint-agent:latest

# View agent logs in real-time
podman logs -f <container_id>

# Shell access to agent container for debugging
podman exec -it <container_id> bash

# Test individual components
python -c "from tools.network_tool import dns_lookup; print(dns_lookup('example.com'))"
```

### Configuration for Local LLM Endpoints

For local OpenAI-compatible endpoints (like OpenRouter, Ollama, etc.):

```bash
# Use --network host flag for container networking
podman run --rm --env-file .env --network host localhost/osint_osint-agent:latest

# Or modify .env file:
OPENAI_BASE_URL=http://127.0.0.1:4000
OPENAI_API_KEY=sk-1234
```

## 🛡️ Security Considerations

- **Container Isolation**: All operations run within isolated container environment
- **Memory Management**: Agent uses Agno's cloud-based memory system for secure storage
- **Investigation Logging**: All activities logged for audit and forensic purposes  
- **Rate Limiting**: IRC message rate limiting prevents channel flooding
- **Ethical Usage**: Designed exclusively for legitimate OSINT research
- **Tool Safety**: Pre-installed tools are security-focused and non-malicious

## 🎪 Demo Usage for Talks

Perfect for demonstrating:
- **Autonomous AI in Action**: Real-time AI reasoning and tool selection
- **Advanced OSINT Techniques**: Professional-grade digital investigation methods
- **Human-AI Collaboration**: Natural language interface for complex tasks
- **Container Security**: Secure execution environment for security tools
- **Cross-platform Intelligence**: Multi-source information correlation

## 🔧 Troubleshooting

### Common Issues

1. **Agent won't connect to IRC:**
   ```bash
   # Check configuration
   cat .env | grep IRC_
   
   # Test network connectivity
   podman run --rm alpine nc -zv irc.libera.chat 6667
   ```

2. **LLM API errors:**
   ```bash
   # Verify API key configuration
   echo $OPENAI_API_KEY | cut -c1-10
   
   # Test API endpoint
   curl -H "Authorization: Bearer $OPENAI_API_KEY" $OPENAI_BASE_URL/models
   ```

3. **Local LLM endpoint connectivity:**
   ```bash
   # Use host networking for local endpoints
   podman run --rm --env-file .env --network host <image>
   
   # Test endpoint from container
   podman run --rm --network host curlimages/curl:latest curl -s http://127.0.0.1:4000/health
   ```

4. **Container networking issues:**
   ```bash
   # Check container logs
   podman logs -f <container_name>
   
   # Inspect network configuration
   podman inspect <container_name> | jq '.[].NetworkSettings'
   ```

### Debug Commands

```bash
# Check all running containers
podman ps -a

# View comprehensive agent logs
podman logs --follow --timestamps osint-agent

# Test IRC connectivity manually
telnet irc.libera.chat 6667

# Verify environment variables
podman exec osint-agent env | grep -E "(IRC|LLM|OPENAI)"

# Monitor resource usage
podman stats osint-agent

# Shell access for interactive debugging
podman exec -it osint-agent /bin/bash
```

## 📊 Performance & Monitoring

- **Investigation Speed**: Typical investigations complete in 5-15 seconds
- **Memory Usage**: ~200-500MB depending on active investigations
- **Network Usage**: Minimal, only for IRC and API calls
- **Storage**: Investigation reports stored in persistent workspace volume
- **Concurrent Users**: Supports multiple simultaneous IRC users

## 🚀 Future Enhancements

- [ ] Web UI dashboard for investigation management
- [ ] Integration with additional OSINT platforms
- [ ] Advanced correlation and timeline analysis
- [ ] Automated threat intelligence feeds
- [ ] Multi-language investigation support
- [ ] Custom investigation workflow templates

---

**⚠️ Legal Notice**: This tool is designed for legitimate OSINT research, security assessment, and educational purposes only. Users are responsible for compliance with applicable laws and regulations.

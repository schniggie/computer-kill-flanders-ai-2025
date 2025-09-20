# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an OSINT (Open Source Intelligence) project containing the **mcp-maigret** MCP (Model Context Protocol) server. This server integrates the powerful [maigret](https://github.com/soxoj/maigret) OSINT tool with MCP-compatible applications like Claude Desktop to enable username searches across social networks and URL analysis.

## Core Architecture

The project consists of a single Node.js/TypeScript MCP server (`mcp-maigret/`) that:

- **Docker Integration**: Uses the `soxoj/maigret:latest` Docker image to run maigret securely
- **MCP Protocol**: Implements the Model Context Protocol server using `@modelcontextprotocol/sdk`
- **Two Main Tools**:
  - `search_username`: Search for usernames across social networks
  - `parse_url`: Analyze URLs to extract usernames and information
- **Report Generation**: Supports multiple output formats (txt, html, pdf, json, csv, xmind)
- **Environment Configuration**: Requires `MAIGRET_REPORTS_DIR` environment variable

## Development Commands

```bash
# Install dependencies
npm install

# Build the TypeScript code
npm run build

# Publish to npm (runs build automatically)
npm run prepublishOnly
```

## Key Components

### Main Server (`src/index.ts`)
- `MaigretServer` class handles MCP protocol and Docker execution
- Type guards ensure parameter validation (`isSearchUsernameArgs`, `isParseUrlArgs`)
- Docker commands are executed with proper volume mounting for report output
- Error handling for Docker and environment setup

### Docker Requirements
- Docker must be installed and running
- The server automatically pulls `soxoj/maigret:latest` if not present
- Reports directory must exist and be writable

### Environment Setup
- `MAIGRET_REPORTS_DIR`: Required environment variable for report output location
- The server creates the reports directory if it doesn't exist

## Testing and Validation

Before deploying changes:
1. Ensure Docker is available and the maigret image can be pulled
2. Test with valid MAIGRET_REPORTS_DIR environment variable
3. Verify both tools work with sample data

## Security Considerations

This tool is designed for legitimate OSINT research:
- Only searches publicly available information
- Respects rate limits and platform terms of service
- Docker isolation provides security boundary
- Filename sanitization prevents path traversal

## Installation Methods

- Global npm install: `npm install -g mcp-maigret`
- Smithery installation: `npx -y @smithery/cli install mcp-maigret --client claude`
- Development from source: Clone, build, and configure manually
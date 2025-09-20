# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Slidev theme called "talk-simpsonsai" - a custom theme for creating presentation slides. Slidev is a presentation framework for developers that uses Markdown files to create slides with Vue.js components and TypeScript support.

## Development Commands

- `npm run dev` - Start development server with example.md slides (opens automatically)
- `npm run prod` - Start development server with slides.md (main presentation file)
- `npm run build` - Build the presentation from example.md for production
- `npm run export` - Export example.md slides to PDF
- `npm run screenshot` - Export example.md slides to PNG format

## Theme Architecture

### Core Structure
- `layouts/` - Vue layout components for different slide types (cover.vue, intro.vue)
- `components/` - Reusable Vue components (currently empty - uses .gitkeep)  
- `styles/` - CSS styling with index.ts (imports base styles + layout.css)
- `setup/` - Theme configuration, including shiki.ts for syntax highlighting themes

### Key Files
- `example.md` - Theme demo/preview slides used for development
- `slides.md` - Main presentation file used in production
- `styles/layout.css` - Custom CSS with theme-specific styling and CSS variables
- `setup/shiki.ts` - Code syntax highlighting configuration (vitesse-dark/light themes)

### Theme Configuration
The theme inherits from Slidev's base layouts and adds custom styling. It uses:
- Primary color: `--slidev-theme-primary: #5d8392`
- Fonts: Nunito Sans (sans), Fira Code (mono)
- Color schema: supports both light and dark modes
- Code highlighting: Vitesse themes for light/dark modes

### Slide Files
Both example.md and slides.md use frontmatter with `theme: ./` to reference the local theme. The slides support standard Slidev features including layouts, transitions, and Vue components.
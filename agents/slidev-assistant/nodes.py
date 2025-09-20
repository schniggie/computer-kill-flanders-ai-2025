import os
import re
import yaml
import json
import logging
from pocketflow import Node

from utils.call_llm import call_llm
from utils.search_web import search_web
from utils.web_crawler import crawl_webpage
from utils.parse_components import parse_components

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ParseInputNode(Node):
    """Parse presentation requirements from input text file"""

    def prep(self, shared):
        input_file = shared.get("input_file", "assets/presentation.txt")
        return input_file

    def exec(self, input_file):
        try:
            # Read the input file
            with open(input_file, 'r', encoding='utf-8') as f:
                raw_content = f.read().strip()

            # Use LLM to intelligently parse the presentation requirements
            prompt = f"""
You are an expert at parsing presentation requirements from text files.

Parse the following presentation requirement text and extract:
1. Title - the presentation title
2. Tone - the presentation tone/style
3. Content - main content description
4. Slides - any specific slide requests with their descriptions

The input text might have various formats - some fields might be missing, content might span multiple lines, slide descriptions might be in different formats. Extract the information intelligently.

INPUT TEXT:
{raw_content}

Return the parsed information as structured YAML:

```yaml
presentation:
  title: "Extracted presentation title"
  tone: "Extracted tone/style"
  content: "Main content description"
  estimated_slides: 15  # estimate based on content and requirements

slides:
  - number: "Slide1"
    description: "Cover slide description"
  - number: "Slide2"
    description: "About me section"
  # ... continue for all mentioned slides

additional_info:
  special_requests: "Any special requirements mentioned"
  target_audience: "Inferred audience if mentioned"
```

Guidelines:
- If title is missing, create a descriptive one based on content
- If tone is missing, infer from content style
- If content spans multiple lines, consolidate intelligently
- Extract all slide requests, normalizing the format
- Estimate total slides needed based on content complexity and specific requests
- If specific slides are mentioned (e.g., "Slide1", "Slide2", etc.), count them and add buffer slides
- For presentations about "AI fails" or technical content, estimate 15-20 slides
- Include any special instructions or requests
"""

            response = call_llm(prompt)

            # Parse YAML response
            try:
                yaml_match = re.search(r'```yaml\n(.*?)\n```', response, re.DOTALL)
                if yaml_match:
                    yaml_content = yaml_match.group(1)
                    parsed_data = yaml.safe_load(yaml_content)

                    # Transform to expected format for compatibility
                    result = {
                        "title": parsed_data.get("presentation", {}).get("title", "Untitled Presentation"),
                        "tone": parsed_data.get("presentation", {}).get("tone", "professional"),
                        "content": parsed_data.get("presentation", {}).get("content", ""),
                        "estimated_slides": parsed_data.get("presentation", {}).get("estimated_slides", 15),
                        "slides": [],
                        "additional_info": parsed_data.get("additional_info", {})
                    }

                    # Convert slides format
                    for slide in parsed_data.get("slides", []):
                        result["slides"].append({
                            "number": slide.get("number", ""),
                            "description": slide.get("description", "")
                        })

                    logger.info(f"LLM successfully parsed presentation: '{result['title']}' with {len(result['slides'])} specific slides")
                    return result

                else:
                    raise ValueError("Could not find YAML block in LLM response")

            except Exception as e:
                logger.error(f"Error parsing LLM YAML response: {e}")
                logger.debug(f"LLM Response: {response}")
                # Fall back to simple parsing if LLM fails
                return self._fallback_parse(raw_content)

        except Exception as e:
            logger.error(f"Error in LLM-based parsing: {e}")
            # Return default structure
            return {
                "title": "AI Fails Presentation",
                "tone": "funny, exaggerated",
                "content": "Latest AI and LLM fails",
                "estimated_slides": 15,
                "slides": [{"number": "Slide1", "description": "Cover slide"}],
                "additional_info": {}
            }

    def _fallback_parse(self, raw_content):
        """Fallback to simple string parsing if LLM fails"""
        logger.info("Using fallback string parsing")

        lines = raw_content.split('\n')
        parsed = {
            "title": "",
            "tone": "",
            "content": "",
            "estimated_slides": 15,
            "slides": [],
            "additional_info": {}
        }

        for line in lines:
            line = line.strip()
            if not line or line.startswith('---'):
                continue

            # Look for key-value pairs
            if line.lower().startswith('title:'):
                parsed["title"] = line.split(':', 1)[1].strip()
            elif line.lower().startswith('tone:'):
                parsed["tone"] = line.split(':', 1)[1].strip()
            elif line.lower().startswith('content:'):
                parsed["content"] = line.split(':', 1)[1].strip()
            elif line.lower().startswith('slide'):
                slide_info = line.split(':', 1)
                if len(slide_info) == 2:
                    slide_num = slide_info[0].strip()
                    slide_desc = slide_info[1].strip()
                    parsed["slides"].append({"number": slide_num, "description": slide_desc})
            else:
                # Continuation of content
                if parsed["content"]:
                    parsed["content"] += " " + line
                else:
                    parsed["content"] = line

        # Set defaults if missing
        if not parsed["title"]:
            parsed["title"] = "Presentation"
        if not parsed["tone"]:
            parsed["tone"] = "professional"
        if not parsed["content"]:
            parsed["content"] = "No content description provided"

        return parsed

    def post(self, shared, prep_res, exec_res):
        shared["input"] = exec_res
        logger.info(f"Parsed presentation: {exec_res['title']} ({exec_res['tone']})")
        return "default"

class LoadComponentsNode(Node):
    """Load available components and Slidev capabilities"""

    def prep(self, shared):
        demo_file = shared.get("demo_file", "assets/demo.md")
        slides_file = shared.get("slides_file", "assets/slides.md")
        return (demo_file, slides_file)

    def exec(self, file_paths):
        demo_file, slides_file = file_paths

        try:
            # Read demo.md and slides.md
            with open(demo_file, 'r', encoding='utf-8') as f:
                demo_content = f.read()

            with open(slides_file, 'r', encoding='utf-8') as f:
                slides_content = f.read()

            # Use LLM to intelligently analyze the components and capabilities
            prompt = f"""
You are an expert at analyzing Slidev presentation files to extract custom components and standard capabilities.

Analyze the following two files:

1. DEMO FILE (custom components and theme examples):
---
{demo_content[:8000]}  # Truncate for token limits
---

2. SLIDES FILE (standard Slidev capabilities):
---
{slides_content[:8000]}  # Truncate for token limits
---

Extract and analyze:
1. Custom components with their properties and usage examples
2. Standard Slidev capabilities and features
3. CSS classes and styling options
4. Available layouts and transitions
5. Integration recommendations

Return the analysis as structured YAML:

```yaml
custom_components:
  - name: "Terminal"
    type: "interactive"
    description: "Interactive terminal simulation with typing animations"
    props:
      - name: "title"
        description: "Terminal window title"
        example: "Homer's Lab"
      - name: "user"
        description: "Username in prompt"
        example: "homer"
      - name: "height"
        description: "Terminal height"
        example: "300px"
    usage_examples:
      - "<Terminal title='My Terminal' user='admin' height='200px' />"
    best_practices: "Use for code demonstrations and command line examples"

  - name: "Warning"
    type: "alert"
    description: "Security alert boxes with various types"
    props:
      - name: "type"
        description: "Alert type"
        options: ["nuclear", "danger", "security", "hack", "info", "warning"]
      - name: "title"
        description: "Alert title"
      - name: "level"
        description: "Alert severity level"
        example: "5"
    usage_examples:
      - "<Warning type='nuclear' title='ALERT' level='5'>Content</Warning>"
    best_practices: "Use for important announcements and warnings"

css_classes:
  - name: "radioactive"
    description: "Glowing nuclear green effect"
    usage: "class='radioactive'"
  - name: "d-oh"
    description: "Homer's signature yellow glow"
    usage: "class='d-oh'"

layouts:
  - name: "terminal"
    description: "Full-screen terminal layout with CRT effects"
  - name: "intro"
    description: "Clean intro layout for section breaks"

slidev_capabilities:
  animations:
    - "v-click for click animations"
    - "v-motion for motion animations"
  code_highlighting:
    - "syntax highlighting for multiple languages"
    - "line highlighting and focus"
  diagrams:
    - "Mermaid diagram support"
    - "PlantUML diagram support"
  interactive:
    - "Monaco editor integration"
    - "Interactive Vue components"
  layouts:
    - "Multiple built-in layouts (center, two-cols, image-right)"
  math:
    - "LaTeX mathematical expressions with KaTeX"

theme_integration:
  primary_colors: ["nuclear green", "danger red", "Simpson yellow"]
  styling_approach: "Dark theme with hacker/nuclear aesthetics"
  recommended_usage: "Best for security presentations and technical demos"
```

Guidelines:
- Extract ALL custom components you find
- Include comprehensive prop information
- Provide realistic usage examples
- Identify styling patterns and CSS classes
- Categorize standard Slidev capabilities
- Give integration recommendations
"""

            response = call_llm(prompt)

            # Parse YAML response
            try:
                yaml_match = re.search(r'```yaml\n(.*?)\n```', response, re.DOTALL)
                if yaml_match:
                    yaml_content = yaml_match.group(1)
                    parsed_data = yaml.safe_load(yaml_content)

                    # Transform to expected format for compatibility
                    result = {
                        'available_components': [],
                        'slidev_capabilities': self._format_capabilities(parsed_data),
                        'css_classes': parsed_data.get('css_classes', []),
                        'layouts': parsed_data.get('layouts', []),
                        'theme_integration': parsed_data.get('theme_integration', {})
                    }

                    # Transform custom components to expected format
                    for component in parsed_data.get('custom_components', []):
                        comp_data = {
                            'name': component.get('name', ''),
                            'type': component.get('type', ''),
                            'description': component.get('description', ''),
                            'props': component.get('props', []),
                            'usage_examples': component.get('usage_examples', []),
                            'best_practices': component.get('best_practices', '')
                        }
                        result['available_components'].append(comp_data)

                    logger.info(f"LLM successfully analyzed {len(result['available_components'])} custom components")
                    return result

                else:
                    raise ValueError("Could not find YAML block in LLM response")

            except Exception as e:
                logger.error(f"Error parsing LLM YAML response: {e}")
                logger.debug(f"LLM Response: {response}")
                # Fall back to original parsing if LLM fails
                return self._fallback_parse(demo_content, slides_content)

        except Exception as e:
            logger.error(f"Error in LLM-based component analysis: {e}")
            return {
                'available_components': [],
                'slidev_capabilities': 'Basic Slidev functionality with code highlighting and animations'
            }

    def _format_capabilities(self, parsed_data):
        """Format Slidev capabilities into a readable string"""
        try:
            capabilities = []

            slidev_caps = parsed_data.get('slidev_capabilities', {})

            if slidev_caps.get('animations'):
                capabilities.append("Animations: " + ", ".join(slidev_caps['animations']))

            if slidev_caps.get('code_highlighting'):
                capabilities.append("Code Highlighting: " + ", ".join(slidev_caps['code_highlighting']))

            if slidev_caps.get('diagrams'):
                capabilities.append("Diagrams: " + ", ".join(slidev_caps['diagrams']))

            if slidev_caps.get('interactive'):
                capabilities.append("Interactive: " + ", ".join(slidev_caps['interactive']))

            if slidev_caps.get('layouts'):
                capabilities.append("Layouts: " + ", ".join(slidev_caps['layouts']))

            if slidev_caps.get('math'):
                capabilities.append("Math: " + ", ".join(slidev_caps['math']))

            return "\n".join([f"- {cap}" for cap in capabilities])

        except Exception as e:
            logger.error(f"Error formatting capabilities: {e}")
            return "Standard Slidev capabilities including animations, code highlighting, and layouts"

    def _fallback_parse(self, demo_content, slides_content):
        """Fallback to original parsing if LLM fails"""
        logger.info("Using fallback component parsing")

        try:
            # Use the original parse_components utility as fallback
            components_data = parse_components(demo_content, slides_content)
            return components_data
        except Exception as e:
            logger.error(f"Fallback parsing also failed: {e}")
            return {
                'available_components': [],
                'slidev_capabilities': 'Basic Slidev functionality'
            }

    def post(self, shared, prep_res, exec_res):
        shared["components"] = exec_res
        logger.info(f"Loaded {len(exec_res['available_components'])} components")
        return "default"

class ResearchAgentNode(Node):
    """Intelligent agent that decides whether to search, crawl, or generate"""

    def __init__(self, max_retries=2, wait=1):
        super().__init__(max_retries, wait)
        self.search_count = 0
        self.crawl_count = 0

    def prep(self, shared):
        input_data = shared.get("input", {})
        research_data = shared.get("research", {
            "search_results": [],
            "crawled_content": {},
            "research_complete": False
        })

        return {
            "title": input_data.get("title", ""),
            "content": input_data.get("content", ""),
            "tone": input_data.get("tone", ""),
            "slides": input_data.get("slides", []),
            "search_results": research_data.get("search_results", []),
            "crawled_content": research_data.get("crawled_content", {}),
            "search_count": len(research_data.get("search_results", [])),
            "crawl_count": len(research_data.get("crawled_content", {}))
        }

    def exec(self, context):
        try:
            # Build decision context
            prompt = f"""
You are a research agent helping create a Slidev presentation about: "{context['title']}"
Content focus: {context['content']}
Tone: {context['tone']}

Current research status:
- Search results: {context['search_count']} searches completed
- Crawled pages: {context['crawl_count']} pages crawled
- Slide requests: {len(context['slides'])} specific slides requested

Based on this context, decide the next action:

1. SEARCH - If you need more information about the topic (max 3 searches)
2. CRAWL - If search results contain promising URLs to get detailed content (max 2 crawls)
3. GENERATE - If you have enough information to create the presentation

Guidelines:
- For technical/recent topics, do at least 1-2 searches
- For controversial/current events topics, search for latest information
- If you have good search results with relevant URLs, crawl 1-2 key pages
- Don't over-research - generate when you have sufficient context

Return your decision as YAML:

```yaml
thinking: |
  Your reasoning process here
action: search/crawl/generate
search_query: "search terms here" (only if action is search)
crawl_url: "https://example.com" (only if action is crawl)
reason: Brief explanation of why this action
```
            """

            response = call_llm(prompt)

            # Parse YAML response
            try:
                yaml_match = re.search(r'```yaml\n(.*?)\n```', response, re.DOTALL)
                if yaml_match:
                    yaml_content = yaml_match.group(1)
                    decision = yaml.safe_load(yaml_content)
                else:
                    # Fallback parsing
                    decision = {"action": "generate", "reason": "Could not parse decision"}

            except Exception as e:
                logger.error(f"Error parsing agent decision: {e}")
                decision = {"action": "generate", "reason": "Parsing error - proceeding to generate"}

            # Validate decision
            if decision.get("action") not in ["search", "crawl", "generate"]:
                decision["action"] = "generate"

            # Safety limits
            if decision["action"] == "search" and context["search_count"] >= 3:
                decision["action"] = "generate"
                decision["reason"] = "Search limit reached"

            if decision["action"] == "crawl" and context["crawl_count"] >= 2:
                decision["action"] = "generate"
                decision["reason"] = "Crawl limit reached"

            logger.info(f"Agent decision: {decision['action']} - {decision.get('reason', '')}")
            return decision

        except Exception as e:
            logger.error(f"Error in research agent: {e}")
            return {"action": "generate", "reason": "Error occurred - proceeding to generate"}

    def post(self, shared, prep_res, exec_res):
        # Store the decision for other nodes to use
        shared["agent_decision"] = exec_res

        # Update research completion status
        if "research" not in shared:
            shared["research"] = {
                "search_results": [],
                "crawled_content": {},
                "research_complete": False
            }

        if exec_res["action"] == "generate":
            shared["research"]["research_complete"] = True

        return exec_res["action"]

class SearchWebNode(Node):
    """Perform web searches based on agent decisions"""

    def prep(self, shared):
        agent_decision = shared.get("agent_decision", {})
        search_query = agent_decision.get("search_query", "")
        return search_query

    def exec(self, search_query):
        if not search_query:
            return []

        try:
            # Perform search
            results = search_web(search_query, max_results=5)
            logger.info(f"Found {len(results)} search results for: {search_query}")
            return results
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

    def post(self, shared, prep_res, exec_res):
        if "research" not in shared:
            shared["research"] = {"search_results": [], "crawled_content": {}}

        # Add new results to existing ones
        shared["research"]["search_results"].extend(exec_res)
        logger.info(f"Total search results: {len(shared['research']['search_results'])}")
        return "research"  # Go back to research agent

class CrawlWebNode(Node):
    """Crawl specific URLs for detailed content"""

    def prep(self, shared):
        agent_decision = shared.get("agent_decision", {})
        crawl_url = agent_decision.get("crawl_url", "")

        # If no specific URL, pick from recent search results
        if not crawl_url:
            search_results = shared.get("research", {}).get("search_results", [])
            if search_results:
                # Take the first uncrawled URL from recent results
                crawled_urls = set(shared.get("research", {}).get("crawled_content", {}).keys())
                for result in search_results:
                    url = result.get("link", "")
                    if url and url not in crawled_urls:
                        crawl_url = url
                        break

        return crawl_url

    def exec(self, crawl_url):
        if not crawl_url:
            return ("", [])

        try:
            content, links = crawl_webpage(crawl_url, delay_after_load=2)
            logger.info(f"Crawled {len(content)} characters from {crawl_url}")
            return (content, links)
        except Exception as e:
            logger.error(f"Crawl error for {crawl_url}: {e}")
            return ("", [])

    def post(self, shared, prep_res, exec_res):
        url = prep_res
        content, links = exec_res

        if url and content:
            if "research" not in shared:
                shared["research"] = {"search_results": [], "crawled_content": {}}

            shared["research"]["crawled_content"][url] = {
                "content": content,
                "links": links[:10]  # Store up to 10 links
            }

        return "research"  # Go back to research agent

class GenerateOutlineNode(Node):
    """Generate structured presentation outline"""

    def prep(self, shared):
        return {
            "input": shared.get("input", {}),
            "research": shared.get("research", {}),
            "components": shared.get("components", {})
        }

    def exec(self, data):
        try:
            input_data = data["input"]
            research_data = data["research"]
            components_data = data["components"]

            # Prepare research context
            research_context = ""
            if research_data.get("search_results"):
                research_context += "Search Results:\n"
                for result in research_data["search_results"]:
                    research_context += f"- {result.get('title', '')}: {result.get('snippet', '')}\n"

            if research_data.get("crawled_content"):
                research_context += "\nDetailed Content:\n"
                for url, content_data in research_data["crawled_content"].items():
                    content = content_data.get("content", "")[:500]  # First 500 chars
                    research_context += f"- {url}: {content}...\n"

            # Prepare components context
            components_context = ""
            for comp in components_data.get("available_components", []):
                components_context += f"- {comp['name']} ({comp['type']}): {comp['description']}\n"

            prompt = f"""
Create a detailed outline for a Slidev presentation with these requirements:

PRESENTATION DETAILS:
Title: {input_data.get('title', '')}
Tone: {input_data.get('tone', '')}
Content Focus: {input_data.get('content', '')}

SPECIFIC SLIDE REQUESTS:
{chr(10).join([f"- {slide['number']}: {slide['description']}" for slide in input_data.get('slides', [])])}

RESEARCH CONTEXT:
{research_context}

AVAILABLE CUSTOM COMPONENTS:
{components_context}

SLIDEV CAPABILITIES:
{components_data.get('slidev_capabilities', '')}

Create a detailed presentation outline that:
1. Uses the specified tone and style
2. Incorporates research findings
3. Leverages available custom components appropriately
4. Follows good presentation structure
5. Addresses ALL the specific slide requests listed above
6. Creates {input_data.get('estimated_slides', 15)} total slides (use this exact number)
7. If more slides are requested than estimated, expand to cover all requests

Return the outline as YAML:

```yaml
presentation:
  title: "Final title"
  theme: "nuclear/hacker theme or default"
  total_slides: {input_data.get('estimated_slides', 15)}  # Use estimated count from input

slides:
  - number: 1
    type: "cover"
    title: "Slide title"
    content_description: "What this slide contains"
    components_used: ["Terminal", "Warning"]
    layout: "cover"

  - number: 2
    type: "content"
    title: "Slide title"
    content_description: "Detailed description"
    components_used: []
    layout: "default"

  # ... continue for ALL slides based on estimated_slides count
```
            """

            response = call_llm(prompt)

            # Parse YAML response
            try:
                yaml_match = re.search(r'```yaml\n(.*?)\n```', response, re.DOTALL)
                if yaml_match:
                    yaml_content = yaml_match.group(1)
                    outline = yaml.safe_load(yaml_content)
                else:
                    # Create basic outline if parsing fails
                    estimated_slides = input_data.get("estimated_slides", 15)
                    outline = {
                        "presentation": {
                            "title": input_data.get("title", "Presentation"),
                            "theme": "default",
                            "total_slides": estimated_slides
                        },
                        "slides": [
                            {"number": i+1, "type": "content", "title": f"Slide {i+1}", "content_description": "Content slide"}
                            for i in range(estimated_slides)
                        ]
                    }
                    # Make first slide a cover
                    if outline["slides"]:
                        outline["slides"][0] = {"number": 1, "type": "cover", "title": "Cover", "content_description": "Introduction"}
            except Exception as e:
                logger.error(f"Error parsing outline: {e}")
                outline = {"presentation": {"title": "Error"}, "slides": []}

            return outline

        except Exception as e:
            logger.error(f"Error generating outline: {e}")
            return {"error": str(e)}

    def post(self, shared, prep_res, exec_res):
        shared["generated"] = {"outline": exec_res}
        logger.info(f"Generated outline with {len(exec_res.get('slides', []))} slides")
        return "default"

class GenerateSlidesNode(Node):
    """Generate final Slidev markdown presentation"""

    def prep(self, shared):
        return {
            "outline": shared.get("generated", {}).get("outline", {}),
            "input": shared.get("input", {}),
            "research": shared.get("research", {}),
            "components": shared.get("components", {})
        }

    def exec(self, data):
        try:
            outline = data["outline"]
            input_data = data["input"]
            research_data = data["research"]
            components_data = data["components"]

            # Build component reference
            component_examples = ""
            for comp in components_data.get("available_components", []):
                if comp.get("usage"):
                    component_examples += f"{comp['name']}:\n{comp['usage']}\n\n"

            # Build research summary
            research_summary = ""
            search_results = research_data.get("search_results", [])[:3]  # Top 3 results
            for result in search_results:
                research_summary += f"- {result.get('title', '')}\n"

            prompt = f"""
Generate a complete Slidev presentation markdown file based on this outline:

OUTLINE:
{json.dumps(outline, indent=2)}

ORIGINAL REQUIREMENTS:
Title: {input_data.get('title', '')}
Tone: {input_data.get('tone', '')}
Content: {input_data.get('content', '')}

RESEARCH CONTEXT (incorporate relevant information):
{research_summary}

AVAILABLE CUSTOM COMPONENTS AND EXAMPLES:
{component_examples}

SLIDEV CAPABILITIES:
{components_data.get('slidev_capabilities', '')}

Generate a complete Slidev markdown file that:
1. Starts with proper frontmatter (theme, title, etc.)
2. Implements all slides from the outline
3. Uses appropriate custom components where beneficial
4. Maintains the specified tone throughout
5. Incorporates research findings naturally
6. Uses proper Slidev syntax and features
7. Includes engaging content that matches the tone

Important:
- Use --- to separate slides
- Include proper frontmatter at the start
- Use custom components like <Terminal> and <Warning> where appropriate
- Include code examples and interactive elements
- Make it engaging and match the specified tone

Return ONLY the complete Slidev markdown content, no additional text or explanations.
            """

            response = call_llm(prompt)

            # Clean up the response to ensure it's proper markdown
            if response.startswith("```"):
                # Remove code block markers if present
                lines = response.split('\n')
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines[-1].startswith("```"):
                    lines = lines[:-1]
                response = '\n'.join(lines)

            return response.strip()

        except Exception as e:
            logger.error(f"Error generating slides: {e}")
            return f"""---
theme: default
title: Error Generating Slides
---

# Error

There was an error generating the presentation: {str(e)}

Please check the logs and try again.
"""

    def post(self, shared, prep_res, exec_res):
        if "generated" not in shared:
            shared["generated"] = {}

        shared["generated"]["slides"] = exec_res
        logger.info(f"Generated complete Slidev presentation ({len(exec_res)} characters)")

        # Write the slides to a file
        output_file = "generated_presentation.md"
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(exec_res)
            logger.info(f"Saved presentation to {output_file}")
        except Exception as e:
            logger.error(f"Error saving presentation file: {e}")

        return "default"
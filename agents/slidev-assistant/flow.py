from pocketflow import Flow
from nodes import (
    ParseInputNode,
    LoadComponentsNode,
    ResearchAgentNode,
    SearchWebNode,
    CrawlWebNode,
    GenerateOutlineNode,
    GenerateSlidesNode
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_slidev_assistant_flow():
    """
    Create and return the complete Slidev Assistant flow.

    Flow structure:
    1. Parse input requirements
    2. Load available components
    3. Research agent (with search/crawl loop)
    4. Generate outline
    5. Generate slides
    """

    # Create all nodes
    parse_input = ParseInputNode()
    load_components = LoadComponentsNode()
    research_agent = ResearchAgentNode(max_retries=2, wait=1)
    search_web = SearchWebNode()
    crawl_web = CrawlWebNode()
    generate_outline = GenerateOutlineNode()
    generate_slides = GenerateSlidesNode()

    logger.info("Creating Slidev Assistant flow with agent-based research")

    # Define the main flow sequence
    parse_input >> load_components >> research_agent

    # Research agent branching:
    # - "search" -> search web -> back to research agent
    # - "crawl" -> crawl web -> back to research agent
    # - "generate" -> generate outline -> generate slides
    research_agent - "search" >> search_web
    research_agent - "crawl" >> crawl_web
    research_agent - "generate" >> generate_outline

    # Search and crawl nodes loop back to research agent
    search_web - "research" >> research_agent
    crawl_web - "research" >> research_agent

    # Final generation sequence
    generate_outline >> generate_slides

    # Create the main flow starting with parse_input
    flow = Flow(start=parse_input)

    logger.info("Slidev Assistant flow created successfully")
    return flow

def create_simple_flow():
    """
    Create a simplified flow that skips research for testing purposes.
    """

    parse_input = ParseInputNode()
    load_components = LoadComponentsNode()
    generate_outline = GenerateOutlineNode()
    generate_slides = GenerateSlidesNode()

    # Simple linear flow without research
    parse_input >> load_components >> generate_outline >> generate_slides

    flow = Flow(start=parse_input)
    logger.info("Simple Slidev Assistant flow created (no research)")
    return flow

if __name__ == "__main__":
    # Test the flow creation
    print("Testing flow creation...")

    try:
        # Create the main flow
        main_flow = create_slidev_assistant_flow()
        print("✓ Main flow created successfully")

        # Create the simple flow
        simple_flow = create_simple_flow()
        print("✓ Simple flow created successfully")

        print("\nFlow creation test completed successfully!")

    except Exception as e:
        print(f"✗ Error creating flows: {e}")
        raise
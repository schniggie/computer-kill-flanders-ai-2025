import argparse
import logging
import os
from flow import create_slidev_assistant_flow, create_simple_flow

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the Slidev Assistant"""

    parser = argparse.ArgumentParser(description="Slidev Assistant - Generate presentations from text descriptions")
    parser.add_argument(
        "--input",
        "-i",
        default="assets/presentation.txt",
        help="Input file with presentation requirements (default: assets/presentation.txt)"
    )
    parser.add_argument(
        "--demo",
        "-d",
        default="assets/demo.md",
        help="Demo file with custom components (default: assets/demo.md)"
    )
    parser.add_argument(
        "--slides",
        "-s",
        default="assets/slides.md",
        help="Slides file with Slidev capabilities (default: assets/slides.md)"
    )
    parser.add_argument(
        "--output",
        "-o",
        default="generated_presentation.md",
        help="Output file for generated presentation (default: generated_presentation.md)"
    )
    parser.add_argument(
        "--simple",
        action="store_true",
        help="Use simple flow without web research (faster, for testing)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate input files exist
    required_files = [args.input, args.demo, args.slides]
    for file_path in required_files:
        if not os.path.exists(file_path):
            logger.error(f"Required file not found: {file_path}")
            print(f"Error: File '{file_path}' not found!")
            return 1

    logger.info("Starting Slidev Assistant")
    logger.info(f"Input file: {args.input}")
    logger.info(f"Demo file: {args.demo}")
    logger.info(f"Slides file: {args.slides}")
    logger.info(f"Output file: {args.output}")
    logger.info(f"Simple mode: {args.simple}")

    try:
        # Initialize shared store
        shared = {
            "input_file": args.input,
            "demo_file": args.demo,
            "slides_file": args.slides,
            "output_file": args.output,
            # These will be populated by the flow
            "input": {},
            "components": {},
            "research": {
                "search_results": [],
                "crawled_content": {},
                "research_complete": False
            },
            "generated": {
                "outline": {},
                "slides": ""
            }
        }

        # Create and run the flow
        if args.simple:
            logger.info("Creating simple flow (no research)")
            flow = create_simple_flow()
        else:
            logger.info("Creating full flow with research agent")
            flow = create_slidev_assistant_flow()

        logger.info("Running Slidev Assistant flow...")
        flow.run(shared)

        # Report results
        if shared["generated"].get("slides"):
            slides_length = len(shared["generated"]["slides"])
            outline_slides = len(shared["generated"].get("outline", {}).get("slides", []))

            logger.info(f"✅ Successfully generated presentation!")
            logger.info(f"   - Slides generated: {outline_slides}")
            logger.info(f"   - Content length: {slides_length} characters")
            logger.info(f"   - Output saved to: {args.output}")

            print("\n" + "="*60)
            print("🎉 SLIDEV PRESENTATION GENERATED SUCCESSFULLY!")
            print("="*60)
            print(f"📄 Input: {args.input}")
            print(f"📋 Slides: {outline_slides} slides")
            print(f"📝 Content: {slides_length:,} characters")
            print(f"💾 Output: {args.output}")

            # Show research summary if available
            if not args.simple:
                research = shared.get("research", {})
                search_count = len(research.get("search_results", []))
                crawl_count = len(research.get("crawled_content", {}))
                if search_count > 0 or crawl_count > 0:
                    print(f"🔍 Research: {search_count} searches, {crawl_count} crawls")

            print("="*60)
            print(f"🚀 Ready to present! Run: slidev {args.output}")
            print("="*60)

            return 0

        else:
            logger.error("❌ Failed to generate presentation - no slides created")
            print("Error: No slides were generated. Check the logs for details.")
            return 1

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        print("\nOperation interrupted by user.")
        return 1

    except Exception as e:
        logger.error(f"❌ Error running Slidev Assistant: {e}", exc_info=args.debug)
        print(f"Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1

def demo():
    """Run a quick demo with the default presentation.txt"""
    print("Running Slidev Assistant Demo...")
    print("This will generate a presentation based on assets/presentation.txt")
    print()

    # Run with simple mode for faster demo
    import sys
    sys.argv = ["main.py", "--simple", "--debug"]
    return main()

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)

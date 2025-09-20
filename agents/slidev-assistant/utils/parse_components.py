import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_components(demo_content, slides_content):
    """
    Parse available components and Slidev capabilities from demo and slides files

    Args:
        demo_content (str): Content from demo.md with custom components
        slides_content (str): Content from slides.md with standard Slidev features

    Returns:
        dict: Dictionary with available_components and slidev_capabilities
    """
    try:
        # Parse custom components from demo.md
        custom_components = parse_custom_components(demo_content)

        # Parse standard Slidev capabilities from slides.md
        slidev_capabilities = parse_slidev_capabilities(slides_content)

        logger.info(f"Found {len(custom_components)} custom components")
        logger.info(f"Extracted Slidev capabilities: {len(slidev_capabilities)} characters")

        return {
            'available_components': custom_components,
            'slidev_capabilities': slidev_capabilities
        }

    except Exception as e:
        logger.error(f"Error parsing components: {e}")
        return {'available_components': [], 'slidev_capabilities': ''}

def parse_custom_components(demo_content):
    """
    Extract custom components from demo.md file

    Args:
        demo_content (str): Content of demo.md file

    Returns:
        list: List of custom components with their usage examples
    """
    components = []

    try:
        # Find Terminal component usage
        terminal_matches = re.findall(r'<Terminal[^>]*(?:/>|>.*?</Terminal>)', demo_content, re.DOTALL)
        for match in terminal_matches:
            components.append({
                'name': 'Terminal',
                'type': 'interactive',
                'usage': match,
                'description': 'Interactive terminal simulation with typing animations',
                'props': extract_component_props(match)
            })

        # Find Warning component usage
        warning_matches = re.findall(r'<Warning[^>]*(?:/>|>.*?</Warning>)', demo_content, re.DOTALL)
        for match in warning_matches:
            components.append({
                'name': 'Warning',
                'type': 'alert',
                'usage': match,
                'description': 'Security alert boxes with various types and animations',
                'props': extract_component_props(match)
            })

        # Extract special CSS classes mentioned in the demo
        css_classes = extract_special_classes(demo_content)
        if css_classes:
            components.append({
                'name': 'CSS Classes',
                'type': 'styling',
                'usage': css_classes,
                'description': 'Special CSS classes for nuclear/hacker theme effects',
                'props': []
            })

        # Extract layout information
        layouts = extract_layouts(demo_content)
        for layout in layouts:
            components.append({
                'name': f'Layout: {layout}',
                'type': 'layout',
                'usage': f'layout: {layout}',
                'description': f'Slidev layout: {layout}',
                'props': []
            })

        logger.info(f"Parsed {len(components)} custom components")
        return components

    except Exception as e:
        logger.error(f"Error parsing custom components: {e}")
        return []

def extract_component_props(component_match):
    """Extract properties from component usage"""
    props = []
    try:
        # Extract attributes like title="...", type="...", etc.
        attr_pattern = r'(\w+)=(?:"([^"]*)"|\'([^\']*)\')'
        matches = re.findall(attr_pattern, component_match)

        for match in matches:
            prop_name = match[0]
            prop_value = match[1] or match[2]
            props.append({'name': prop_name, 'value': prop_value})

    except Exception as e:
        logger.error(f"Error extracting props: {e}")

    return props

def extract_special_classes(content):
    """Extract special CSS classes mentioned in the content"""
    try:
        # Look for class mentions like .radioactive, .d-oh, .glitch, etc.
        class_pattern = r'\.(radioactive|d-oh|glitch|cursor|nuclear-warning|terminal-style)\b'
        classes = list(set(re.findall(class_pattern, content)))
        return classes
    except:
        return []

def extract_layouts(content):
    """Extract layout types used in the demo"""
    try:
        layout_pattern = r'layout:\s*(\w+)'
        layouts = list(set(re.findall(layout_pattern, content)))
        return layouts
    except:
        return []

def parse_slidev_capabilities(slides_content):
    """
    Extract standard Slidev capabilities from slides.md

    Args:
        slides_content (str): Content of slides.md file

    Returns:
        str: Formatted string describing Slidev capabilities
    """
    try:
        capabilities = []

        # Extract major feature sections
        feature_sections = [
            'Code highlighting',
            'Animations',
            'Components',
            'Themes',
            'LaTeX support',
            'Diagrams',
            'Interactive elements',
            'Layouts'
        ]

        # Look for actual features mentioned in slides.md
        if 'v-click' in slides_content:
            capabilities.append("Click animations with v-click directive")

        if 'v-motion' in slides_content:
            capabilities.append("Motion animations with v-motion directive")

        if 'mermaid' in slides_content or 'plantuml' in slides_content:
            capabilities.append("Diagram support (Mermaid, PlantUML)")

        if 'latex' in slides_content.lower() or 'katex' in slides_content:
            capabilities.append("LaTeX mathematical expressions with KaTeX")

        if 'monaco' in slides_content:
            capabilities.append("Monaco editor integration for code editing")

        if 'layout:' in slides_content:
            capabilities.append("Multiple slide layouts (center, two-cols, image-right, etc.)")

        if 'transition:' in slides_content:
            capabilities.append("Slide transitions (fade, slide-left, etc.)")

        # Extract code highlighting languages mentioned
        code_blocks = re.findall(r'```(\w+)', slides_content)
        if code_blocks:
            langs = list(set(code_blocks))
            capabilities.append(f"Code highlighting for: {', '.join(langs)}")

        result = "Standard Slidev capabilities:\n" + "\n".join([f"- {cap}" for cap in capabilities])

        logger.info("Parsed Slidev capabilities")
        return result

    except Exception as e:
        logger.error(f"Error parsing Slidev capabilities: {e}")
        return "Standard Slidev presentation framework with code highlighting, animations, and layouts"

if __name__ == "__main__":
    # Test with the demo files
    import os

    demo_path = os.path.join(os.path.dirname(__file__), "..", "assets", "demo.md")
    slides_path = os.path.join(os.path.dirname(__file__), "..", "assets", "slides.md")

    try:
        with open(demo_path, 'r') as f:
            demo_content = f.read()

        with open(slides_path, 'r') as f:
            slides_content = f.read()

        components_data = parse_components(demo_content, slides_content)

        print("=== CUSTOM COMPONENTS ===")
        for component in components_data['available_components']:
            print(f"\nComponent: {component['name']}")
            print(f"Type: {component['type']}")
            print(f"Description: {component['description']}")
            if component['props']:
                print(f"Props: {component['props'][:3]}...")  # Show first 3 props

        print("\n=== SLIDEV CAPABILITIES ===")
        print(components_data['slidev_capabilities'])

    except Exception as e:
        print(f"Error testing: {e}")
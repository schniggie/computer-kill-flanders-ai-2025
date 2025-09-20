import os
from openai import OpenAI
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_llm_config():
    """Load LLM configuration from assets/llm.env"""
    config = {}
    env_file = os.path.join(os.path.dirname(__file__), "..", "assets", "llm.env")

    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            content = f.read()
            # Parse the simple format: api_key="...", base_url="...", model="..."
            for line in content.strip().split(','):
                line = line.strip()
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"')
                    config[key] = value

    return config

def call_llm(prompt, messages=None, use_cache=True):
    """
    Call LLM using configuration from llm.env

    Args:
        prompt (str): The prompt to send to the LLM
        messages (list, optional): List of messages for chat completion
        use_cache (bool): Whether to use caching (for future enhancement)

    Returns:
        str: The LLM response
    """
    try:
        config = load_llm_config()

        client = OpenAI(
            api_key=config.get("api_key", ""),
            base_url=config.get("base_url", "https://api.openai.com/v1")
        )

        # Prepare messages
        if messages is None:
            messages = [{"role": "user", "content": prompt}]
        elif isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]

        logger.info(f"Calling LLM with model: {config.get('model', 'gpt-3.5-turbo')}")
        logger.info(f"Prompt length: {len(str(messages))}")

        response = client.chat.completions.create(
            model=config.get("model", "gpt-3.5-turbo"),
            messages=messages,
            temperature=0.7
        )

        result = response.choices[0].message.content
        logger.info(f"Response length: {len(result)}")

        return result

    except Exception as e:
        logger.error(f"Error calling LLM: {e}")
        raise e

if __name__ == "__main__":
    # Test the LLM function
    test_prompt = "Hello, can you help me create a presentation about AI safety?"

    print("Testing LLM call...")
    response = call_llm(test_prompt)
    print(f"Response: {response}")

from duckduckgo_search import DDGS
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def search_web(query, max_results=5, backend="text"):
    """
    Search the web using DuckDuckGo

    Args:
        query (str): Search query
        max_results (int): Maximum number of results to return
        backend (str): Search backend - "text" for general search, "news" for news

    Returns:
        list: List of search results with 'title', 'link', 'snippet' keys
    """
    try:
        logger.info(f"Searching for: {query} (max_results: {max_results})")

        with DDGS() as ddgs:
            if backend == "news":
                # Search for news articles
                results = ddgs.news(query, max_results=max_results)
            else:
                # Regular web search
                results = ddgs.text(query, max_results=max_results)

            # Convert to consistent format
            formatted_results = []
            for result in results:
                formatted_result = {
                    'title': result.get('title', ''),
                    'link': result.get('href', result.get('url', '')),
                    'snippet': result.get('body', result.get('snippet', ''))
                }
                formatted_results.append(formatted_result)

            logger.info(f"Found {len(formatted_results)} results")
            return formatted_results

    except Exception as e:
        logger.error(f"Error searching web: {e}")
        return []

def search_web_detailed(query, max_results=3):
    """
    Search the web and return detailed results with additional metadata

    Args:
        query (str): Search query
        max_results (int): Maximum number of results to return

    Returns:
        list: List of detailed search results
    """
    try:
        logger.info(f"Detailed search for: {query}")

        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=max_results)

            detailed_results = []
            for result in results:
                detailed_result = {
                    'title': result.get('title', ''),
                    'link': result.get('href', ''),
                    'snippet': result.get('body', ''),
                    'source': result.get('hostname', ''),
                    'relevance_score': 1.0  # Could be enhanced with actual scoring
                }
                detailed_results.append(detailed_result)

            return detailed_results

    except Exception as e:
        logger.error(f"Error in detailed search: {e}")
        return []

if __name__ == "__main__":
    # Test the search functions
    test_query = "latest AI fails 2024"

    print("Testing basic web search...")
    results = search_web(test_query, max_results=3)

    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   Link: {result['link']}")
        print(f"   Snippet: {result['snippet'][:100]}...")

    print("\n" + "="*50)
    print("Testing news search...")
    news_results = search_web(test_query, max_results=2, backend="news")

    for i, result in enumerate(news_results, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   Link: {result['link']}")
        print(f"   Snippet: {result['snippet'][:100]}...")
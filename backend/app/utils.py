"""Utility functions for PromptLab"""

from typing import List
from app.models import Prompt


def sort_prompts_by_date(prompts: List[Prompt], descending: bool = True) -> List[Prompt]:
    """Sort prompts by creation date.
    
    Args:
        prompts (List[Prompt]): A list of prompts to be sorted.
        descending (bool): If True, sort in descending order (newest first). If False, sort in ascending order (oldest first).

    Returns:
        List[Prompt]: The list of prompts sorted by creation date.

    """
    return sorted(prompts, key=lambda p: p.created_at, reverse=descending)


def filter_prompts_by_collection(prompts: List[Prompt], collection_id: str) -> List[Prompt]:
    """Filter prompts by a specific collection ID.
    
    Args:
        prompts (List[Prompt]): A list of prompts to filter.
        collection_id (str): The ID of the collection to filter prompts by.

    Returns:
        List[Prompt]: A list of prompts that belong to the specified collection.

    """
    return [p for p in prompts if p.collection_id == collection_id]


def search_prompts(prompts: List[Prompt], query: str) -> List[Prompt]:
    """Search for prompts based on a query string. Matching is case-insensitive.
    
    Args:
        prompts (List[Prompt]): A list of prompts to search through.
        query (str): The search term used to find prompts by title or description.

    Returns:
        List[Prompt]: A list of prompts that contain the search query in their title or description.

    """
    query_lower = query.lower()
    return [
        p for p in prompts 
        if query_lower in p.title.lower() or 
           (p.description and query_lower in p.description.lower())
    ]


def validate_prompt_content(content: str) -> bool:
    """Check if prompt content is valid.
    
    A valid prompt should:
    - Not be empty
    - Not be just whitespace
    - Be at least 10 characters after stripping leading and trailing whitespaces

    Args:
        content (str): The content of the prompt to validate.

    Returns:
        bool: True if the content is valid, False otherwise.

    Example:
        >>> is_valid = validate_prompt_content('This is a valid prompt.')
        >>> is_valid
        True
    """
    if not content or not content.strip():
        return False
    return len(content.strip()) >= 10


def extract_variables(content: str) -> List[str]:
    """Extract template variables from prompt content.
    
    Variables are in the format {{variable_name}}.

    Args:
        content (str): The content of the prompt containing template variables.

    Returns:
        List[str]: A list of variable names extracted from the content.

    Example:
        >>> variables = extract_variables('Hello {{name}}, welcome to {{place}}!')
        >>> variables
        ['name', 'place']
    """
    import re
    pattern = r'\{\{(\w+)\}\}'
    return re.findall(pattern, content)

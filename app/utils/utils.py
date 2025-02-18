from typing import List
import re

def sql_like_search(value: str) -> dict:
    """
    Create a MongoDB query for case-insensitive partial string matching.
    Mimics SQL's LIKE %value% behavior with proper substring matching.
    
    Args:
        value (str): Search term
    
    Returns:
        dict: MongoDB regex query
    """
    if not value:
        return {}
    
    # Pastikan case-insensitive substring match
    # Contoh: "Gadget" cocok dengan "gadget", "SuperGadget"
    escaped_value = re.escape(value.strip())  # Escape special regex chars
    return {"$regex": escaped_value, "$options": "i"}

def array_like_search(values: List[str]) -> dict:
    """
    Create a MongoDB query for case-insensitive substring search with multiple values.
    Replaces $in with $or to allow multiple regex conditions.
    
    Args:
        values (List[str]): List of search terms
    
    Returns:
        dict: MongoDB $or query using regex
    """
    if not values:
        return {}

    regex_list = [{"tags": {"$regex": re.escape(val.strip()), "$options": "i"}} for val in values]
    return {"$or": regex_list}

def parse_comma_separated(value: str) -> List[str]:
    """Convert comma-separated string to list of strings."""
    return value.split(",") if value else []

def trim_value(value):
    if isinstance(value, str):
        return value.strip()
    elif isinstance(value, list):
        return [item.strip() if isinstance(item, str) else item for item in value]
    return value

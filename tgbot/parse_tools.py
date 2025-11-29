#!/usr/bin/python
# -*- coding: utf8 -*-
"""
Parse tools module for searching GOSTs from various sources.

This module provides functions to search for GOSTs in the local database
and from online sources.
"""

from bs4 import BeautifulSoup
import requests

from tgbot.models import Gost, session
from tgbot.data_sources import (
    get_all_data_sources,
    fetch_from_all_sources,
    fetch_from_source,
)


# Optional: OCR support for extracting GOST numbers from images
try:
    from PIL import Image
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False


def get_gost_from_photo(photo_path: str) -> str:
    """
    Extract GOST text from an image using OCR.
    
    Args:
        photo_path: Path to the image file.
        
    Returns:
        Extracted text from the image.
        
    Raises:
        ImportError: If PIL or pytesseract are not installed.
    """
    if not HAS_OCR:
        raise ImportError("PIL and pytesseract are required for OCR functionality")
    return pytesseract.image_to_string(Image.open(photo_path))


def get_search_list_online(search_text: str) -> list:
    """
    Search for GOSTs online from all available data sources.
    
    Args:
        search_text: The search query.
        
    Returns:
        List of matching GOSTs as dictionaries with 'name' and 'description'.
    """
    all_gosts = fetch_from_all_sources()
    
    # Filter results based on search text
    search_lower = search_text.lower()
    results = []
    
    for gost in all_gosts:
        if (search_lower in gost['name'].lower() or 
            search_lower in gost.get('description', '').lower()):
            results.append(gost)
    
    return results


def get_search_list_db(search_text: str) -> list:
    """
    Search for GOSTs in the local database.
    
    Args:
        search_text: The search query.
        
    Returns:
        List of Gost objects matching the search.
    """
    # Search in name
    res = session.query(Gost).filter(
        Gost.name.like('%' + search_text + '%')
    ).all()
    
    # Also search in description, avoiding duplicates
    existing_ids = {g.id for g in res}
    desc_results = session.query(Gost).filter(
        Gost.description.like('%' + search_text + '%')
    ).all()
    
    for gost in desc_results:
        if gost.id not in existing_ids:
            res.append(gost)
            existing_ids.add(gost.id)
    
    return res


def get_search_list(search_text: str) -> list:
    """
    Search for GOSTs from all sources (database first, then online).
    
    Args:
        search_text: The search query.
        
    Returns:
        List of GOSTs as [name, description] pairs.
    """
    # First try database
    db_results = get_search_list_db(search_text)
    if db_results:
        return [[g.name, g.description] for g in db_results]
    
    # Fall back to online search
    online_results = get_search_list_online(search_text)
    return [[g['name'], g.get('description', '')] for g in online_results]


def list_available_sources() -> list:
    """
    Get a list of all available GOST data sources.
    
    Returns:
        List of source names.
    """
    return [source.name for source in get_all_data_sources()]

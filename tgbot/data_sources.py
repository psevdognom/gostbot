#!/usr/bin/python
# -*- coding: utf8 -*-
"""
Data sources module for retrieving GOSTs from various public APIs and storages.

This module contains parsers for multiple GOST data sources:
- gost.ru - Official Russian Standards portal (Rosstandart)
- docs.cntd.ru - Technical regulations and standards database
- protect.gost.ru - Official GOST protection portal
- meganorm.ru - Standards database
- files.stroyinf.ru - Construction standards database
- internet-law.ru - Legal database with GOST standards
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import logging

from bs4 import BeautifulSoup
from lxml import html
import requests

from tgbot.models import Gost, session, Base, engine

logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36',
    'Accept': '*/*'
}


class GostDataSource(ABC):
    """Abstract base class for GOST data sources."""
    
    name: str = "Base Source"
    base_url: str = ""
    
    @abstractmethod
    def fetch_gosts(self) -> List[Dict[str, str]]:
        """
        Fetch GOSTs from the data source.
        
        Returns:
            List of dictionaries with 'name' and 'description' keys.
        """
        pass
    
    def get_html(self, url: str, params: Optional[Dict] = None) -> Optional[str]:
        """
        Helper method to fetch HTML content from a URL.
        
        Args:
            url: The URL to fetch.
            params: Optional query parameters.
            
        Returns:
            HTML content as string, or None if request failed.
        """
        try:
            response = requests.get(url, headers=HEADERS, params=params, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None


class GostRuDataSource(GostDataSource):
    """
    Parser for gost.ru - Official Russian Standards portal (Rosstandart).
    
    This source provides official open data for national standards.
    URL: https://www.gost.ru/opendata/7706406291-nationalstandards
    """
    
    name = "gost.ru"
    base_url = "https://www.gost.ru"
    opendata_url = "/opendata/7706406291-nationalstandards"
    
    def fetch_gosts(self) -> List[Dict[str, str]]:
        """Fetch GOSTs from gost.ru open data portal."""
        gosts = []
        
        try:
            page = requests.get(
                self.base_url + self.opendata_url,
                headers=HEADERS,
                timeout=30
            )
            page.raise_for_status()
            
            tree = html.fromstring(page.content)
            # Find the CSV file link using the XPath pattern
            csv_links = tree.xpath('//*[@id="242b6628-20e0-459f-b512-2fe12015e7eb"]/div/div[1]/div[5]/div[1]/a/@href')
            
            if not csv_links:
                # Try alternative XPath for different page structure
                csv_links = tree.xpath('//a[contains(@href, ".csv")]/@href')
            
            if csv_links:
                csv_url = csv_links[0]
                if not csv_url.startswith('http'):
                    csv_url = self.base_url + csv_url
                
                file_response = requests.get(csv_url, headers=HEADERS, timeout=60)
                file_response.raise_for_status()
                
                # Parse CSV content (CP1251 encoding for Russian)
                content = file_response.content.decode('cp1251').splitlines()
                
                for i in range(1, len(content)):
                    data = content[i].split(";")
                    if len(data) >= 2:
                        gosts.append({
                            'name': data[0].strip(),
                            'description': data[1].strip()
                        })
                        
            logger.info(f"Fetched {len(gosts)} GOSTs from {self.name}")
            
        except requests.RequestException as e:
            logger.error(f"Error fetching from {self.name}: {e}")
        except Exception as e:
            logger.error(f"Error parsing data from {self.name}: {e}")
            
        return gosts


class DocsCntdRuDataSource(GostDataSource):
    """
    Parser for docs.cntd.ru - Electronic fund of legal and normative-technical documents.
    
    This source provides access to GOST standards through their catalog.
    URL: https://docs.cntd.ru/document/gost
    """
    
    name = "docs.cntd.ru"
    base_url = "https://docs.cntd.ru"
    catalog_url = "/document/gost"
    
    def fetch_gosts(self) -> List[Dict[str, str]]:
        """Fetch GOSTs from docs.cntd.ru catalog."""
        gosts = []
        
        html_content = self.get_html(self.base_url + self.catalog_url)
        if not html_content:
            return gosts
        
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Parse GOST items from the catalog
            items = soup.find_all('div', class_='doc-item') or \
                    soup.find_all('a', class_='document-title') or \
                    soup.find_all('li', class_='doc')
            
            for item in items:
                title_elem = item.find('a') if item.name != 'a' else item
                desc_elem = item.find('span', class_='description') or \
                           item.find('div', class_='doc-desc')
                
                if title_elem:
                    name = title_elem.get_text(strip=True)
                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    if name and 'ГОСТ' in name.upper():
                        gosts.append({
                            'name': name,
                            'description': description
                        })
            
            logger.info(f"Fetched {len(gosts)} GOSTs from {self.name}")
            
        except Exception as e:
            logger.error(f"Error parsing data from {self.name}: {e}")
            
        return gosts


class MeganormRuDataSource(GostDataSource):
    """
    Parser for meganorm.ru - Normative documents database.
    
    This source provides GOST standards organized by categories.
    URL: https://meganorm.ru/
    """
    
    name = "meganorm.ru"
    base_url = "https://meganorm.ru"
    gost_url = "/Index2/1/4294817/4294817904.htm"  # GOST category
    
    def fetch_gosts(self) -> List[Dict[str, str]]:
        """Fetch GOSTs from meganorm.ru."""
        gosts = []
        
        html_content = self.get_html(self.base_url + self.gost_url)
        if not html_content:
            return gosts
        
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Parse GOST links from the page
            rows = soup.find_all('tr')
            
            for row in rows:
                link = row.find('a')
                if link and 'ГОСТ' in link.get_text().upper():
                    name = link.get_text(strip=True)
                    
                    # Get description from adjacent cells
                    cells = row.find_all('td')
                    description = ""
                    if len(cells) > 1:
                        description = cells[1].get_text(strip=True)
                    
                    gosts.append({
                        'name': name,
                        'description': description
                    })
            
            logger.info(f"Fetched {len(gosts)} GOSTs from {self.name}")
            
        except Exception as e:
            logger.error(f"Error parsing data from {self.name}: {e}")
            
        return gosts


class ProtectGostRuDataSource(GostDataSource):
    """
    Parser for protect.gost.ru - GOST documents protection system.
    
    This is the official portal for protected GOST documents.
    URL: https://protect.gost.ru
    """
    
    name = "protect.gost.ru"
    base_url = "https://protect.gost.ru"
    search_url = "/v.aspx"
    
    def fetch_gosts(self) -> List[Dict[str, str]]:
        """Fetch GOSTs from protect.gost.ru."""
        gosts = []
        
        try:
            # This source requires specific queries
            # We'll search for common GOST prefixes
            prefixes = ['ГОСТ Р', 'ГОСТ']
            
            for prefix in prefixes:
                params = {'s': prefix}
                html_content = self.get_html(self.base_url + self.search_url, params)
                if not html_content:
                    continue
                
                soup = BeautifulSoup(html_content, 'lxml')
                
                # Parse search results
                results = soup.find_all('div', class_='result-item') or \
                         soup.find_all('tr', class_='doc-row')
                
                for result in results:
                    title_elem = result.find('a') or result.find('span', class_='title')
                    desc_elem = result.find('p') or result.find('span', class_='desc')
                    
                    if title_elem:
                        name = title_elem.get_text(strip=True)
                        description = desc_elem.get_text(strip=True) if desc_elem else ""
                        
                        gosts.append({
                            'name': name,
                            'description': description
                        })
            
            logger.info(f"Fetched {len(gosts)} GOSTs from {self.name}")
            
        except Exception as e:
            logger.error(f"Error fetching/parsing from {self.name}: {e}")
            
        return gosts


class FilesStroyinfRuDataSource(GostDataSource):
    """
    Parser for files.stroyinf.ru - Construction standards database.
    
    This source provides construction-related GOST standards.
    URL: https://files.stroyinf.ru
    """
    
    name = "files.stroyinf.ru"
    base_url = "https://files.stroyinf.ru"
    gost_url = "/cat/Gosts.html"
    
    def fetch_gosts(self) -> List[Dict[str, str]]:
        """Fetch GOSTs from files.stroyinf.ru."""
        gosts = []
        
        html_content = self.get_html(self.base_url + self.gost_url)
        if not html_content:
            return gosts
        
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Parse GOST links from the catalog
            links = soup.find_all('a')
            
            for link in links:
                text = link.get_text(strip=True)
                if 'ГОСТ' in text.upper():
                    # Extract name and description if available
                    parent = link.parent
                    description = ""
                    
                    if parent:
                        # Try to get description from sibling or parent elements
                        next_sibling = link.find_next_sibling(string=True)
                        if next_sibling:
                            description = str(next_sibling).strip()
                    
                    gosts.append({
                        'name': text,
                        'description': description
                    })
            
            logger.info(f"Fetched {len(gosts)} GOSTs from {self.name}")
            
        except Exception as e:
            logger.error(f"Error parsing data from {self.name}: {e}")
            
        return gosts


class InternetLawRuDataSource(GostDataSource):
    """
    Parser for internet-law.ru - Legal database with GOST standards.
    
    This source provides GOST standards in a searchable format.
    URL: https://internet-law.ru/gosts/
    """
    
    name = "internet-law.ru"
    base_url = "https://internet-law.ru"
    gost_url = "/gosts/"
    
    def fetch_gosts(self) -> List[Dict[str, str]]:
        """Fetch GOSTs from internet-law.ru."""
        gosts = []
        
        html_content = self.get_html(self.base_url + self.gost_url)
        if not html_content:
            return gosts
        
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Parse GOST items
            items = soup.find_all('div', class_='gost-item') or \
                    soup.find_all('li', class_='gost')
            
            for item in items:
                link = item.find('a')
                if link:
                    name = link.get_text(strip=True)
                    
                    # Get description
                    desc_elem = item.find('p') or item.find('span', class_='desc')
                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    if 'ГОСТ' in name.upper():
                        gosts.append({
                            'name': name,
                            'description': description
                        })
            
            logger.info(f"Fetched {len(gosts)} GOSTs from {self.name}")
            
        except Exception as e:
            logger.error(f"Error parsing data from {self.name}: {e}")
            
        return gosts


class LibGostRuDataSource(GostDataSource):
    """
    Parser for libgost.ru - GOST library.
    
    This source provides GOST standards in various categories.
    URL: http://libgost.ru/gost/
    """
    
    name = "libgost.ru"
    base_url = "http://libgost.ru"
    gost_url = "/gost/"
    
    def fetch_gosts(self) -> List[Dict[str, str]]:
        """Fetch GOSTs from libgost.ru."""
        gosts = []
        
        html_content = self.get_html(self.base_url + self.gost_url)
        if not html_content:
            return gosts
        
        try:
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Parse news items containing GOSTs
            items = soup.find_all('div', class_='news')
            
            for item in items:
                title_elem = item.find('a') or item.find('h2') or item.find('h3')
                if title_elem:
                    name = title_elem.get_text(strip=True)
                    
                    # Get description from the item content
                    desc_elem = item.find('p') or item.find('div', class_='desc')
                    description = desc_elem.get_text(strip=True) if desc_elem else ""
                    
                    if 'ГОСТ' in name.upper() or name:
                        gosts.append({
                            'name': name,
                            'description': description
                        })
            
            logger.info(f"Fetched {len(gosts)} GOSTs from {self.name}")
            
        except Exception as e:
            logger.error(f"Error parsing data from {self.name}: {e}")
            
        return gosts


# Registry of all available data sources
DATA_SOURCES = [
    GostRuDataSource(),
    DocsCntdRuDataSource(),
    MeganormRuDataSource(),
    ProtectGostRuDataSource(),
    FilesStroyinfRuDataSource(),
    InternetLawRuDataSource(),
    LibGostRuDataSource(),
]


def get_all_data_sources() -> List[GostDataSource]:
    """Get all available GOST data sources."""
    return DATA_SOURCES


def fetch_from_source(source: GostDataSource) -> List[Dict[str, str]]:
    """
    Fetch GOSTs from a specific data source.
    
    Args:
        source: The data source to fetch from.
        
    Returns:
        List of GOST dictionaries.
    """
    logger.info(f"Fetching from {source.name}...")
    return source.fetch_gosts()


def fetch_from_all_sources() -> List[Dict[str, str]]:
    """
    Fetch GOSTs from all available data sources.
    
    Returns:
        Combined list of GOSTs from all sources.
    """
    all_gosts = []
    
    for source in DATA_SOURCES:
        try:
            gosts = fetch_from_source(source)
            all_gosts.extend(gosts)
        except Exception as e:
            logger.error(f"Failed to fetch from {source.name}: {e}")
    
    # Remove duplicates based on name
    seen_names = set()
    unique_gosts = []
    for gost in all_gosts:
        if gost['name'] not in seen_names:
            seen_names.add(gost['name'])
            unique_gosts.append(gost)
    
    logger.info(f"Total unique GOSTs fetched: {len(unique_gosts)}")
    return unique_gosts


def save_gosts_to_db(gosts: List[Dict[str, str]]) -> int:
    """
    Save GOSTs to the database.
    
    Args:
        gosts: List of GOST dictionaries with 'name' and 'description'.
        
    Returns:
        Number of GOSTs saved.
    """
    Base.metadata.create_all(engine)
    
    count = 0
    for gost_data in gosts:
        # Check if GOST already exists
        existing = session.query(Gost).filter(Gost.name == gost_data['name']).first()
        if not existing:
            gost = Gost(name=gost_data['name'], description=gost_data['description'])
            session.add(gost)
            count += 1
    
    session.commit()
    logger.info(f"Saved {count} new GOSTs to database")
    return count


def update_database_from_all_sources() -> int:
    """
    Fetch GOSTs from all sources and update the database.
    
    Returns:
        Number of new GOSTs added.
    """
    gosts = fetch_from_all_sources()
    return save_gosts_to_db(gosts)


if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Update database from all sources
    count = update_database_from_all_sources()
    print(f"Added {count} new GOSTs to the database")

"""
Script to populate the GOST database from all available data sources.

Usage:
    python csv_to_sql.py [--source SOURCE_NAME] [--all]

Options:
    --source SOURCE_NAME  Fetch from a specific source only
    --all                 Fetch from all available sources (default)
"""

import argparse
import logging
import sys

from tgbot.data_sources import (
    get_all_data_sources,
    fetch_from_source,
    save_gosts_to_db,
    update_database_from_all_sources,
    GostRuDataSource,
)
from tgbot.models import Base, engine

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for the database update script."""
    parser = argparse.ArgumentParser(
        description='Populate the GOST database from available data sources.'
    )
    parser.add_argument(
        '--source',
        type=str,
        help='Fetch from a specific source only (e.g., gost.ru, docs.cntd.ru)'
    )
    parser.add_argument(
        '--list-sources',
        action='store_true',
        help='List all available data sources'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        default=True,
        help='Fetch from all available sources (default)'
    )
    
    args = parser.parse_args()
    
    # Create database tables if they don't exist
    Base.metadata.create_all(engine)
    
    if args.list_sources:
        print("Available data sources:")
        for source in get_all_data_sources():
            print(f"  - {source.name}: {source.base_url}")
        return 0
    
    if args.source:
        # Find the specific source
        sources = get_all_data_sources()
        source = next((s for s in sources if s.name.lower() == args.source.lower()), None)
        
        if not source:
            print(f"Error: Unknown source '{args.source}'")
            print("Available sources:")
            for s in sources:
                print(f"  - {s.name}")
            return 1
        
        logger.info(f"Fetching from {source.name}...")
        gosts = fetch_from_source(source)
        count = save_gosts_to_db(gosts)
        print(f"Added {count} new GOSTs from {source.name}")
    else:
        # Fetch from all sources
        logger.info("Fetching from all available sources...")
        count = update_database_from_all_sources()
        print(f"Added {count} new GOSTs from all sources")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
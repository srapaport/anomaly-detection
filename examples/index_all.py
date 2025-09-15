import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from graphrepo.drillers.cache_driller import CacheDriller
from graphrepo.logger import Logger

LG = Logger()

def main():
    parser = argparse.ArgumentParser(description='Index all repository data in Neo4j')
    parser.add_argument('--config', required=True, help='Path to the configuration file')
    
    args = parser.parse_args()
    
    try:
        print(f"Starting repository indexing with config: {args.config}")
        
        driller = CacheDriller(config_path=args.config)
        
        print("Mining repository data...")

        driller.drill_batch_cache_sequential(index=True)
        
        print("Repository indexing completed successfully!")
        
    except Exception as e:
        LG.log_and_raise(e)

if __name__ == '__main__':
    main()
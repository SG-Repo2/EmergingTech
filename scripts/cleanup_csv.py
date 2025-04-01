import os
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('csv_cleaner')

def delete_csv_files(directory):
    """Delete all CSV files in the specified directory"""
    path = Path(directory)
    if not path.is_dir():
        logger.error(f"Directory not found: {directory}")
        return
    
    csv_files = list(path.glob("*.csv"))
    
    if not csv_files:
        logger.info(f"No CSV files found in {directory}")
        return
    
    for csv_file in csv_files:
        try:
            csv_file.unlink()
            logger.info(f"Deleted: {csv_file}")
        except Exception as e:
            logger.error(f"Failed to delete {csv_file}: {str(e)}")
    
    logger.info(f"Deleted {len(csv_files)} CSV files")

def main():
    parser = argparse.ArgumentParser(description="Delete CSV files from a directory")
    parser.add_argument(
        "directory", 
        help="Directory containing CSV files to delete"
    )
    args = parser.parse_args()
    
    delete_csv_files(args.directory)

if __name__ == "__main__":
    main()

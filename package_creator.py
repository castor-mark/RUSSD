"""
RUSSD Package Creator
Creates the final ZIP file with DATA and META files
"""

import zipfile
import os
from datetime import datetime


def create_package(data_file, meta_file):
    """
    Create RUSSD_YYYYMMDD.ZIP containing both files
    
    Args:
        data_file: Path to RUSSD_DATA_YYYYMMDD.xlsx
        meta_file: Path to RUSSD_META_YYYYMMDD.xls
    """
    # Extract timestamp from data file
    timestamp = data_file.split('_')[-1].replace('.xlsx', '').replace('.xls', '')
    zip_filename = f'RUSSD_{timestamp}.ZIP'
    
    # Create ZIP file
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        if os.path.exists(data_file):
            zipf.write(data_file, os.path.basename(data_file))
            print(f"  Added: {data_file}")
        
        if os.path.exists(meta_file):
            zipf.write(meta_file, os.path.basename(meta_file))
            print(f"  Added: {meta_file}")
    
    print(f"\n✅ Package created: {zip_filename}")
    return zip_filename


if __name__ == "__main__":
    # Example usage
    data_file = "RUSSD_DATA_20250211.xlsx"
    meta_file = "RUSSD_META_20250211.xls"
    create_package(data_file, meta_file)
"""
RUSSD Metadata File Generator
Creates the metadata file required by the data engineering team
"""

from datetime import datetime
import xlwt

from config import EXCEL_HEADERS, DATA_COLUMNS, DATA_FREQUENCY, DATA_SOURCE_NAME


def create_metadata_file(trade_date_str):
    """
    Create RUSSD_META_YYYYMMDD.xls file
    
    Args:
        trade_date_str: Trade date in YYYY-MM-DD format
    """
    # Parse trade date
    trade_date = datetime.strptime(trade_date_str, '%Y-%m-%d')
    timestamp = trade_date.strftime('%Y%m%d')
    filename = f'RUSSD_META_{timestamp}.xls'
    
    # Create workbook
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Metadata')
    
    # Headers
    headers = ['CODE', 'DESCRIPTION', 'FREQUENCY', 'UNIT', 'SOURCE', 'LAST_UPDATE', 'NEXT_RELEASE_DATE']
    
    # Write headers
    for col_idx, header in enumerate(headers):
        ws.write(0, col_idx, header)
    
    # Write metadata for each column
    row_idx = 1
    for col_letter in DATA_COLUMNS:
        col_info = EXCEL_HEADERS[col_letter]
        
        # Determine unit based on data type
        if 'date' in col_info['description'].lower():
            unit = 'Date (YYYYMMDD)'
        elif 'rate' in col_info['description'].lower() or '%' in col_info['description']:
            unit = '% per annum'
        elif 'volume' in col_info['description'].lower():
            if 'rubles' in col_info['description'].lower():
                unit = 'Millions of RUB'
            else:
                unit = 'Millions of USD'
        elif 'amount' in col_info['description'].lower():
            unit = 'Billions of FC'
        elif 'points' in col_info['description'].lower():
            unit = 'Rubles'
        else:
            unit = 'Number'
        
        # Next release date (tomorrow at 10:00 UTC)
        next_release = datetime.now().strftime('%Y-%m-%dT10:00:00')
        
        # Write row
        ws.write(row_idx, 0, col_info['code'])
        ws.write(row_idx, 1, col_info['description'])
        ws.write(row_idx, 2, DATA_FREQUENCY)
        ws.write(row_idx, 3, unit)
        ws.write(row_idx, 4, DATA_SOURCE_NAME)
        ws.write(row_idx, 5, trade_date_str)
        ws.write(row_idx, 6, next_release)
        
        row_idx += 1
    
    # Save file
    wb.save(filename)
    print(f"✅ Metadata file created: {filename}")
    
    return filename


if __name__ == "__main__":
    # Example usage
    create_metadata_file('2025-02-11')
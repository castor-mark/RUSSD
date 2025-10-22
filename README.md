# RUSSD - Russian Central Bank FX Swaps Data Scraper

Automated data collection tool for Russian Central Bank (CBR) Foreign Currency/RUB FX Swaps data.

## Overview

This script collects daily FX swap data from the Central Bank of Russia website, including:
- Volume of Foreign Currency/RUB sell/buy FX Swaps
- Terms of Foreign Currency/RUB sell/buy FX Swaps

Data is collected for USD currency across TODTOM and TOMSPT settlement types.

## Requirements

- Python 3.13+
- Chrome browser installed
- Internet connection

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install setuptools (required for Python 3.12+):
```bash
pip install setuptools
```

## Usage

Run the orchestrator script:
```bash
python orchastrator.py
```

The script will:
1. Launch Chrome browser with undetected-chromedriver
2. Scrape data from CBR website
3. Generate Excel data file: `RUSSD_DATA_YYYYMMDD.xlsx`
4. Generate metadata file: `RUSSD_META_YYYYMMDD.xls`
5. Create ZIP package: `RUSSD_YYYYMMDD.ZIP`

## Output Files

- **RUSSD_DATA_YYYYMMDD.xlsx** - Main data file with 18 columns (B-S) containing swap volumes and terms
- **RUSSD_META_YYYYMMDD.xls** - Metadata file with column descriptions, units, and frequency
- **RUSSD_YYYYMMDD.ZIP** - Compressed package containing both files

## Configuration

Edit `config.py` to modify:
- Data sources and URLs
- Currency and settlement mappings
- Excel column headers and mappings
- Date formats
- Web scraping selectors

## Data Sources

- **swapinfosellvol**: https://www.cbr.ru/eng/hd_base/swap_info/swapinfosellvol/
- **swap_info_sell**: https://www.cbr.ru/eng/hd_base/swap_info/sell/

## Troubleshooting

**ModuleNotFoundError: No module named 'distutils'**
- Solution: `pip install setuptools`

**Chrome driver issues**
- The script uses undetected-chromedriver which auto-downloads the correct Chrome driver
- Ensure Chrome browser is installed and up to date

## License

This tool is for data collection purposes only. Please respect the Central Bank of Russia's terms of service.

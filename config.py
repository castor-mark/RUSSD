# config.py

# =============================================================================
# DATA SOURCES CONFIGURATION
# =============================================================================
DATA_SOURCES = {
    'swapinfosellvol': {
        'url': 'https://www.cbr.ru/eng/hd_base/swap_info/swapinfosellvol/',
        'description': 'Volume of Foreign Currency/RUB sell/buy FX Swaps',
        'settlements': ['TODTOM', 'TOMSPT'],
    },
    'swap_info_sell': {
        'url': 'https://www.cbr.ru/eng/hd_base/swap_info/sell/',
        'description': 'Terms of Foreign Currency/RUB sell/buy FX Swaps',
        'settlements': ['TODTOM', 'TOMSPT'],
    }
}

# =============================================================================
# CURRENCY AND SETTLEMENT MAPPINGS
# =============================================================================
CURRENCIES = {
    'USD': {'name': 'US Dollar', 'value': '0', 'id': 'UniDbQuery_Cur_1'},
    'EUR': {'name': 'Euro', 'value': '1', 'id': 'UniDbQuery_Cur_2'},
    'CNY': {'name': 'Chinese Yuan', 'value': '2', 'id': 'UniDbQuery_Cur_3'}
}
DEFAULT_CURRENCY = 'USD'

SETTLEMENTS = {
    'TODTOM': {'name': 'Today-Tomorrow', 'value': '0', 'id': 'UniDbQuery_P1_1'},
    'TOMSPT': {'name': 'Tomorrow-Spot', 'value': '1', 'id': 'UniDbQuery_P1_2'}
}

# =============================================================================
# DATE FORMATS
# =============================================================================
SOURCE_DATE_FORMAT = '%d.%m.%Y'
OUTPUT_DATE_FORMAT = '%Y-%m-%d'
DATE_INT_FORMAT = '%Y%m%d'

# =============================================================================
# WEB SCRAPING SELECTORS
# =============================================================================
SELECTORS = {
    'filter_button': 'button.filter_title',
    'dropdown_content_visible': 'div.filter_content[style*="display: block;"]',
    'datepicker_button': 'button.datepicker-filter_button',
    'date_from_input': 'input.datepicker-filter_input-from',
    'date_to_input': 'input.datepicker-filter_input-to',
    'datepicker_apply': 'button.datepicker-filter_apply-btn',
    'data_table': 'table.data',
    'cookie_accept_button': 'button.js-cookie-accept'
}

# =============================================================================
# EXCEL OUTPUT CONFIGURATION
# =============================================================================
EXCEL_HEADERS = {
    'B': {'code': 'RUSSD.VOLUMEFXSWAPS.TODTOM.USD.B', 'description': 'Volume of Foreign Currency/RUB sell/buy FX Swaps. TODTOM. USD'},
    'C': {'code': 'RUSSD.VOLUMEFXSWAPS.TODTOM.RUB.B', 'description': 'Volume of Foreign Currency/RUB sell/buy FX Swaps. TODTOM. USD. Rubles'},
    'D': {'code': 'RUSSD.VOLUMEFXSWAPS.TOMSPT.USD.B', 'description': 'Volume of Foreign Currency/RUB sell/buy FX Swaps. TOMSPT. USD'},
    'E': {'code': 'RUSSD.VOLUMEFXSWAPS.TOMSPT.RUB.B', 'description': 'Volume of Foreign Currency/RUB sell/buy FX Swaps. TOMSPT. USD. Rubles'},
    'F': {'code': 'RUSSD.TERMSFXSWAPS.TODTOM.FCSELLDATE.B', 'description': 'Terms of Foreign Currency/RUB sell/buy FX Swaps. TODTOM. USD. FC sell date'},
    'G': {'code': 'RUSSD.TERMSFXSWAPS.TODTOM.RUBSELLDATE.B', 'description': 'Terms of Foreign Currency/RUB sell/buy FX Swaps. TODTOM. USD. RUB sell date'},
    'H': {'code': 'RUSSD.TERMSFXSWAPS.TODTOM.RUBINTERESTRATE.B', 'description': 'Terms of Foreign Currency/RUB sell/buy FX Swaps. TODTOM. USD. RUB interest rate (% p.a.)'},
    'I': {'code': 'RUSSD.TERMSFXSWAPS.TODTOM.FCINTERESTRATE.B', 'description': 'Terms of Foreign Currency/RUB sell/buy FX Swaps. TODTOM. USD. FC interest rate (% p.a.)'},
    'J': {'code': 'RUSSD.TERMSFXSWAPS.TODTOM.BASESWAPRATE.B', 'description': 'Terms of Foreign Currency/RUB sell/buy FX Swaps. TODTOM. USD. Base swap rate RUB/FC'},
    'K': {'code': 'RUSSD.TERMSFXSWAPS.TODTOM.SWAPPOINTSRUB.B', 'description': 'Terms of Foreign Currency/RUB sell/buy FX Swaps. TODTOM. USD. Swap points (rubles)'},
    'L': {'code': 'RUSSD.TERMSFXSWAPS.TODTOM.MAXALLOTMENTAMOUNT.B', 'description': 'Terms of Foreign Currency/RUB sell/buy FX Swaps. TODTOM. USD. Maximum allotment amount (billions of FC)'},
    'M': {'code': 'RUSSD.TERMSFXSWAPS.TOMSPT.FCSELLDATE.B', 'description': 'Terms of Foreign Currency/RUB sell/buy FX Swaps. TOMSPT. USD. FC sell date'},
    'N': {'code': 'RUSSD.TERMSFXSWAPS.TOMSPT.RUBSELLDATE.B', 'description': 'Terms of Foreign Currency/RUB sell/buy FX Swaps. TOMSPT. USD. RUB sell date'},
    'O': {'code': 'RUSSD.TERMSFXSWAPS.TOMSPT.RUBINTERESTRATE.B', 'description': 'Terms of Foreign Currency/RUB sell/buy FX Swaps. TOMSPT. USD. RUB interest rate (% p.a.)'},
    'P': {'code': 'RUSSD.TERMSFXSWAPS.TOMSPT.FCINTERESTRATE.B', 'description': 'Terms of Foreign Currency/RUB sell/buy FX Swaps. TOMSPT. USD. FC interest rate (% p.a.)'},
    'Q': {'code': 'RUSSD.TERMSFXSWAPS.TOMSPT.BASESWAPRATE.B', 'description': 'Terms of Foreign Currency/RUB sell/buy FX Swaps. TOMSPT. USD. Base swap rate RUB/FC'},
    'R': {'code': 'RUSSD.TERMSFXSWAPS.TOMSPT.SWAPPOINTSRUB.B', 'description': 'Terms of Foreign Currency/RUB sell/buy FX Swaps. TOMSPT. USD. Swap points (rubles)'},
    'S': {'code': 'RUSSD.TERMSFXSWAPS.TOMSPT.MAXALLOTMENTAMOUNT.B', 'description': 'Terms of Foreign Currency/RUB sell/buy FX Swaps. TOMSPT. USD. Maximum allotment amount (billions of FC)'}
}

DATA_COLUMNS = list(EXCEL_HEADERS.keys())

# =============================================================================
# METADATA CONFIGURATION
# =============================================================================
DATA_FREQUENCY = 'Daily'
DATA_SOURCE_NAME = 'Central Bank of Russia'

def get_column_mapping_by_source(source: str, settlement: str):
    """Gets the list of Excel columns for a given source and settlement type."""
    mapping = {
        'swapinfosellvol': {
            'TODTOM': ['B', 'C'],
            'TOMSPT': ['D', 'E']
        },
        'swap_info_sell': {
            'TODTOM': ['F', 'G', 'H', 'I', 'J', 'K', 'L'],
            'TOMSPT': ['M', 'N', 'O', 'P', 'Q', 'R', 'S']
        }
    }
    return mapping.get(source, {}).get(settlement, [])
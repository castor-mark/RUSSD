"""
RUSSD Data Collection - Main Web Scraper
Bank of Russia (CBR) FX Swaps Data Extraction
"""

import time
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import pandas as pd  # <-- ADDED for Excel export

from config import (
    DATA_SOURCES, EXCEL_HEADERS, DATA_COLUMNS, CURRENCIES, SETTLEMENTS,
    DEFAULT_CURRENCY, SELECTORS, SOURCE_DATE_FORMAT, OUTPUT_DATE_FORMAT,
    DATE_INT_FORMAT, get_column_mapping_by_source
)

# =============================================================================
# SCRIPT CONFIGURATION
# =============================================================================
HEADLESS_MODE = False
DEBUG_MODE = True
WAIT_TIMEOUT = 15
PAGE_LOAD_DELAY = 2

# =============================================================================
# UTILITY FUNCTIONS (Unchanged)
# =============================================================================
def log_debug(message: str, prefix: str = "INFO"):
    if DEBUG_MODE: print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] [{prefix}] {message}")

def setup_driver():
    log_debug("Setting up Chrome WebDriver...")
    options = uc.ChromeOptions(); options.add_argument("--window-size=1920,1080"); options.add_argument("--lang=en-US")
    if HEADLESS_MODE: options.add_argument("--headless=new")
    try:
        driver = uc.Chrome(options=options)
        log_debug("WebDriver initialized successfully", "SUCCESS"); return driver
    except Exception as e:
        log_debug(f"Error creating driver: {str(e)}", "ERROR"); raise

def wait_for_clickable(driver, by, selector, timeout=WAIT_TIMEOUT):
    try: return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, selector)))
    except TimeoutException: log_debug(f"Timeout waiting for clickable element: {selector}", "WARNING"); return None

def wait_for_visible(driver, by, selector, timeout=WAIT_TIMEOUT):
    try: return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located((by, selector)))
    except TimeoutException: log_debug(f"Timeout waiting for element visibility: {selector}", "WARNING"); return None
        
def safe_click(driver, element, description="element"):
    try:
        driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'nearest'});", element)
        time.sleep(0.5); element.click(); log_debug(f"Clicked {description}"); return True
    except Exception as e:
        log_debug(f"Error clicking {description}: {str(e)}", "ERROR"); return False
        
# ... other utility functions remain the same ...
def wait_for_element(driver, by, selector, timeout=WAIT_TIMEOUT):
    try: return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, selector)))
    except TimeoutException: log_debug(f"Timeout waiting for element: {selector}", "WARNING"); return None
def parse_number(value_str):
    if not value_str or value_str in ['N/A', '']: return None
    try: return float(str(value_str).replace(',', '').replace(' ', '').strip())
    except (ValueError, AttributeError): log_debug(f"Could not parse number: {value_str}", "WARNING"); return None
def parse_date_to_standard(date_str):
    if not date_str: return None
    try: return datetime.strptime(date_str, SOURCE_DATE_FORMAT).strftime(OUTPUT_DATE_FORMAT)
    except ValueError: log_debug(f"Could not parse date to standard: {date_str}", "WARNING"); return None
def parse_date_to_integer(date_str):
    if not date_str: return None
    try: return int(datetime.strptime(date_str, SOURCE_DATE_FORMAT).strftime(DATE_INT_FORMAT))
    except ValueError: log_debug(f"Could not parse date to integer: {date_str}", "WARNING"); return None
def get_max_available_date(driver):
    datepicker = wait_for_element(driver, By.CSS_SELECTOR, 'div.datepicker-filter')
    if datepicker: return datepicker.get_attribute('data-max-date')
    log_debug("Could not find datepicker element", "WARNING"); return None


# =============================================================================
# NEW EXCEL EXPORT FUNCTION
# =============================================================================
def export_to_excel(data_row: dict):
    """Exports the collected data to an Excel file with the required format."""
    if not data_row.get('trade_date'):
        log_debug("No trade date found, skipping Excel export.", "WARNING")
        return

    # Generate the filename with today's date
    trade_date_obj = datetime.strptime(data_row['trade_date'], OUTPUT_DATE_FORMAT)
    filename = f"RUSSD_DATA_{trade_date_obj.strftime('%Y%m%d')}.xlsx"
    log_debug(f"Preparing to export data to {filename}...")

    # Prepare the three rows for the DataFrame
    header_codes = {'A': ''} # Column A is blank for headers
    header_desc = {'A': ''}
    for col_letter, headers in EXCEL_HEADERS.items():
        header_codes[col_letter] = headers['code']
        header_desc[col_letter] = headers['description']

    # Format the data row, moving trade_date to column 'A'
    output_data = data_row.copy()
    output_data['A'] = output_data.pop('trade_date', '')

    # Create DataFrame from the three rows
    df = pd.DataFrame([header_codes, header_desc, output_data])

    # Ensure correct column order from A to S
    column_order = ['A'] + DATA_COLUMNS
    df = df[column_order]

    try:
        # Write to Excel without pandas index or header
        df.to_excel(filename, index=False, header=False, engine='openpyxl')
        log_debug(f"Successfully created Excel file: {filename}", "SUCCESS")
    except Exception as e:
        log_debug(f"Failed to write Excel file: {e}", "ERROR")


# =============================================================================
# PAGE INTERACTION FUNCTIONS (Unchanged)
# =============================================================================
def handle_cookie_banner(driver):
    cookie_button = wait_for_clickable(driver, By.CSS_SELECTOR, SELECTORS['cookie_accept_button'], timeout=5)
    if cookie_button: log_debug("Cookie banner found."); safe_click(driver, cookie_button, "cookie accept button")
    else: log_debug("No cookie banner found.")

def set_currency(driver, currency: str):
    log_debug(f"Setting currency to {currency}...")
    currency_info = CURRENCIES.get(currency)
    if not currency_info: log_debug(f"Invalid currency: {currency}", "ERROR"); return False
    try:
        wait_for_element(driver, By.CSS_SELECTOR, "div.filter_placeholder"); time.sleep(1)
        all_filters = driver.find_elements(By.CSS_SELECTOR, "div.filter")
        currency_filter_div = next((f for f in all_filters if any(kw in f.text for kw in ["Currency", "Валюта"])), None)
        if not currency_filter_div: log_debug("Currency filter container not found", "ERROR"); return False
        currency_button = currency_filter_div.find_element(By.CSS_SELECTOR, SELECTORS['filter_button'])
        if currency_button.text.strip() == currency: log_debug(f"Currency already set to {currency}"); return True
        if not safe_click(driver, currency_button, "currency dropdown button"): return False
        if not wait_for_visible(driver, By.CSS_SELECTOR, SELECTORS['dropdown_content_visible']): log_debug("Currency dropdown panel did not appear", "ERROR"); return False
        label_selector = f"label[for='{currency_info['id']}']"
        label_element = wait_for_clickable(driver, By.CSS_SELECTOR, label_selector)
        if label_element and safe_click(driver, label_element, f"'{currency}' label"):
            time.sleep(PAGE_LOAD_DELAY); log_debug(f"Successfully set currency to {currency}", "SUCCESS"); return True
        else:
            log_debug(f"Could not find or click label for {currency}", "ERROR"); return False
    except Exception as e:
        log_debug(f"An unexpected error in set_currency: {e}", "ERROR"); return False

# ... other page interaction functions are unchanged ...
def set_settlement(driver, settlement: str):
    log_debug(f"Setting settlement to {settlement}...")
    settlement_info = SETTLEMENTS.get(settlement)
    if not settlement_info: log_debug(f"Invalid settlement: {settlement}", "ERROR"); return False
    try:
        wait_for_element(driver, By.CSS_SELECTOR, "div.filter_placeholder"); time.sleep(1)
        all_filters = driver.find_elements(By.CSS_SELECTOR, "div.filter")
        settlement_filter_div = next((f for f in all_filters if any(kw in f.text for kw in ["Settlement", "Сроки расчетов"])), None)
        if not settlement_filter_div: log_debug("Settlement filter container not found", "ERROR"); return False
        settlement_button = settlement_filter_div.find_element(By.CSS_SELECTOR, SELECTORS['filter_button'])
        if settlement_button.text.strip() == settlement: log_debug(f"Settlement already set to {settlement}"); return True
        if not safe_click(driver, settlement_button, "settlement dropdown button"): return False
        if not wait_for_visible(driver, By.CSS_SELECTOR, SELECTORS['dropdown_content_visible']): log_debug("Settlement dropdown panel did not appear", "ERROR"); return False
        label_selector = f"label[for='{settlement_info['id']}']"
        label_element = wait_for_clickable(driver, By.CSS_SELECTOR, label_selector)
        if label_element and safe_click(driver, label_element, f"'{settlement}' label"):
            time.sleep(PAGE_LOAD_DELAY); log_debug(f"Successfully set settlement to {settlement}", "SUCCESS"); return True
        else:
            log_debug(f"Could not find or click label for {settlement}", "ERROR"); return False
    except Exception as e:
        log_debug(f"An unexpected error in set_settlement: {e}", "ERROR"); return False
def set_date_to_latest(driver):
    log_debug("Setting date to latest available...")
    try:
        max_date = get_max_available_date(driver)
        if not max_date: return None
        datepicker_button = wait_for_clickable(driver, By.CSS_SELECTOR, SELECTORS['datepicker_button'])
        if not safe_click(driver, datepicker_button, "datepicker button"): return None
        time.sleep(1)
        date_to_input = wait_for_element(driver, By.CSS_SELECTOR, SELECTORS['date_to_input'])
        if date_to_input: driver.execute_script(f"arguments[0].value = '{max_date}';", date_to_input)
        date_from_input = wait_for_element(driver, By.CSS_SELECTOR, SELECTORS['date_from_input'])
        if date_from_input: driver.execute_script(f"arguments[0].value = '{max_date}';", date_from_input)
        time.sleep(1)
        apply_button = wait_for_clickable(driver, By.CSS_SELECTOR, SELECTORS['datepicker_apply'])
        if safe_click(driver, apply_button, "Apply date button"):
            time.sleep(PAGE_LOAD_DELAY); log_debug(f"Date successfully set to {max_date}", "SUCCESS"); return max_date
        return None
    except Exception as e:
        log_debug(f"An unexpected error in set_date: {e}", "ERROR"); return None
def extract_table_data(driver, source, settlement):
    log_debug(f"Extracting table data for {source} + {settlement}...")
    try:
        table = wait_for_element(driver, By.CSS_SELECTOR, SELECTORS['data_table'])
        if not table: log_debug("Data table not found", "ERROR"); return None
        soup = BeautifulSoup(table.get_attribute('outerHTML'), 'html.parser')
        rows = soup.select('tbody tr')
        if not rows: log_debug("No data rows found in table", "WARNING"); return {}
        cells = rows[0].find_all('td'); cell_values = [c.get_text(strip=True) for c in cells]
        log_debug(f"Raw cell values extracted: {cell_values}")
        mapping = get_column_mapping_by_source(source, settlement)
        data = {'trade_date': parse_date_to_standard(cell_values[0])}
        if source == 'swapinfosellvol' and len(cell_values) >= 3:
            data[mapping[0]] = parse_number(cell_values[1]); data[mapping[1]] = parse_number(cell_values[2])
        elif source == 'swap_info_sell' and len(cell_values) >= 8:
            data[mapping[0]] = parse_date_to_integer(cell_values[1]); data[mapping[1]] = parse_date_to_integer(cell_values[2])
            data[mapping[2]] = parse_number(cell_values[3]); data[mapping[3]] = parse_number(cell_values[4])
            data[mapping[4]] = parse_number(cell_values[5]); data[mapping[5]] = parse_number(cell_values[6])
            data[mapping[6]] = parse_number(cell_values[7])
        return data
    except Exception as e:
        log_debug(f"An unexpected error during table extraction: {e}", "ERROR"); return None

# =============================================================================
# MAIN WORKFLOW (Unchanged)
# =============================================================================
def collect_data_from_source(driver, source_key, currency):
    source_info = DATA_SOURCES[source_key]; url = source_info['url']
    log_debug(f"\n{'='*80}\nCollecting from: {source_key} at {url}\n{'='*80}")
    driver.get(url); handle_cookie_banner(driver)
    if not set_currency(driver, currency) or not set_date_to_latest(driver):
        log_debug(f"Halting collection from {source_key} due to setup failure", "ERROR"); return None
    combined_data = {}
    for settlement in source_info['settlements']:
        log_debug(f"\n--- Collecting data for settlement: {settlement} ---")
        if not set_settlement(driver, settlement): continue
        data = extract_table_data(driver, source_key, settlement)
        if data is not None:
            combined_data.update(data); log_debug(f"Successfully collected data for {settlement}", "SUCCESS")
    return combined_data

def run_full_collection(currency):
    log_debug("\n" + "="*80 + "\nSTARTING FULL DATA COLLECTION\n" + "="*80)
    driver = None
    try:
        driver = setup_driver()
        data_row = {col: None for col in DATA_COLUMNS}
        volume_data = collect_data_from_source(driver, 'swapinfosellvol', currency)
        if volume_data: data_row.update(volume_data)
        terms_data = collect_data_from_source(driver, 'swap_info_sell', currency)
        if terms_data: data_row.update(terms_data)
        log_debug("\n" + "="*80 + "\nDATA COLLECTION COMPLETE\n" + "="*80)
        return data_row
    except Exception as e:
        log_debug(f"A critical error occurred in the full collection process: {e}", "ERROR"); return None
    finally:
        if driver: log_debug("Closing WebDriver..."); driver.quit()

# =============================================================================
# MAIN EXECUTION (Updated to call export_to_excel)
# =============================================================================
def main():
    start_time = time.time()
    print("\n" + "="*80 + "\nRUSSD DATA COLLECTION SCRIPT\n" + "="*80)
    
    final_data = run_full_collection(DEFAULT_CURRENCY)
    
    if final_data:
        print("\n" + "="*80 + "\nCOLLECTED DATA SUMMARY\n" + "="*80)
        if final_data.get('trade_date'):
            print(f"Trade Date: {final_data.get('trade_date')}\n")
            for col in DATA_COLUMNS:
                value = final_data.get(col); header_info = EXCEL_HEADERS[col]
                print(f"Column {col} ({header_info['code']}): {value}")
            
            print("\n✅ Data collection successful!")
            
            # --- ADDED: Call the export function ---
            export_to_excel(final_data)

        else:
            print("\n❌ Collection finished, but no data was extracted. Please check the logs.")
    else:
        print("\n❌ Data collection failed critically.")
        
    elapsed_time = time.time() - start_time
    print(f"\n⏱️  Total collection time: {elapsed_time:.2f} seconds")

if __name__ == "__main__":
    main()
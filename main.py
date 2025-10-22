"""
RUSSD Data Collection - Main Script
Bank of Russia (CBR) FX Swaps Data Extraction
"""

import time
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from bs4 import BeautifulSoup
import undetected_chromedriver as uc

from config import (
    DATA_SOURCES, EXCEL_HEADERS, DATA_COLUMNS, CURRENCIES, SETTLEMENTS,
    DEFAULT_CURRENCY, SELECTORS, SOURCE_DATE_FORMAT, OUTPUT_DATE_FORMAT,
    DATE_INT_FORMAT, get_column_mapping_by_source
)

HEADLESS_MODE = False
DEBUG_MODE = True
WAIT_TIMEOUT = 10
PAGE_LOAD_DELAY = 2

def log_debug(message, prefix="INFO"):
    if DEBUG_MODE:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [{prefix}] {message}")

def setup_driver():
    options = uc.ChromeOptions()
    if HEADLESS_MODE:
        options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = uc.Chrome(options=options, version_main=None)
    return driver

def wait_for_clickable(driver, by, selector, timeout=WAIT_TIMEOUT):
    try:
        return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, selector)))
    except TimeoutException:
        return None

def safe_click(element, description="element"):
    try:
        element.click()
        log_debug(f"Clicked {description}")
        return True
    except Exception as e:
        log_debug(f"Error clicking {description}: {e}", "ERROR")
        return False

def parse_number(value_str):
    if not value_str:
        return None
    try:
        return float(str(value_str).replace(',', '').strip())
    except:
        return None

def parse_date_to_standard(date_str):
    try:
        return datetime.strptime(date_str, SOURCE_DATE_FORMAT).strftime(OUTPUT_DATE_FORMAT)
    except:
        return None

def parse_date_to_integer(date_str):
    try:
        return int(datetime.strptime(date_str, SOURCE_DATE_FORMAT).strftime(DATE_INT_FORMAT))
    except:
        return None

def set_currency(driver, currency='USD'):
    log_debug(f"Setting currency to {currency}...")
    try:
        buttons = driver.find_elements(By.CSS_SELECTOR, SELECTORS['currency_button'])
        for btn in buttons:
            if btn.text.strip() in ['USD', 'EUR', 'CNY']:
                safe_click(btn, "currency dropdown")
                time.sleep(1)
                radio = wait_for_clickable(driver, By.CSS_SELECTOR, f"input[name='UniDbQuery.Cur'][value='{CURRENCIES[currency]['value']}']", 5)
                if radio:
                    safe_click(radio, f"currency {currency}")
                    time.sleep(PAGE_LOAD_DELAY)
                    return True
        return False
    except Exception as e:
        log_debug(f"Error setting currency: {e}", "ERROR")
        return False

def set_settlement(driver, settlement):
    log_debug(f"Setting settlement to {settlement}...")
    try:
        buttons = driver.find_elements(By.CSS_SELECTOR, SELECTORS['settlement_button'])
        for btn in buttons:
            if btn.text.strip() in ['TODTOM', 'TOMSPT']:
                safe_click(btn, "settlement dropdown")
                time.sleep(1)
                radio = wait_for_clickable(driver, By.CSS_SELECTOR, f"input[name='UniDbQuery.P1'][value='{SETTLEMENTS[settlement]['value']}']", 5)
                if radio:
                    safe_click(radio, f"settlement {settlement}")
                    time.sleep(PAGE_LOAD_DELAY)
                    return True
        return False
    except Exception as e:
        log_debug(f"Error setting settlement: {e}", "ERROR")
        return False

def set_date_to_latest(driver):
    try:
        datepicker = driver.find_element(By.CSS_SELECTOR, 'div.datepicker-filter')
        max_date = datepicker.get_attribute('data-max-date')
        if not max_date:
            return False, None
        
        date_btn = wait_for_clickable(driver, By.CSS_SELECTOR, SELECTORS['date_button'])
        if date_btn:
            safe_click(date_btn, "date picker")
            time.sleep(1)
            
            driver.execute_script(f"document.querySelector('{SELECTORS['date_input_to']}').value = '{max_date}';")
            driver.execute_script(f"document.querySelector('{SELECTORS['date_input_from']}').value = '{max_date}';")
            
            apply_btn = wait_for_clickable(driver, By.CSS_SELECTOR, SELECTORS['date_apply_button'], 5)
            if apply_btn:
                safe_click(apply_btn, "apply button")
                time.sleep(PAGE_LOAD_DELAY)
                return True, max_date
        return False, None
    except Exception as e:
        log_debug(f"Error setting date: {e}", "ERROR")
        return False, None

def extract_table_data(driver, source_page, settlement):
    try:
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table = soup.find('table', {'class': 'data'})
        if not table:
            return None
        
        headers = [th.get_text(strip=True) for th in table.find('thead').find('tr').find_all('th')]
        rows = table.find('tbody').find_all('tr')
        if not rows:
            return None
        
        cells = rows[0].find_all('td')
        row_data = {headers[i]: cells[i].get_text(strip=True) for i in range(min(len(headers), len(cells)))}
        
        excel_data = {}
        for col_letter in get_column_mapping_by_source(source_page, settlement):
            col_info = EXCEL_HEADERS[col_letter]
            value = None
            for header, cell_value in row_data.items():
                if col_info['table_column'].lower() in header.lower():
                    value = cell_value
                    break
            
            if value:
                if col_info['data_type'] == 'float':
                    excel_data[col_letter] = parse_number(value)
                elif col_info['data_type'] == 'date_int':
                    excel_data[col_letter] = parse_date_to_integer(value)
                else:
                    excel_data[col_letter] = value
        
        if 'Trade date' in row_data:
            excel_data['_trade_date'] = parse_date_to_standard(row_data['Trade date'])
        
        return excel_data
    except Exception as e:
        log_debug(f"Error extracting table: {e}", "ERROR")
        return None

def collect_from_source(driver, source_name, currency='USD'):
    log_debug(f"\n{'='*80}\nCOLLECTING FROM: {source_name.upper()}\n{'='*80}")
    
    driver.get(DATA_SOURCES[source_name]['url'])
    time.sleep(PAGE_LOAD_DELAY)
    
    if not set_currency(driver, currency):
        return None
    
    success, date = set_date_to_latest(driver)
    if not success:
        return None
    
    collected = {'source': source_name, 'currency': currency, 'date': date, 'settlements': {}}
    
    for settlement in ['TODTOM', 'TOMSPT']:
        if set_settlement(driver, settlement):
            data = extract_table_data(driver, source_name, settlement)
            if data:
                collected['settlements'][settlement] = data
    
    return collected

def main():
    print("\n" + "="*80)
    print("RUSSD DATA COLLECTION - STARTING")
    print("="*80 + "\n")
    
    driver = setup_driver()
    all_data = {'sources': {}}
    
    try:
        for source in DATA_SOURCES.keys():
            data = collect_from_source(driver, source, DEFAULT_CURRENCY)
            if data:
                all_data['sources'][source] = data
        
        consolidated = {}
        trade_date = None
        
        for source_data in all_data['sources'].values():
            for settlement_data in source_data.get('settlements', {}).values():
                if '_trade_date' in settlement_data and not trade_date:
                    trade_date = settlement_data['_trade_date']
                for col, val in settlement_data.items():
                    if col != '_trade_date':
                        consolidated[col] = val
        
        consolidated['A'] = trade_date
        all_data['consolidated_row'] = consolidated
        
        print("\n" + "="*80)
        print("✅ DATA COLLECTION COMPLETED")
        print(f"📅 Trade Date: {trade_date}")
        print(f"📊 Data Points: {len(consolidated) - 1}")
        print("="*80 + "\n")
        
        return all_data
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        driver.quit()

if __name__ == "__main__":
    result = main()
    if result:
        print("✅ Success! Ready for Excel export")
    else:
        print("❌ Failed - check logs")
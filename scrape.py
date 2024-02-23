#%%
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common import NoSuchElementException, ElementNotInteractableException, StaleElementReferenceException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pathlib import Path
import time
import re
#%%
WAIT_TIMEOUT = 10
DRIVER_PATH = str((Path(__file__).parent/"chromedriver_mac_arm64/chromedriver").resolve())
DOWNLOAD_PATH = str((Path(__file__).parent/"theses-pdfs").resolve())
pdf_file_pattern = re.compile(r"(.*\.pdf)")
#%%
def collect_links_in_page(driver):
    errors = [NoSuchElementException, ElementNotInteractableException, StaleElementReferenceException]
    wait = WebDriverWait(driver, timeout=WAIT_TIMEOUT, poll_frequency=.2, ignored_exceptions=errors)
    row_elem = (By.CLASS_NAME, "row")
    wait.until(EC.visibility_of_all_elements_located(row_elem))
    rows = driver.find_elements(*row_elem)
    num_rows = len(rows)
    row_num = 0
    while row_num<num_rows:
        # Get the rows again
        wait.until(EC.visibility_of_all_elements_located(row_elem))
        rows = driver.find_elements(*row_elem)
        # find the current row to check
        row = rows[row_num]
        try:
            # Can only download PDF for thesis which have "Open Access" badge
            badge = row.find_element(By.CLASS_NAME, "badge-secondary")
            if badge.text != "Open Access":
                continue
            elem = row.find_elements(By.XPATH, ".//a[@href]")[1]
            title = elem.text
            # The thesis title
            print(title)
            # Click the thesis link and download the PDF
            elem.click()
            download_pdf(driver)
            # Go back to list
            driver.back()
        except NoSuchElementException as e:
            # print(e)
            continue
        finally:
            row_num+=1

def wait_till_downloaded(file:Path):
    while True:
        if file.exists():
            return True

def download_pdf(driver,download_dir: Path = Path(DOWNLOAD_PATH)):
    errors = [NoSuchElementException, ElementNotInteractableException, StaleElementReferenceException]
    wait = WebDriverWait(driver, timeout=WAIT_TIMEOUT, poll_frequency=.2, ignored_exceptions=errors)
    pdf_element = (By.PARTIAL_LINK_TEXT,"pdf")
    wait.until(EC.visibility_of_element_located(pdf_element))
    pdf_link = driver.find_element(*pdf_element)
    pdf_file = download_dir/pdf_file_pattern.search(pdf_link.text).group(1)
    if not pdf_file.exists():
        pdf_link.click()
        wait_till_downloaded(pdf_file)
        print(f"\t pdf_downloaded: {pdf_file.name}")
        driver.back()
    else:
        print("File Already Downloaded")
#%%
if __name__ == "__main__":
    service = Service(executable_path=DRIVER_PATH)
    options = Options()
    # options.add_argument("--window-size=1920,1200")
    options.add_argument("--headless=new")
    options.add_experimental_option('prefs', {
    "download.default_directory": DOWNLOAD_PATH, #Change default directory for downloads
    "download.prompt_for_download": False, #To auto download the file
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
    })
    #%%
    driver = webdriver.Chrome(options=options)
    # main page for Faculty of Science theses
    driver.get("https://helda.helsinki.fi/collections/b9c99799-fd50-4802-a8dd-f1d833b10794")
    errors = [NoSuchElementException, ElementNotInteractableException, StaleElementReferenceException]
    wait = WebDriverWait(driver, timeout=WAIT_TIMEOUT, poll_frequency=.2, ignored_exceptions=errors)
    # how to get different elements 
    next_page_link = (By.XPATH,'//ul[@class="pagination"]/li[@aria-current="page"]/following-sibling::li[1]') # for the next page
    page_link = (By.XPATH,'//ul[@class="pagination"]/li[@aria-current="page"]') # for the current page
    advance_elem = (By.XPATH,'//ul[@class="pagination"]/li[@aria-current="page"]/following-sibling::li[last()]') # the button to advance to the next page
    wait.until(EC.visibility_of_element_located(next_page_link))
    next_page_text = driver.find_element(*next_page_link)
    page_num =1 
    start_page = 218
    if start_page == 1:
        # collect for page 1
        collect_links_in_page(driver)
    while next_page_text != "»":
        # click advance to next page button
        wait.until(EC.visibility_of_element_located(advance_elem))
        button = driver.find_element(*advance_elem)
        button.click()
        # find the current and next page values
        wait.until(EC.visibility_of_element_located(page_link))
        page_num = driver.find_element(*page_link).text
        next_page_text = driver.find_element(By.XPATH,'//ul[@class="pagination"]/li[@aria-current="page"]/following-sibling::li[1]').text
        print(f"{page_num=}")
        if int(page_num.split('\n')[0]) < start_page:
            continue
        # perform task
        collect_links_in_page(driver)
    # %%
    driver.quit()
# %%


import time
from typing import List

from selenium.webdriver.chrome.webdriver import WebDriver

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

from src.core.form import get_form_data, fill_form_page, get_next_button
from src.core.manual_fill import JobApplication
import concurrent.futures
import functools
from logger import get_logger
logger = get_logger(__name__)



def timeout(seconds=60):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(func, *args, **kwargs)
                try:
                    return future.result(timeout=seconds)
                except concurrent.futures.TimeoutError:
                    raise TimeoutError(f"{func.__name__} did not complete within {seconds} seconds.")
        return wrapper
    return decorator

@timeout(60)
def apply_job(job: JobApplication, driver: WebDriver, skipped_jobs: List, visited_jobs: List):
    try:

        # job.click()
        # time.sleep(2)

        # job_details = driver.find_element(By.CSS_SELECTOR, 'div.jobs-details')
        job_details = driver.find_element(
            By.XPATH,
            "//*[normalize-space(@class)='job-view-layout jobs-details']"
        )
        job_content = job.job_details
        job_url = job.job_url


        # job_content = job_details.find_element(By.CLASS_NAME, 'jobs-description__content').get_attribute('innerText')
        # job_url = job.get_attribute('baseURI').rsplit('/', 2)[0] + '/view/' + job.get_attribute('data-job-id')
        # visited_job = JobApplication(job_url, job.text, job_content)

        logger.debug(f"Applying to job:\n {job.job_summary}")

        all_applies = job_details.find_elements(By.CSS_SELECTOR, "button.jobs-apply-button")
        easy_applies = [b for b in all_applies if  'easy apply' in b.find_element(By.TAG_NAME, "span").text.lower()]
        easy_apply = easy_applies[0] if easy_applies else None
        apply_text = easy_apply.find_element(By.TAG_NAME, "span").text if easy_applies else None

        if not apply_text or 'easy apply' not in apply_text.lower():
            raise NoSuchElementException("Easy Apply button not found")
        easy_apply.click()
        time.sleep(2)
    except NoSuchElementException as e:
        logger.debug("Easy apply not found. Checking if already applied")
        try:
            applied = driver.find_element(By.CSS_SELECTOR,"button.artdeco-inline-feedback--success")
            logger.debug(f"Already applied to job.")
            # job_apply = JobApplication(job_url, job.job_summary,job_content, failed_reason="Already Applied")
            # skipped_jobs.append(job_apply.__dict__)
            return
        except Exception as e:
            logger.debug("Job not already applied & Easy apply not found")
            logger.debug("Skipping application.")
            raise Exception("Easy Apply unsupported & Have not applied already")



    try:
        form_data, form_element, dialog = get_form_data(driver)
        status, button_found, button_element = get_next_button(dialog)
        invalid_fields = []
        while status and not invalid_fields:
            button_element.click()
            time.sleep(2)
            form_data, form_element, dialog = get_form_data(driver)
            if form_data:
                invalid_fields = form_element.find_elements(By.CLASS_NAME, "fb-dash-form-element__error-field") +\
                                form_element.find_elements(By.CLASS_NAME, "artdeco-inline-feedback--error")
            if invalid_fields:
                fill_form_page(form_data, form_element)
                logger.debug("Form filled completely")
                invalid_fields = []
                time.sleep(1.5)

            status, button_found, button_element = get_next_button(dialog)

            # if invalid fields. fill form with error desc

            # form_data, form_element = get_form_data(driver)

            # status, button_found, button_element = get_next_button(form_element)
            if button_found == 'submit':
                try:
                    follow_company = driver.find_element(By.CSS_SELECTOR, 'label[for="follow-company-checkbox"]')
                    follow_company.click()
                except:
                    pass
                button_element.click()
                time.sleep(3)
                break
            # button_element.click()
            # time.sleep(2)

            # invalid_fields = form_element.find_elements(By.CLASS_NAME, "fb-dash-form-element__error-field")
                             # form_element.find_elements(By.CLASS_NAME, "artdeco-inline-feedback--error")


                # print("Invalid Fill. Skipping Application.")
                # job_apply = JobApplication(job_url, job.text,job_content, failed_reason="Invalid Form fill", invalid_fields=[i.text for i in invalid_fields])
                # skipped_jobs.append(job_apply)
                # raise InvalidArgumentException()

    except Exception as e:
        logger.debug(f"Form fill failed: {e}")

        # directly raising error.
        # job_apply = JobApplication(job_url, job.job_summary, job_content, failed_reason=str(e))
        # skipped_jobs.append(job_apply.__dict__)

        dismiss_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Dismiss']")
        logger.debug("Exiting form")
        dismiss_button.click()
        dismiss_button = driver.find_element(By.CSS_SELECTOR,
                                             "button[data-control-name='discard_application_confirm_btn']")
        dismiss_button.click()
        raise Exception(f"Form fill failed: {e}")
    else:
        dismiss_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Dismiss']")
        logger.debug("Exiting form")
        dismiss_button.click()


def load_all_job_cards(driver, job_card_selector="div.job-card-list", scroll_pause=1.0, max_attempts=3):
    last_count = 0
    attempts = 0

    while attempts < max_attempts:
        jobs = driver.find_elements(By.CSS_SELECTOR, job_card_selector)
        driver.execute_script("arguments[0].scrollIntoView();", jobs[-1])
        time.sleep(scroll_pause)
        new_jobs = driver.find_elements(By.CSS_SELECTOR, job_card_selector)
        if len(new_jobs) == last_count:
            attempts += 1
        else:
            attempts = 0
        last_count = len(new_jobs)
    return new_jobs


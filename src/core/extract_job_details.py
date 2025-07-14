import time
from selenium.webdriver.common.by import By

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.webdriver import WebDriver

from manual_fill import JobApplication


def extract(job: WebElement, driver: WebDriver):

    job.click()
    time.sleep(1)

    # job_details = driver.find_element(By.CSS_SELECTOR, 'div.jobs-details')
    job_details = driver.find_element(
        By.XPATH,
        "//*[normalize-space(@class)='job-view-layout jobs-details']"
    )
    job_content = job_details.find_element(By.CLASS_NAME, 'jobs-description__content').get_attribute('innerText')
    job_url: str = job.get_attribute('baseURI').rsplit('/', 2)[0] + '/view/' + job.get_attribute('data-job-id')
    job_url = job_url.replace("/collections", "")
    hiring_section = driver.find_element(By.CSS_SELECTOR, 'div.jobs-details')

    # all_applies = job_details.find_elements(By.CSS_SELECTOR, "button.jobs-apply-button")
    # easy_applies = [b for b in all_applies if 'easy apply' in b.find_element(By.TAG_NAME, "span").text.lower()]
    easy_apply = True if 'easy apply' in job.text.lower() else False

    # application_link = job_details.find_elements(By.ID, "jobs-apply-see-application-link")
    applied = True if 'applied' in job.text.lower() else False
    visited_job = JobApplication(job_url, job.text, job_content, easy_apply=easy_apply, applied=applied)

    return visited_job

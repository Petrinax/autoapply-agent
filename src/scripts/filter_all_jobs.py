import os
import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from src.core.manual_fill import JobApplication

load_dotenv('./.env')

driver = webdriver.Chrome()

driver.get("https://www.linkedin.com/login")

email = driver.find_element(By.ID, "username")
email.send_keys(os.getenv("LINKEDIN_EMAIL"))

password = driver.find_element(By.ID, "password")
password.send_keys(os.getenv("LINKEDIN_PASSWORD"))
password.send_keys(Keys.RETURN)
time.sleep(4)


driver.get("https://www.linkedin.com/jobs/")

search_box = driver.find_element(By.CSS_SELECTOR, "input[aria-label='Search by title, skill, or company']")
search_box.clear()
search_box.send_keys("Software Engineer")
time.sleep(1)

search_box.send_keys(Keys.RETURN)
time.sleep(3)

location_box = driver.find_element(By.CSS_SELECTOR, "input[aria-label='City, state, or zip code']")
location_box.clear()
location_box.send_keys("India")
time.sleep(1)

location_box.send_keys(Keys.RETURN)
time.sleep(3)

jobs_visited = []


jobs = driver.find_elements(By.CSS_SELECTOR, "div.job-card-list")

for job in jobs:
    job.click()
    time.sleep(2)

    job_details = driver.find_element(By.CSS_SELECTOR, 'div.jobs-details')
    job_content = job_details.find_element(By.CLASS_NAME, 'jobs-description__content').get_attribute('innerText')
    job_url = job.get_attribute('baseURI').rsplit('/', 2)[0] + '/view/' + job.get_attribute('data-job-id')
    visited_job = JobApplication(job_url, job.text, job_content)
    jobs_visited.append(visited_job)

print("Completed")

if __name__ == '__main__':
    pass
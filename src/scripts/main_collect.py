import json
import os
import time

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By

from src.core.extract_job_details import extract
from src.core.jobs import load_all_job_cards
from selenium.webdriver.chrome.options import Options

from src.core.manual_fill import JobApplication
from tqdm import tqdm

load_dotenv('../../.env')

chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{os.getenv('DEBUG_PORT')}")
driver = webdriver.Chrome(options=chrome_options)
time.sleep(2)

# driver.get("https://www.linkedin.com/login")
#
# email = driver.find_element(By.ID, "username")
# email.send_keys(os.getenv("LINKEDIN_EMAIL"))
#
# password = driver.find_element(By.ID, "password")
# password.send_keys(os.getenv("LINKEDIN_PASSWORD"))
#
# checkbox = driver.find_element(By.ID, 'rememberMeOptIn-checkbox')
# if checkbox.is_selected():
#     driver.execute_script("arguments[0].click();", checkbox)
#
# password.send_keys(Keys.RETURN)
# time.sleep(4)
#
#
driver.get("https://www.linkedin.com/jobs/")
time.sleep(4)

#
# retry = 3
# while retry:
#     try:
#         search_box = driver.find_element(By.CSS_SELECTOR, "input[aria-label='Search by title, skill, or company']")
#         retry = 0
#     except Exception as e:
#         retry-=1
# #
# #
# # search_box.clear()
# # search_box.send_keys("Software Engineer")
# # time.sleep(1)
# #
# # search_box.send_keys(Keys.RETURN)
# # time.sleep(3)
# #
# # location_box = driver.find_element(By.CSS_SELECTOR, "input[aria-label='City, state, or zip code']")
# # location_box.clear()
# # location_box.send_keys("India")
# # time.sleep(1)
# #
# # location_box.send_keys(Keys.RETURN)
# # time.sleep(3)
#
# easy_apply_button = driver.find_element(By.XPATH, "//button[text()='Easy Apply']")
# easy_apply_button.click()
# time.sleep(2)
#

print("Reading from file")
with open('job_links_ea.json', 'r') as f:
    all_jobs = json.load(f)
# all_jobs=[]
next_page_elements = True

while next_page_elements:
    next_page_elements = driver.find_elements(By.CSS_SELECTOR, '[aria-label="View next page"]')

    jobs_visited: list[JobApplication] = []
    manual_fill_queue = []

    jobs = load_all_job_cards(driver)
    print(f"Total jobs loaded: {len(jobs)}")

    # for idx, job in enumerate(jobs):
    #     try:
    #         obj = extract(job, driver)
    #         jobs_visited.append(obj)
    #         print(f"Visited: {idx+1}/{total}", end='\r', flush=True)
    #         # apply_job(job, driver, manual_fill_queue, jobs_visited)
    #         # obj.applied = True
    #     except Exception as e:
    #         print(e)
    #         pass

    # def process_job(idx_job):
    #     idx, job = idx_job
    #     try:
    #         obj = extract(job, driver)
    #         return (idx, obj, None)
    #     except Exception as e:
    #         return (idx, None, e)


    # with ThreadPoolExecutor(max_workers=25) as executor:  # Adjust max_workers as needed
    #     futures = {executor.submit(process_job, (idx, job)): idx for idx, job in enumerate(jobs)}
    #     completed = 0
    #     total = len(jobs)
    #     jobs_visited = []
    #     for future in as_completed(futures):
    #         idx, obj, error = future.result()
    #         completed += 1
    #         # print(f"Visited: {completed}/{total}", end='\r', flush=True)
    #         if obj:
    #             jobs_visited.append(obj)
    #         if error:
    #             print(error)

    jobs_visited = []
    total = len(jobs)
    for job in tqdm(jobs, desc="Processing jobs"):
        try:
            obj = extract(job, driver)
            jobs_visited.append(obj)
        except Exception as e:
            print(e)

    # print(jobs_visited)
    # print(manual_fill_queue)

    print(f"Adding {len(jobs_visited)} new jobs")

    with open("job_links_ea.json", "w") as f:
        for job in jobs_visited:
            all_jobs.append(job.__dict__)
        json.dump(all_jobs, f, indent=2)

    if next_page_elements:
        next_page_elements[0].click()
        time.sleep(5)
    else:
        next_page_elements=False




if __name__ == '__main__':

    print("Completed")







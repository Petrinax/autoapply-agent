
import json
import os
import time

from dotenv import load_dotenv
from selenium import webdriver

from src.core.jobs import apply_job
from selenium.webdriver.chrome.options import Options

from src.core.manual_fill import JobApplication
from src.core.logger import get_logger
from tqdm import tqdm

load_dotenv('../../.env')

chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{os.getenv('DEBUG_PORT')}")
driver = webdriver.Chrome(options=chrome_options)
time.sleep(2)

logger = get_logger(__name__)

logger.debug("Reading from file")
with open('manual_fill_queue.json', 'r') as f:
    all_jobs = json.load(f)
    all_jobs = [ v for  v in all_jobs if v.get('easy_apply') and not v.get('applied')]

# Track start time
start_time = time.time()

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

# Save progress after each job (visited, applied, manual fill)
import json

def save_progress(jobs_visited, jobs_applied, manual_fill_queue):
    try:
        with open("jobs_visited.json", "w", encoding="utf-8") as f:
            json.dump(jobs_visited, f, indent=2)
        with open("jobs_applied.json", "w", encoding="utf-8") as f:
            json.dump(jobs_applied, f, indent=2)
        with open("manual_fill_queue.json", "w", encoding="utf-8") as f:
            json.dump([job if isinstance(job, dict) else job.__dict__ for job in manual_fill_queue], f, indent=2)
    except Exception as e:
        logger.debug(f"Error saving progress: {e}")


jobs_visited: list[dict] = []
jobs_applied: list[dict] = []
manual_fill_queue: list[dict] = []
total = len(all_jobs)
# Use tqdm for progress bar with custom postfix
with tqdm(all_jobs, desc="Jobs Visited", unit="job") as pbar:
    for job in pbar:
        try:
            obj= JobApplication(**job)
            driver.get(obj.job_url)
            time.sleep(4)
            jobs_visited.append(job)
            apply_job(obj, driver, [], [])
            job['applied'] = True
            jobs_applied.append(job)
        except Exception as e:
            job['failed_reason'] = str(e).strip()[:500]
            manual_fill_queue.append(job)
            logger.debug(e)
            pass
        except KeyboardInterrupt as e:
            job['failed_reason'] = str(e).strip()[:500]
            manual_fill_queue.append(job)
            print("Application Interrupt. Saving progress till now...")
            save_progress(jobs_visited, jobs_applied, manual_fill_queue)
            break
        # Update progress bar postfix
        pbar.set_postfix({
            'applied': len(jobs_applied),
            'manual_fill': len(manual_fill_queue)
        })

save_progress(jobs_visited, jobs_applied, manual_fill_queue)

# Track end time and calculate duration
end_time = time.time()
total_time_taken = end_time - start_time

# Break total_time_taken into days, hours, minutes, seconds if large
days = int(total_time_taken // 86400)
hours = int((total_time_taken % 86400) // 3600)
minutes = int((total_time_taken % 3600) // 60)
seconds = total_time_taken % 60

if days > 0:
    total_time_taken_str = f"{days}d {hours}h {minutes}m {seconds:.2f}s"
elif hours > 0:
    total_time_taken_str = f"{hours}h {minutes}m {seconds:.2f}s"
elif minutes > 0:
    total_time_taken_str = f"{minutes}m {seconds:.2f}s"
else:
    total_time_taken_str = f"{seconds:.2f}s"

# Open a custom made Thank You Page using driver
try:
    import os
    import sys
    current_dir = os.path.abspath(os.getcwd())
    logger.debug(f"Current directory: {current_dir}")
    # Prepare summary details as query parameters
    thank_you_url: str = os.getenv("THANK_YOU_PAGE_URL", f"file://{os.path.join(current_dir, 'thank_you.html')}")
    from urllib.parse import urlencode, urlparse, urlunparse, parse_qs
    summary_params = {
        'total': total,
        'visited': len(jobs_visited),
        'applied': len(jobs_applied),
        'manual_fill': len(manual_fill_queue),
        'time_taken': f"{total_time_taken:.2f}"
    }
    thank_you_url += '?' + urlencode(summary_params)
    driver.get(thank_you_url)
except Exception as e:
    logger.debug(f"Could not open Thank You page: {e}")

if __name__ == '__main__':
    logger.info("Summary:\n")
    logger.info(f"Total jobs received: {total}")
    logger.info(f"Jobs visited: {len(jobs_visited)}")
    logger.info(f"Jobs applied: {len(jobs_applied)}")
    logger.info(f"Jobs queued for manual fill: {len(manual_fill_queue)}\n")

    # if jobs_applied:
    #     print("Applied Jobs:")
    #     for job in jobs_applied:
    #         print(f"- {job.get('job_summary', job.get('job_url', 'N/A'))}")
    #     print()
    

    # if jobs_visited:
    #     print("Visited Jobs:")
    #     for job in jobs_visited:
    #         print(f"- {job.get('job_summary', job.get('job_url', 'N/A'))}")
    #     print()


    # with open("manual_fill_queue.json", "w", encoding="utf-8") as f:
    #     json.dump(manual_fill_queue, f, indent=2)
    pass
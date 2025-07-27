import csv
import datetime
import logging
import os
import pathlib
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any

import dotenv
from google import genai
from langchain.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from tqdm import tqdm
import threading
import time
import queue

dotenv.load_dotenv()

# Configure logging
logging.basicConfig(level=logging.WARN, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, max_calls: int, period: float):
        self.max_calls = max_calls
        self.period = period
        self.lock = threading.Lock()
        self.calls = []  # timestamps of recent calls
        self.condition = threading.Condition(self.lock)

    def acquire(self):
        with self.condition:
            while True:
                now = time.time()
                # Remove timestamps older than period
                self.calls = [t for t in self.calls if now - t < self.period]
                if len(self.calls) < self.max_calls:
                    self.calls.append(now)
                    return
                # Wait until the earliest call is outside the window
                wait_time = self.period - (now - self.calls[0])
                if wait_time > 0:
                    self.condition.wait(timeout=wait_time)
                else:
                    # Shouldn't happen, but just in case
                    time.sleep(0.1)

    def notify(self):
        with self.condition:
            self.condition.notify_all()

class ATSAgent:
    def __init__(self, user_profile: str, gemini_api_key: str, gemini_model_name: str = "gemini-2.5-flash", rate_limiter=None):
        self.user_profile = user_profile
        self.model_name = "gemini-2.5-flash-lite"
        self.gemini_client = genai.Client()
        self.model_info = self.gemini_client.models.get(model=self.model_name)
        self.llm: GoogleGenerativeAI = GoogleGenerativeAI(model=self.model_name, google_api_key=gemini_api_key, temperature=0.4)
        with open("./src/prompts/ATS_SCORE_PROMPT.txt") as f:
            self.ATS_SCORE_PROMPT  = PromptTemplate(
                input_variables=["profile", "job"],
                template=f.read(),
            )
        self.rate_limiter = rate_limiter

    def analyze_job(self, job_description: str) -> Dict[str, Any]:
        if self.rate_limiter:
            self.rate_limiter.acquire()
        job_description = job_description.lower()
        result = self._score_and_explain_relevance_and_ats(job_description)
        scores = {
            "relevance_score": result["relevance_score"],
            "relevance_explanation": result["relevance_explanation"],
            "ats_score": result["ats_score"],
            "ats_score_explanation": result["ats_explanation"],
            "selection_chance": None  # Will be calculated below
        }
        scores["selection_chance"] = self._score_selection_chance(scores)
        if self.rate_limiter:
            self.rate_limiter.notify()
        return scores

    def _score_and_explain_relevance_and_ats(self, job_description: str) -> Dict[str, Any]:
        prompt_str = self.ATS_SCORE_PROMPT.format(profile=self.user_profile, job=job_description)


        response = self.llm.invoke(prompt_str)
        
        import datetime
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y_%m_%d_%H_%M_%S_%f")
        with open(f"./src/data/request_logs/{timestamp}_request", "w") as f:
            f.write(prompt_str)
        with open(f"./src/data/request_logs/{timestamp}_response", "w") as f:
            f.write(response)


        logger.info("LLM combined relevance+ATS response: %s", response)
        import json
        try:
            result = json.loads(self._extract_json(response))
            result["relevance_score"] = int(result["relevance_score"])
            result["ats_score"] = int(result["ats_score"])
            #  Selection Chance Score
            result["selection_chance"] = int(0.6 * result["relevance_score"] + 0.4 * result["ats_score"])
            return result
        except Exception as e:
            logger.error("Failed to parse combined LLM response: %s", e)
            # Fallback with safe defaults
            return {
                "relevance_score": 1,
                "relevance_explanation": "Could not parse explanation.",
                "ats_score": 1,
                "ats_explanation": "Could not parse explanation."
            }

    def _extract_json(self, text: str) -> str:
        # Extract JSON object from text (in case LLM adds extra text)
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return match.group(0)
        return text

    def _score_selection_chance(self, scores: Dict[str, int]) -> int:
        # Weighted average (can be tuned)
        return int(0.6 * scores["relevance_score"] + 0.4 * scores["ats_score"])

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate the number of tokens in a string for Gemini models.
        If tiktoken is not available for Gemini, use a simple heuristic: 1 token ≈ 4 characters (English text).
        """
        # Try to use tiktoken if available for Gemini, else fallback
        try:
            tokens = self.gemini_client.models.count_tokens(model=self.model_name, contents=text).total_tokens
            return tokens
        except Exception:
            # Fallback: 1 token ≈ 4 chars (OpenAI heuristic)
            return max(1, len(text) // 4)


if __name__ == "__main__":
    # Simple test for ATSMatcher
    gemini_api_key = os.getenv('GOOGLE_API_KEY')  # Make sure to set this in your .env file
    import json
    with open("./src/data/job_links_ea.json", 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    with open("./src/data/user_resume.txt", encoding='utf-8') as f:
        user_profile = str(f.read())
    # --- Rate limiter: 10 requests per 60 seconds ---
    rate_limiter = RateLimiter(max_calls=8, period=60.0)
    ats = ATSAgent(user_profile, gemini_api_key, rate_limiter=rate_limiter)
    jds = [f"Job Summary: {job['job_summary']} \n\n Job Details: {job['job_details']}" for _, job in json_data.items()]

    # Use a queue for jobs and results
    job_queue = queue.Queue()
    result_queue = queue.Queue()
    num_jobs = min(50, len(jds))
    for i in range(num_jobs):
        job_queue.put((f"job_{i}", jds[i]))

    def worker():
        while True:
            try:
                job_key, jd = job_queue.get(timeout=1)
            except queue.Empty:
                break
            try:
                result = ats.analyze_job(jd)
            except Exception as exc:
                result = {"error": str(exc)}
            result_queue.put((job_key, jd, result))
            job_queue.task_done()

    num_workers = 5  # Fewer workers since rate limiting is enforced
    threads = [threading.Thread(target=worker) for _ in range(num_workers)]
    for t in threads:
        t.start()

    with tqdm(total=num_jobs, desc="Analyzing jobs") as pbar:
        completed = 0
        results = {}
        while completed < num_jobs:
            job_key, jd, result = result_queue.get()
            results[job_key] = (jd, result)
            completed += 1
            pbar.update(1)
    for t in threads:
        t.join()

    print("Result:")
    for k, (jd, v) in results.items():
        print(f"{k}: {v}")

    # Store job descriptions and their results to a persistent CSV file with a unique file name for each batch run
    output_dir = pathlib.Path("./src/data/ats_results")
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"job_results_{timestamp}.csv"

    # Determine fieldnames: job_key, job_description, and all keys from result (flattened)
    def flatten_result(result):
        if isinstance(result, dict):
            return result
        else:
            return {"result": str(result)}

    # Collect all possible keys for CSV header
    all_keys = set()
    for i, (job_key, (jd, result)) in enumerate(results.items()):
        flat = flatten_result(result)
        all_keys.update(flat.keys())
    fieldnames = ["job_key", "job_description"] + sorted(all_keys)

    # Write to CSV (always write header since file is unique per run)
    with open(output_path, "w", encoding="utf-8", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i, (job_key, (jd, result)) in enumerate(results.items()):
            row = {
                "job_key": job_key,
                "job_description": jd
            }
            row.update(flatten_result(result))
            writer.writerow(row)
    print(f"Results saved to {output_path}")

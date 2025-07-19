import json
import os
from langchain_google_genai import GoogleGenerativeAI

from pydantic import BaseModel, ValidationError


def get_user_details(answer_format: type(BaseModel)) -> tuple[dict, bool]:
    # From LLM model
    status = False
    try_limit = 1
    with open('./data/system_prompt.txt', 'r') as f:
        user_resume = str(f.read())
    with open('./data/other_user_details.txt', 'r') as f:
        other_user_details = str(f.read())
    with open('./prompts/system_prompt.txt', 'r') as f:
        system_prompt = str(f.read())
    client = GoogleGenerativeAI(model='gemini-2.5-flash', google_api_key= os.getenv('GOOGLE_API_KEY'), temperature=0.4)
    prompt = system_prompt.format(user_resume=user_resume, other_details=other_user_details, format=answer_format.model_json_schema())
    response = "No call happened to AI Agent"

    while not status and try_limit>0:
        response: str = client.invoke(prompt)
        try:
            response_dict: dict = json.loads(response)
            answer_format(**response_dict)
            status = True
        except (ValidationError, Exception)as e:
            status = False
            prompt = system_prompt.format(format=answer_format.model_json_schema()) + \
            f"""
                Your previous response had following issues: 
                {e}

                Try to re generate with more precision
            """
            try_limit-=1
        
    return json.loads(response), status

def score_job(job_description: str, user_resume: str) -> tuple[int, bool]:
    """
    Uses an LLM to score the match between a user's resume and a job description on a scale of 1-10.
    10: User is almost certain to get shortlisted (perfect match).
    1: Almost no chance (no match).
    Returns (score, status) where status is True if a valid score was returned.
    """
    status = False
    try_limit = 1
    system_prompt = """
You are an expert job application assistant. Given a user's resume and a job description, score how well the user's profile matches the job description on a scale of 1 to 10.

10 means: user is almost certain to get shortlisted for the job, or is the top most applicant, or user profile matches perfectly with job description.
1 means: there is almost no chance for user to get short listed for this job, or user profile & job description do not match at all.

Respond ONLY with a single integer between 1 and 10. No extra text, no explanation, no code block.

Job Description:
{job_description}

User Resume:
{user_resume}
""".format(job_description=job_description, user_resume=user_resume)
    client = GoogleGenerativeAI(model='gemini-2.5-flash', google_api_key= os.getenv('GOOGLE_API_KEY'), temperature=0.2)
    prompt = system_prompt
    response = "No call happened to AI Agent"
    score = -1
    while not status and try_limit > 0:
        response: str = client.invoke(prompt)
        try:
            # Only accept a valid integer between 1 and 10
            score = int(response.strip())
            if 1 <= score <= 10:
                status = True
            else:
                raise ValueError(f"Score {score} out of range.")
        except Exception as e:
            status = False
            prompt = system_prompt + \
                f"\n\nYour previous response had following issues: {e}\nRespond ONLY with a single integer between 1 and 10. Try again."
            try_limit -= 1
            score = -1
    return score, status 
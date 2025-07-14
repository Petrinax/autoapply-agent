from dataclasses import dataclass
from typing import List, Optional

from selenium.webdriver.remote.webelement import WebElement


@dataclass
class JobApplication:
    job_url: str
    job_summary: str
    job_details: str
    failed_reason: str = ''
    # invalid_fields: List[WebElement] = None
    hiring_team: List[str] = None
    connections: List[str] = None
    applied: bool = False
    easy_apply: bool = False



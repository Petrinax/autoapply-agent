# SmartApply
The Ultimate Automated Job Application Engine.

**Fills up 100s of job applications in just 10 minutes. Perfectly tailors every application to your unique profile.**

---

## 🚀 What is this project?
This project is ann AI-powered automation tool designed to streamline the job application process. Leveraging the power of LangChain AI Agents, LLMs, and custom data pipelines, it can:

- **Auto-fill hundreds of job applications** across multiple platforms in minutes, not hours.
- **Intelligently parse and match your resume** to job descriptions, ensuring every application is highly relevant.
- **Perfectly tailor cover letters and responses** to each company and role, maximizing your chances of landing interviews.
- **Integrate with your existing data** (resumes, LinkedIn, custom profiles) for seamless, personalized applications.
- **Track, log, and analyze** your application history for continuous improvement.

---

## ✨ Features

- **Lightning Fast:** Apply to 100+ jobs in under 10 minutes.
- **Hyper-Personalized:** Every application is customized to your skills, experience, and the job description.
- **Smart Matching:** Uses advanced NLP to match your profile to the best-fit roles.
- **Plug-and-Play:** Connect your résumé, LinkedIn, or custom data sources.
- **Extensible:** Modular architecture—add new job boards, resume formats, or AI models with minimal effort.
- **Transparent:** Logs every application, so you always know where you’ve applied and what was sent.

---

## 🛠️ How does it work?

1. **Ingests your profile data** (resume, LinkedIn, custom YAML/JSON).
2. **Scrapes or imports job descriptions** from your target companies or boards.
3. **Uses LLMs** to generate tailored application materials.
4. **Auto-fills forms and submits applications** at scale, handling even complex workflows.
5. **Logs and tracks** every application for your review.

---

## 🎯 Why use this?

- **Save 100+ hours** of manual application work.
- **Never send a generic application again.**
- **Maximize your interview rate** with perfectly matched, AI-crafted applications.
- **Ideal for job seekers, recruiters, and career coaches** who want to automate and optimize the application process.

---

## 📦 Getting Started

1. Clone the repo:  
   `git clone https://github.com/yourusername/job-autoapply.git`
2. Install dependencies:  
   `pip install -r requirements.txt`
3. Add your profile data (resume, LinkedIn, etc.) to the `/data` folder.
4. Run the main script:  
   `python generate_yaml/src/main.py`
5. Watch as your applications are generated and submitted at lightning speed!

---

## 🤖 Tech Stack

- **Python 3.11+**
- **LangChain**
- **OpenAI/LLM APIs**
- **BeautifulSoup, Selenium** (for scraping and automation)
- **Modular, extensible architecture**

---

## 🏆 Impress recruiters. Land more interviews. Automate your job search.

---

> **Note:** This project is currently for educational use only and still requires a lot of improvements to be compliant with LinkedIn and other Job Board policies.

> Always review applications before submission to ensure accuracy and compliance with job board policies.

--- 

**Limitations:**
- Typeahead/combobox form inputs are not supported.
- Only "Easy Apply" job postings are supported.

## Issues:
- Linkedin blocking requests because of rate limits. 
- Pages not getting loaded fully before bot could read it. causing many jobs to get skipped.

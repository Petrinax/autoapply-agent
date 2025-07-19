# 🔄 Data Pipeline & ETL in SmartApply

## Overview
SmartApply features a robust, modular data pipeline that powers its automation and AI-driven personalization.

---

## 🏗️ Pipeline Stages

### 1. Data Ingestion
- **Sources:** Resume (TXT/JSON), LinkedIn export, custom YAML/JSON.
- **Parsing:** Uses Pydantic and custom parsers for structured extraction.

### 2. Job Scraping
- **Automation:** Selenium-based scrapers collect job descriptions from boards/platforms.
- **Batch Processing:** Handles large volumes efficiently.

### 3. Data Transformation
- **Profile Normalization:** Standardizes user data for AI agent consumption.
- **Job Description Cleaning:** Extracts relevant fields, removes noise.

### 4. AI Agent Integration
- **Input:** Cleaned profile and job data are fed to the LLM agent.
- **Output:** Generates tailored application materials and scores.

### 5. Application Logging & Analytics
- **Storage:** All applications, outcomes, and logs are stored as JSON for transparency and review.
- **Analytics:** Enables progress tracking and outcome analysis.

---

## 💡 Skills Demonstrated
- ETL pipeline design and implementation
- Data validation and transformation
- Scalable scraping and batch processing
- Structured logging and analytics

---

For architecture, see [ARCHITECTURE.md](ARCHITECTURE.md).
For AI agent details, see [AI_AGENT.md](AI_AGENT.md). 
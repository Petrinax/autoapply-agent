# 📊 Model Comparison Report: flash vs flash-lite for Job Picking & Applying

## 1. **Overview of the Models**

- **flash**: Refers to `gemini-2.5-flash` (full version).
- **flash-lite**: Refers to `gemini-2.5-flash-lite` (lighter, faster, and cheaper version).

Both models are used to:
- Score jobs for ATS (Applicant Tracking System) compatibility.
- Score relevance to the candidate's profile.
- Generate explanations for both scores.
- Compute a final `selection_chance` (weighted average of relevance and ATS scores).

---

## 2. **Empirical Results: Quantitative Comparison**

Comparision was performed by analyzing same set of Jobs against User profile using buth the models.

**Generated Results:**
- [Using Flash 2.5](./src/data/ats_results/flash-2.5-job_results_20250726_024338.csv)
- [Using Flash 2.5 Lite](./src/data/ats_results/flash-2.5-lite-job_results_20250726_025651.csv)


### **a. Score Distribution & Consistency**

- **flash** tends to be slightly more conservative in its scoring, especially for jobs with partial matches or where experience/tech stack is a mismatch.
- **flash-lite** is more optimistic, often giving higher scores for jobs where there is some overlap, even if not a perfect fit.

#### **Example:**
- For jobs requiring Java/Golang (where the candidate is Python-centric):
  - **flash**: Scores are often 2-4, with clear explanations of mismatch.
  - **flash-lite**: Sometimes gives 5-7, focusing on transferable skills.

- For strong Python/Data Engineering jobs:
  - Both models give high scores (8-10), but **flash** explanations are more nuanced and critical.

### **b. Selection Chance Calculation**

- Both models use the same formula:  
  `selection_chance = 0.6 * relevance_score + 0.4 * ats_score`
- **flash**'s more critical scoring leads to a sharper separation between "good" and "bad" jobs.
- **flash-lite**'s optimism may result in more jobs being picked as "good enough," potentially increasing false positives.

### **c. Explanations**

- **flash**: Explanations are more detailed, often highlighting subtle mismatches (e.g., missing AWS, specific frameworks, or years of experience).
- **flash-lite**: Explanations are shorter, sometimes missing nuanced gaps, but still generally accurate for clear matches/mismatches.

---

## 3. **Qualitative Comparison: Speed, Cost, and Use Case**

### **a. Speed & Cost**
- **flash-lite** is significantly faster and cheaper per API call.
- **flash** is slower and more expensive, but provides higher-fidelity analysis.

### **b. Accuracy & Filtering**
- **flash** is better at:
  - Filtering out jobs with hard mismatches (e.g., wrong language, insufficient experience).
  - Prioritizing jobs where the candidate is a *top* match.
  - Reducing wasted applications to jobs with low real-world chances.
- **flash-lite** is better for:
  - Rapid, large-scale screening where some false positives are acceptable.
  - Scenarios where API cost or rate limits are a concern.

---

## 4. **Job Picking Logic in Codebase**

- The codebase (see `ats_agent.py`) uses the model to generate:
  - `ats_score` (ATS keyword match)
  - `relevance_score` (profile/job fit)
  - `selection_chance` (final score for picking)
- The model name is set at agent initialization; **flash-lite** is currently the default in code.
- The job picking logic is **agnostic** to the model, but the model's scoring behavior directly impacts which jobs are picked.

---

## 5. **Summary Table: Model Performance**

| Criteria                | flash (full)         | flash-lite           |
|-------------------------|----------------------|----------------------|
| **Speed**               | Slower               | Faster               |
| **Cost**                | Higher               | Lower                |
| **Scoring Strictness**  | More critical        | More optimistic      |
| **Explanation Quality** | More nuanced         | Shorter, less nuanced|
| **False Positives**     | Fewer                | More                 |
| **Best For**            | Precision, quality   | Scale, speed         |
| **Job Picking**         | Fewer, higher quality| More, lower quality  |

---

## 6. **Recommendation**

### **If your goal is:**
- **Maximum interview chances, minimal wasted applications:**  
  **Use `flash` (full model)**.  
  It will filter out jobs where you are unlikely to succeed, saving time and effort.

- **Maximum coverage, rapid applications, cost savings:**  
  **Use `flash-lite`**.  
  Accept that you may apply to some jobs where you are not a strong fit, but you will cover more ground quickly and cheaply.

### **Hybrid Approach (Recommended for Most Users):**
- **First pass:** Use `flash-lite` to screen a large pool of jobs, filtering out obvious mismatches.
- **Second pass:** Use `flash` on the top N jobs (e.g., those with selection_chance ≥ 7 from flash-lite) for a more critical review before applying.

---

## 7. **Sample Observations from Your Data**

- Jobs with hard mismatches (e.g., Java-only roles) are more likely to be filtered out by **flash**.
- For Python/Data roles, both models agree, but **flash** provides more actionable feedback.
- For borderline jobs (e.g., experience slightly below requirement), **flash-lite** is more forgiving.

---

## 8. **Conclusion**

- **flash** is best for high-precision, high-quality job picking and applying.
- **flash-lite** is best for speed, scale, and cost efficiency, but may result in more wasted applications.
- For most users, a **two-stage approach** (flash-lite filter, flash confirm) is optimal.


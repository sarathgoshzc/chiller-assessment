
# Chiller Plant Assessment - Streamlit Application

This Streamlit application allows participants to complete a chiller plant operation and optimization assessment.

## Features

- Participant form:
  - Name
  - Position
  - Department
  - Phone No.
  - Email
- 10 multiple-choice assessment questions
- Automatic scoring
- Result shown immediately after submission
- Pass criteria: score >= 80%
- Shows `PASSED` or `RETAKE`
- Saves all submitted records to CSV
- Download results CSV from the sidebar

## How to Run

### 1. Install Python
Install Python 3.10 or newer.

### 2. Install Required Packages

Open Command Prompt / Terminal inside this folder and run:

```bash
pip install -r requirements.txt
```

### 3. Start the Application

```bash
streamlit run app.py
```

### 4. Open in Browser

Streamlit will open automatically. If not, open:

```text
http://localhost:8501
```

## Result Storage

Submitted assessment records are saved here:

```text
results/assessment_results.csv
```

You can download this file from the application sidebar.

## Pass Criteria

```text
Score >= 80% = PASSED
Score < 80% = RETAKE
```

# Chiller Plant Assessment - Streamlit App with Course Feedback and Auto Certificate

This version adds the requested workflow:

1. Participant fills in details and completes the 10-question exam.
2. After exam submission, the course feedback form appears.
3. Feedback ratings must be submitted before the final result is shown.
4. If the participant passes with score >= 80%, the course completion certificate is generated automatically.
5. Assessment records and feedback records are saved locally and to GitHub CSV when Streamlit Secrets are configured.

## Files to upload / replace in GitHub

```text
app.py
requirements.txt
assets/zealcorps_logo.png
results/assessment_results.csv
results/course_feedback.csv
```

## Streamlit Secrets

In Streamlit Community Cloud, open your app > Settings > Secrets and add:

```toml
[app]
admin_password = "admin123"

[github]
token = "YOUR_GITHUB_FINE_GRAINED_TOKEN"
owner = "sarathgoshzc"
repo = "chiller-assessment"
branch = "main"
results_path = "results/assessment_results.csv"
feedback_path = "results/course_feedback.csv"
```

## GitHub token permission

Create a GitHub fine-grained personal access token with:

```text
Repository: chiller-assessment
Contents: Read and Write
```

Do not put the token inside `app.py`.

## Admin download

In the app sidebar:

1. Enter admin password.
2. Download assessment CSV and feedback CSV.

Default password:

```text
admin123
```

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

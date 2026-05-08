# Chiller Plant Assessment - Streamlit App with GitHub CSV Save

This version saves each submitted assessment record to:

1. Local runtime backup: `results/assessment_results.csv`
2. GitHub repository CSV: `results/assessment_results.csv`

## Important

Streamlit Community Cloud local files are not reliable for permanent storage. This app commits each submission into your GitHub repository CSV using the GitHub API.

## Upload / replace these files in GitHub

```text
app.py
requirements.txt
results/assessment_results.csv
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
2. Click `Download GitHub Results CSV`.

Default password:

```text
admin123
```

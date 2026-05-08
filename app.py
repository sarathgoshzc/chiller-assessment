
import base64
import csv
import io
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
import streamlit as st


PASS_MARK = 80
RESULTS_DIR = Path("results")
RESULTS_FILE = RESULTS_DIR / "assessment_results.csv"

# CSV file path inside your GitHub repository.
GITHUB_RESULTS_PATH = "results/assessment_results.csv"


QUESTIONS = [
    {
        "question": "What are the four major components of a vapour compression chiller?",
        "options": [
            "Compressor, Evaporator, Condenser, Expansion Valve",
            "Pump, AHU, FCU, Cooling Tower",
            "Sensor, Valve, VFD, BMS",
            "Motor, Fan, Damper, Filter",
        ],
        "answer": "Compressor, Evaporator, Condenser, Expansion Valve",
    },
    {
        "question": "What is the main function of the evaporator in a chiller?",
        "options": [
            "Reject heat to the cooling tower",
            "Absorb heat from chilled water",
            "Compress refrigerant vapour",
            "Reduce condenser water pressure",
        ],
        "answer": "Absorb heat from chilled water",
    },
    {
        "question": "In a vapour compression refrigeration cycle, which component increases refrigerant pressure and temperature?",
        "options": [
            "Condenser",
            "Evaporator",
            "Compressor",
            "Expansion Valve",
        ],
        "answer": "Compressor",
    },
    {
        "question": "What is the purpose of the condenser in a chiller system?",
        "options": [
            "To absorb heat from chilled water",
            "To reject heat to condenser water",
            "To reduce refrigerant pressure",
            "To control AHU fan speed",
        ],
        "answer": "To reject heat to condenser water",
    },
    {
        "question": "Which equipment circulates chilled water to AHUs and FCUs?",
        "options": [
            "Condenser Water Pump",
            "Chilled Water Pump",
            "Cooling Tower Fan",
            "Compressor Motor",
        ],
        "answer": "Chilled Water Pump",
    },
    {
        "question": "In a typical chiller start sequence, which item should normally start first?",
        "options": [
            "Cooling tower fan",
            "Chiller compressor",
            "Chilled Water Pump",
            "AHU filter",
        ],
        "answer": "Chilled Water Pump",
    },
    {
        "question": "Which of the following is a major chiller protection interlock?",
        "options": [
            "Lighting failure",
            "High discharge pressure",
            "Door access alarm",
            "Room occupancy sensor fault",
        ],
        "answer": "High discharge pressure",
    },
    {
        "question": "What is the purpose of load-based chiller sequencing?",
        "options": [
            "To run all chillers continuously",
            "To maintain efficient chiller loading based on demand",
            "To stop all pumps during high load",
            "To increase unnecessary part-load operation",
        ],
        "answer": "To maintain efficient chiller loading based on demand",
    },
    {
        "question": "Why is variable speed pump optimization used in chiller plants?",
        "options": [
            "To increase pump speed at all times",
            "To reduce pump energy during low-load conditions",
            "To bypass all flow switches",
            "To disable differential pressure control",
        ],
        "answer": "To reduce pump energy during low-load conditions",
    },
    {
        "question": "What does kW/RT indicate in chiller plant performance monitoring?",
        "options": [
            "Cooling water temperature",
            "Energy consumption per ton of refrigeration",
            "Chilled water flow rate only",
            "Compressor discharge temperature",
        ],
        "answer": "Energy consumption per ton of refrigeration",
    },
]


CSV_FIELDNAMES = [
    "submitted_at",
    "name",
    "position",
    "department",
    "phone",
    "email",
    "score",
    "total",
    "percentage",
    "result",
] + [f"q{i + 1}_answer" for i in range(len(QUESTIONS))] + [
    f"q{i + 1}_status" for i in range(len(QUESTIONS))
]


def setup_page():
    st.set_page_config(
        page_title="Chiller Plant Assessment",
        page_icon="❄️",
        layout="wide",
    )

    st.markdown(
        """
        <style>
            .main {
                background-color: #ffffff;
            }
            .title-box {
                padding: 20px 25px;
                border-radius: 14px;
                background: linear-gradient(90deg, #003B73 0%, #0A548A 100%);
                color: white;
                margin-bottom: 18px;
            }
            .subtitle {
                color: #1f7a3a;
                font-size: 19px;
                font-weight: 600;
                margin-bottom: 20px;
            }
            .info-card {
                padding: 18px;
                border: 1px solid #d8e2ee;
                border-radius: 12px;
                background-color: #f8fbff;
                margin-bottom: 16px;
            }
            .pass-box {
                padding: 28px;
                border-radius: 14px;
                background-color: #ecfdf3;
                border: 2px solid #1f7a3a;
                text-align: center;
            }
            .fail-box {
                padding: 28px;
                border-radius: 14px;
                background-color: #fff4f2;
                border: 2px solid #b42318;
                text-align: center;
            }
            .metric-label {
                font-size: 16px;
                color: #003B73;
                font-weight: 700;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="title-box">
            <h1 style="margin:0;">❄️ Chiller Plant Operation & Optimization Assessment</h1>
            <p style="margin:8px 0 0 0;font-size:18px;">Technical Assessment | Conventional Optimization | HVAC Chiller Plant</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="subtitle">Pass Criteria: Score ≥ {PASS_MARK}%</div>',
        unsafe_allow_html=True,
    )


def valid_email(email: str) -> bool:
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return bool(re.match(pattern, email))


def get_github_config():
    """Read GitHub settings from Streamlit secrets."""
    github = st.secrets.get("github", {})
    return {
        "token": github.get("token", ""),
        "owner": github.get("owner", ""),
        "repo": github.get("repo", ""),
        "branch": github.get("branch", "main"),
        "results_path": github.get("results_path", GITHUB_RESULTS_PATH),
    }


def github_is_configured():
    config = get_github_config()
    return all([config["token"], config["owner"], config["repo"], config["branch"]])


def github_headers(token: str):
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def get_github_csv_content():
    """Get existing CSV content from GitHub. If file does not exist, create header."""
    config = get_github_config()
    url = (
        f"https://api.github.com/repos/{config['owner']}/{config['repo']}"
        f"/contents/{config['results_path']}"
    )

    response = requests.get(
        url,
        headers=github_headers(config["token"]),
        params={"ref": config["branch"]},
        timeout=20,
    )

    if response.status_code == 404:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        return output.getvalue(), None

    response.raise_for_status()
    payload = response.json()
    decoded = base64.b64decode(payload.get("content", "")).decode("utf-8")
    return decoded, payload.get("sha")


def append_row_to_csv_text(csv_text: str, row: dict):
    input_buffer = io.StringIO(csv_text)
    reader = csv.DictReader(input_buffer)
    existing_rows = list(reader)

    output_buffer = io.StringIO()
    writer = csv.DictWriter(output_buffer, fieldnames=CSV_FIELDNAMES)
    writer.writeheader()

    for existing_row in existing_rows:
        writer.writerow({field: existing_row.get(field, "") for field in CSV_FIELDNAMES})

    writer.writerow({field: row.get(field, "") for field in CSV_FIELDNAMES})
    return output_buffer.getvalue()


def save_result_to_github(row: dict):
    """
    Commit the updated assessment CSV to GitHub.
    Streamlit Secrets required:

    [github]
    token = "YOUR_GITHUB_FINE_GRAINED_TOKEN"
    owner = "sarathgoshzc"
    repo = "chiller-assessment"
    branch = "main"
    results_path = "results/assessment_results.csv"
    """
    if not github_is_configured():
        return False, "GitHub storage not configured in Streamlit Secrets."

    config = get_github_config()

    try:
        existing_csv, sha = get_github_csv_content()
        updated_csv = append_row_to_csv_text(existing_csv, row)
        encoded_updated_csv = base64.b64encode(updated_csv.encode("utf-8")).decode("utf-8")

        url = (
            f"https://api.github.com/repos/{config['owner']}/{config['repo']}"
            f"/contents/{config['results_path']}"
        )

        data = {
            "message": f"Add assessment result - {row['name']} - {row['submitted_at']}",
            "content": encoded_updated_csv,
            "branch": config["branch"],
        }

        if sha:
            data["sha"] = sha

        response = requests.put(
            url,
            headers=github_headers(config["token"]),
            json=data,
            timeout=20,
        )
        response.raise_for_status()
        return True, "Submission saved to GitHub CSV."

    except requests.HTTPError as e:
        error_text = e.response.text if e.response is not None else str(e)
        return False, f"GitHub save failed: {error_text}"

    except Exception as e:
        return False, f"GitHub save failed: {e}"


def create_result_row(profile: dict, score: int, total: int, percentage: float, result: str, answers: dict):
    row = {
        "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        **profile,
        "score": score,
        "total": total,
        "percentage": percentage,
        "result": result,
    }

    for i, q in enumerate(QUESTIONS):
        selected = answers.get(i, "")
        row[f"q{i + 1}_answer"] = selected
        row[f"q{i + 1}_status"] = "Correct" if selected == q["answer"] else "Wrong"

    return row


def save_result_locally(row: dict):
    RESULTS_DIR.mkdir(exist_ok=True)
    file_exists = RESULTS_FILE.exists()

    with RESULTS_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def save_result(profile: dict, score: int, total: int, percentage: float, result: str, answers: dict):
    row = create_result_row(profile, score, total, percentage, result, answers)

    # Local runtime backup.
    save_result_locally(row)

    # Permanent GitHub repository CSV save.
    github_saved, github_message = save_result_to_github(row)

    return github_saved, github_message


def calculate_score(answers: dict):
    score = 0
    review_rows = []

    for i, q in enumerate(QUESTIONS):
        selected = answers.get(i)
        correct = q["answer"]
        is_correct = selected == correct

        if is_correct:
            score += 1

        review_rows.append(
            {
                "No": i + 1,
                "Question": q["question"],
                "Your Answer": selected or "Not answered",
                "Correct Answer": correct,
                "Status": "Correct" if is_correct else "Wrong",
            }
        )

    total = len(QUESTIONS)
    percentage = round((score / total) * 100, 1)
    result = "PASSED" if percentage >= PASS_MARK else "RETAKE"

    return score, total, percentage, result, review_rows


def reset_assessment():
    keys_to_delete = [
        key for key in st.session_state.keys()
        if key.startswith("q_") or key in ["submitted", "result_data"]
    ]
    for key in keys_to_delete:
        del st.session_state[key]


def show_result(result_data: dict):
    result = result_data["result"]
    score = result_data["score"]
    total = result_data["total"]
    percentage = result_data["percentage"]

    if result == "PASSED":
        st.markdown(
            f"""
            <div class="pass-box">
                <h1 style="color:#1f7a3a;margin:0;">PASSED</h1>
                <h2 style="color:#003B73;">Score: {score} / {total} | {percentage}%</h2>
                <p>Congratulations. You have successfully passed the assessment.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="fail-box">
                <h1 style="color:#b42318;margin:0;">RETAKE</h1>
                <h2 style="color:#003B73;">Score: {score} / {total} | {percentage}%</h2>
                <p>Your score is below {PASS_MARK}%. Please retake the assessment.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if result_data.get("github_saved"):
        st.success("Submission saved to GitHub CSV successfully.")
    else:
        st.warning(result_data.get("github_message", "Submission was not saved to GitHub CSV."))

    st.write("")
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button("Retake Assessment", type="primary"):
            reset_assessment()
            st.rerun()
    with col2:
        if st.button("New Participant"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    st.subheader("Answer Review")
    review_df = pd.DataFrame(result_data["review"])
    st.dataframe(review_df, use_container_width=True, hide_index=True)


def read_local_results():
    if RESULTS_FILE.exists():
        return pd.read_csv(RESULTS_FILE)
    return pd.DataFrame(columns=CSV_FIELDNAMES)


def read_github_results():
    if not github_is_configured():
        return None, "GitHub storage not configured."

    try:
        csv_text, _sha = get_github_csv_content()
        return pd.read_csv(io.StringIO(csv_text)), "Loaded from GitHub CSV."
    except Exception as e:
        return None, f"Could not read GitHub CSV: {e}"


def show_results_download():
    st.sidebar.header("Admin / Records")
    st.sidebar.caption("Submitted records are saved to GitHub CSV when configured.")

    admin_password = st.sidebar.text_input("Admin Password", type="password")
    expected_password = st.secrets.get("app", {}).get("admin_password", "admin123")

    if admin_password != expected_password:
        st.sidebar.info("Enter admin password to download records.")
        return

    st.sidebar.success("Admin access granted.")

    github_df, github_message = read_github_results()

    if github_df is not None:
        st.sidebar.download_button(
            label="Download GitHub Results CSV",
            data=github_df.to_csv(index=False).encode("utf-8"),
            file_name="assessment_results_github.csv",
            mime="text/csv",
        )
        st.sidebar.success(github_message)
    else:
        st.sidebar.warning(github_message)

    local_df = read_local_results()
    st.sidebar.download_button(
        label="Download Local Backup CSV",
        data=local_df.to_csv(index=False).encode("utf-8"),
        file_name="assessment_results_local_backup.csv",
        mime="text/csv",
    )


def main():
    setup_page()
    show_results_download()

    if st.session_state.get("submitted") and st.session_state.get("result_data"):
        show_result(st.session_state["result_data"])
        return

    st.markdown(
        """
        <div class="info-card">
            Please fill in your details and complete all 10 assessment questions.
            The result will be displayed immediately after submission.
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("assessment_form", clear_on_submit=False):
        st.subheader("Participant Details")

        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name *")
            position = st.text_input("Position *")
            department = st.text_input("Department *")
        with col2:
            phone = st.text_input("Phone No. *")
            email = st.text_input("Email *")

        st.divider()
        st.subheader("Assessment Questions")

        answers = {}

        for i, q in enumerate(QUESTIONS):
            st.markdown(f"**{i + 1}. {q['question']}**")
            answers[i] = st.radio(
                label=f"Question {i + 1}",
                options=q["options"],
                index=None,
                key=f"q_{i}",
                label_visibility="collapsed",
            )
            st.write("")

        submitted = st.form_submit_button("Submit Assessment", type="primary")

    if submitted:
        profile = {
            "name": name.strip(),
            "position": position.strip(),
            "department": department.strip(),
            "phone": phone.strip(),
            "email": email.strip(),
        }

        missing_fields = [label for label, value in profile.items() if not value]
        unanswered = [i + 1 for i, value in answers.items() if value is None]

        if missing_fields:
            st.error("Please fill all participant details.")
            return

        if not valid_email(profile["email"]):
            st.error("Please enter a valid email address.")
            return

        if unanswered:
            st.error(f"Please answer all questions. Missing question(s): {unanswered}")
            return

        score, total, percentage, result, review_rows = calculate_score(answers)
        github_saved, github_message = save_result(profile, score, total, percentage, result, answers)

        st.session_state["submitted"] = True
        st.session_state["result_data"] = {
            "profile": profile,
            "score": score,
            "total": total,
            "percentage": percentage,
            "result": result,
            "review": review_rows,
            "github_saved": github_saved,
            "github_message": github_message,
        }
        st.rerun()


if __name__ == "__main__":
    main()

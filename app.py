
import csv
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st


PASS_MARK = 80
RESULTS_DIR = Path("results")
RESULTS_FILE = RESULTS_DIR / "assessment_results.csv"


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


def save_result(profile: dict, score: int, total: int, percentage: float, result: str, answers: dict):
    RESULTS_DIR.mkdir(exist_ok=True)

    fieldnames = [
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
    ] + [f"q{i + 1}" for i in range(len(QUESTIONS))]

    file_exists = RESULTS_FILE.exists()

    row = {
        "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        **profile,
        "score": score,
        "total": total,
        "percentage": percentage,
        "result": result,
    }

    for i in range(len(QUESTIONS)):
        row[f"q{i + 1}"] = answers.get(i, "")

    with RESULTS_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


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


def show_results_download():
    st.sidebar.header("Admin / Records")
    st.sidebar.caption("Submitted results are stored locally in CSV format.")

    if RESULTS_FILE.exists():
        df = pd.read_csv(RESULTS_FILE)
        st.sidebar.download_button(
            label="Download Results CSV",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="assessment_results.csv",
            mime="text/csv",
        )
    else:
        st.sidebar.info("No submissions yet.")


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
        save_result(profile, score, total, percentage, result, answers)

        st.session_state["submitted"] = True
        st.session_state["result_data"] = {
            "profile": profile,
            "score": score,
            "total": total,
            "percentage": percentage,
            "result": result,
            "review": review_rows,
        }
        st.rerun()


if __name__ == "__main__":
    main()

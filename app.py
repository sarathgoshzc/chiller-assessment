import base64
import csv
import io
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


PASS_MARK = 80
COURSE_TITLE = "Chiller Plant Optimization Training"
COURSE_SUBTITLE = "Conventional Control Strategies and Energy Efficient Operation"
COURSE_DATE_DISPLAY = "09-05-2026"
COURSE_DATE_CODE = datetime.strptime(COURSE_DATE_DISPLAY, "%d-%m-%Y").strftime("%Y%m%d")
COMPANY_NAME = "Zealcorps Pte Ltd"

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
ASSESSMENT_RESULTS_FILE = RESULTS_DIR / "assessment_results.csv"
FEEDBACK_RESULTS_FILE = RESULTS_DIR / "course_feedback.csv"

# CSV file paths inside your GitHub repository.
GITHUB_RESULTS_PATH = "results/assessment_results.csv"
GITHUB_FEEDBACK_PATH = "results/course_feedback.csv"

ASSETS_DIR = BASE_DIR / "assets"
LOGO_FILE = ASSETS_DIR / "zealcorps_logo.png"


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


ASSESSMENT_FIELDNAMES = [
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
    "feedback_submitted",
    "overall_rating",
    "certificate_no",
] + [f"q{i + 1}_answer" for i in range(len(QUESTIONS))] + [
    f"q{i + 1}_status" for i in range(len(QUESTIONS))
]


FEEDBACK_FIELDNAMES = [
    "submitted_at",
    "name",
    "position",
    "department",
    "phone",
    "email",
    "score",
    "percentage",
    "result",
    "overall_rating",
    "course_content_rating",
    "trainer_rating",
    "practical_usefulness_rating",
    "confidence_after_course_rating",
    "comments",
    "improvement_suggestions",
]


RATING_OPTIONS = {
    "5 - Excellent": 5,
    "4 - Very Good": 4,
    "3 - Good": 3,
    "2 - Fair": 2,
    "1 - Poor": 1,
}


# -----------------------------
# Page and UI
# -----------------------------

def setup_page():
    st.set_page_config(
        page_title="Chiller Plant Assessment",
        page_icon="❄️",
        layout="wide",
    )

    st.markdown(
        """
        <style>
            .main { background-color: #ffffff; }
            .title-box {
                padding: 22px 26px;
                border-radius: 16px;
                background: linear-gradient(90deg, #003B73 0%, #0A548A 100%);
                color: white;
                margin-bottom: 18px;
                box-shadow: 0 6px 18px rgba(0, 59, 115, 0.16);
            }
            .subtitle {
                color: #1f7a3a;
                font-size: 19px;
                font-weight: 700;
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
                padding: 30px;
                border-radius: 16px;
                background-color: #ecfdf3;
                border: 2px solid #1f7a3a;
                text-align: center;
            }
            .fail-box {
                padding: 30px;
                border-radius: 16px;
                background-color: #fff4f2;
                border: 2px solid #b42318;
                text-align: center;
            }
            .step-card {
                padding: 18px;
                border-radius: 14px;
                border: 1px solid #dce6ef;
                background-color: #fbfdff;
                margin-bottom: 16px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    logo_col, title_col = st.columns([1, 5])
    with logo_col:
        if LOGO_FILE.exists():
            st.image(str(LOGO_FILE), use_container_width=True)
    with title_col:
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
        f'<div class="subtitle">Pass Criteria: Score ≥ {PASS_MARK}% | Feedback must be submitted before result/certificate release</div>',
        unsafe_allow_html=True,
    )


def valid_email(email: str) -> bool:
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    return bool(re.match(pattern, email))


def rating_value(label: str) -> int:
    return RATING_OPTIONS.get(label, 0)


# -----------------------------
# GitHub storage helpers
# -----------------------------

def get_github_config():
    """Read GitHub settings from Streamlit secrets."""
    github = st.secrets.get("github", {})
    return {
        "token": github.get("token", ""),
        "owner": github.get("owner", ""),
        "repo": github.get("repo", ""),
        "branch": github.get("branch", "main"),
        "results_path": github.get("results_path", GITHUB_RESULTS_PATH),
        "feedback_path": github.get("feedback_path", GITHUB_FEEDBACK_PATH),
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


def get_github_csv_content(repo_path: str, fieldnames: list[str]):
    """Get an existing CSV from GitHub. If it does not exist, return a CSV header."""
    config = get_github_config()
    url = f"https://api.github.com/repos/{config['owner']}/{config['repo']}/contents/{repo_path}"

    response = requests.get(
        url,
        headers=github_headers(config["token"]),
        params={"ref": config["branch"]},
        timeout=20,
    )

    if response.status_code == 404:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        return output.getvalue(), None

    response.raise_for_status()
    payload = response.json()
    decoded = base64.b64decode(payload.get("content", "")).decode("utf-8")
    return decoded, payload.get("sha")


def append_row_to_csv_text(csv_text: str, row: dict, fieldnames: list[str]):
    input_buffer = io.StringIO(csv_text)
    reader = csv.DictReader(input_buffer)
    existing_rows = list(reader)

    output_buffer = io.StringIO()
    writer = csv.DictWriter(output_buffer, fieldnames=fieldnames)
    writer.writeheader()

    for existing_row in existing_rows:
        writer.writerow({field: existing_row.get(field, "") for field in fieldnames})

    writer.writerow({field: row.get(field, "") for field in fieldnames})
    return output_buffer.getvalue()


def save_row_to_github(row: dict, repo_path: str, fieldnames: list[str], commit_label: str):
    """Commit an updated CSV row to GitHub."""
    if not github_is_configured():
        return False, "GitHub storage not configured in Streamlit Secrets."

    config = get_github_config()

    try:
        existing_csv, sha = get_github_csv_content(repo_path, fieldnames)
        updated_csv = append_row_to_csv_text(existing_csv, row, fieldnames)
        encoded_updated_csv = base64.b64encode(updated_csv.encode("utf-8")).decode("utf-8")

        url = f"https://api.github.com/repos/{config['owner']}/{config['repo']}/contents/{repo_path}"

        data = {
            "message": f"Add {commit_label} - {row.get('name', 'participant')} - {row.get('submitted_at', '')}",
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
        return True, f"{commit_label.title()} saved to GitHub CSV."

    except requests.HTTPError as e:
        error_text = e.response.text if e.response is not None else str(e)
        return False, f"GitHub save failed: {error_text}"
    except Exception as e:
        return False, f"GitHub save failed: {e}"


# -----------------------------
# CSV local save/read helpers
# -----------------------------

def save_row_locally(row: dict, file_path: Path, fieldnames: list[str]):
    RESULTS_DIR.mkdir(exist_ok=True)
    file_exists = file_path.exists()

    with file_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow({field: row.get(field, "") for field in fieldnames})


def read_local_csv(file_path: Path, fieldnames: list[str]):
    if file_path.exists():
        return pd.read_csv(file_path)
    return pd.DataFrame(columns=fieldnames)


def read_github_csv(repo_path: str, fieldnames: list[str]):
    if not github_is_configured():
        return None, "GitHub storage not configured."

    try:
        csv_text, _sha = get_github_csv_content(repo_path, fieldnames)
        return pd.read_csv(io.StringIO(csv_text)), "Loaded from GitHub CSV."
    except Exception as e:
        return None, f"Could not read GitHub CSV: {e}"


# -----------------------------
# Assessment, feedback, certificate
# -----------------------------

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


def sanitize_certificate_name(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "", name).upper()
    return cleaned[:12] or "PARTICIPANT"


def make_certificate_no(name: str, submitted_at: str) -> str:
    serial = datetime.now().strftime("%H%M%S")
    name_code = sanitize_certificate_name(name)
    return f"ZC-CC-{COURSE_DATE_CODE}-{name_code}-{serial}"


def create_assessment_row(result_data: dict, feedback_data: dict, certificate_no: str):
    profile = result_data["profile"]
    answers = result_data["answers"]
    row = {
        "submitted_at": result_data["submitted_at"],
        **profile,
        "score": result_data["score"],
        "total": result_data["total"],
        "percentage": result_data["percentage"],
        "result": result_data["result"],
        "feedback_submitted": "Yes",
        "overall_rating": feedback_data.get("overall_rating", ""),
        "certificate_no": certificate_no,
    }

    for i, q in enumerate(QUESTIONS):
        selected = answers.get(i, "")
        row[f"q{i + 1}_answer"] = selected
        row[f"q{i + 1}_status"] = "Correct" if selected == q["answer"] else "Wrong"

    return row


def create_feedback_row(result_data: dict, feedback_data: dict):
    profile = result_data["profile"]
    return {
        "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        **profile,
        "score": result_data["score"],
        "percentage": result_data["percentage"],
        "result": result_data["result"],
        **feedback_data,
    }


def save_final_submission(result_data: dict, feedback_data: dict, certificate_no: str):
    config = get_github_config()
    assessment_row = create_assessment_row(result_data, feedback_data, certificate_no)
    feedback_row = create_feedback_row(result_data, feedback_data)

    save_row_locally(assessment_row, ASSESSMENT_RESULTS_FILE, ASSESSMENT_FIELDNAMES)
    save_row_locally(feedback_row, FEEDBACK_RESULTS_FILE, FEEDBACK_FIELDNAMES)

    assessment_saved, assessment_message = save_row_to_github(
        assessment_row,
        config["results_path"],
        ASSESSMENT_FIELDNAMES,
        "assessment result",
    )
    feedback_saved, feedback_message = save_row_to_github(
        feedback_row,
        config["feedback_path"],
        FEEDBACK_FIELDNAMES,
        "course feedback",
    )

    return {
        "assessment_saved": assessment_saved,
        "assessment_message": assessment_message,
        "feedback_saved": feedback_saved,
        "feedback_message": feedback_message,
    }


def draw_centered(c: canvas.Canvas, text: str, x: float, y: float, font: str, size: float, color=colors.black):
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawCentredString(x, y, text)


def draw_fit_centered(c: canvas.Canvas, text: str, x: float, y: float, max_width: float, font: str, size: float, min_size: float, color=colors.black):
    text = str(text)
    current_size = size
    while current_size > min_size and stringWidth(text, font, current_size) > max_width:
        current_size -= 1
    draw_centered(c, text, x, y, font, current_size, color)


def draw_info_box(c: canvas.Canvas, x: float, y: float, w: float, h: float, label: str, value: str):
    border = colors.HexColor("#d8e4ec")
    dark = colors.HexColor("#25323a")
    muted = colors.HexColor("#6b7d89")
    c.setStrokeColor(border)
    c.setFillColor(colors.white)
    c.setLineWidth(1.2)
    c.roundRect(x, y, w, h, 9, stroke=1, fill=1)
    draw_centered(c, label.upper(), x + w / 2, y + h - 22, "Helvetica-Bold", 7.5, muted)
    draw_fit_centered(c, value, x + w / 2, y + 17, w - 18, "Helvetica-Bold", 11, 7, dark)


def draw_logo(c: canvas.Canvas, page_width: float, top_y: float):
    if LOGO_FILE.exists():
        img = ImageReader(str(LOGO_FILE))
        iw, ih = img.getSize()
        logo_w = 215
        logo_h = logo_w * ih / iw
        c.drawImage(
            img,
            (page_width - logo_w) / 2,
            top_y - logo_h,
            width=logo_w,
            height=logo_h,
            mask="auto",
            preserveAspectRatio=True,
        )
    else:
        draw_centered(c, "ZEALCORPS", page_width / 2, top_y - 25, "Helvetica-Bold", 28, colors.HexColor("#252525"))


def generate_certificate_pdf(profile: dict, percentage: float, certificate_no: str) -> bytes:
    """Generate a certificate PDF matching the provided Zealcorps certificate format."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    page_width, page_height = landscape(A4)

    navy = colors.HexColor("#1f3340")
    light_blue = colors.HexColor("#eaf7fc")
    blue = colors.HexColor("#14a7df")
    green = colors.HexColor("#7ad000")
    dark = colors.HexColor("#252525")
    gray = colors.HexColor("#666666")
    light_border = colors.HexColor("#ccdce4")

    # Background accents
    c.setFillColor(light_blue)
    c.circle(50, page_height - 48, 120, stroke=0, fill=1)
    c.setFillColor(colors.HexColor("#f0fae8"))
    c.circle(page_width - 50, 25, 118, stroke=0, fill=1)

    # Border
    c.setStrokeColor(navy)
    c.setLineWidth(2.2)
    c.roundRect(30, 22, page_width - 60, page_height - 44, 16, stroke=1, fill=0)
    c.setStrokeColor(light_border)
    c.setLineWidth(0.8)
    c.roundRect(43, 35, page_width - 86, page_height - 70, 13, stroke=1, fill=0)

    # Corner marks
    c.setStrokeColor(blue)
    c.setLineWidth(4)
    c.line(62, page_height - 40, 200, page_height - 40)
    c.line(47, page_height - 58, 47, page_height - 148)
    c.setStrokeColor(green)
    c.line(page_width - 63, 40, page_width - 192, 40)
    c.line(page_width - 48, 58, page_width - 48, 150)

    # Faint logo watermark
    c.saveState()
    try:
        c.setFillAlpha(0.07)
        c.setStrokeAlpha(0.07)
    except Exception:
        pass
    c.setFillColor(blue)
    c.setFont("Helvetica-Bold", 160)
    c.drawCentredString(page_width - 145, page_height / 2 - 25, "Z")
    c.restoreState()

    # Top logo
    draw_logo(c, page_width, page_height - 52)

    # Title
    draw_centered(c, "CERTIFICATE", page_width / 2, page_height - 155, "Helvetica-Bold", 34, dark)
    draw_centered(c, "O F   C O M P L E T I O N", page_width / 2, page_height - 188, "Helvetica-Bold", 17, gray)

    # Divider
    c.setStrokeColor(light_border)
    c.setLineWidth(0.8)
    c.line(page_width / 2 - 180, page_height - 208, page_width / 2 - 60, page_height - 208)
    c.line(page_width / 2 + 60, page_height - 208, page_width / 2 + 180, page_height - 208)
    c.setFillColor(blue)
    c.circle(page_width / 2 - 10, page_height - 208, 4, stroke=0, fill=1)
    c.setFillColor(green)
    c.circle(page_width / 2 + 10, page_height - 208, 4, stroke=0, fill=1)

    # Body
    draw_centered(c, "This certificate is proudly presented to", page_width / 2, page_height - 242, "Helvetica", 13.5, gray)
    draw_fit_centered(c, profile.get("name", "Participant"), page_width / 2, page_height - 292, 360, "Times-Bold", 37, 20, dark)
    c.setStrokeColor(light_border)
    c.setLineWidth(0.8)
    c.line(page_width / 2 - 120, page_height - 305, page_width / 2 + 120, page_height - 305)

    draw_centered(c, "has successfully completed the course titled", page_width / 2, page_height - 342, "Helvetica", 13.5, gray)

    # Course box
    box_x = 140
    box_y = page_height - 428
    box_w = page_width - 280
    box_h = 72
    c.setStrokeColor(light_border)
    c.setFillColor(colors.HexColor("#fbfdff"))
    c.setLineWidth(0.9)
    c.roundRect(box_x, box_y, box_w, box_h, 12, stroke=1, fill=1)
    draw_fit_centered(c, COURSE_TITLE, page_width / 2, box_y + 43, box_w - 40, "Helvetica-Bold", 18, 11, dark)
    draw_fit_centered(c, COURSE_SUBTITLE, page_width / 2, box_y + 22, box_w - 50, "Helvetica", 10.5, 8, gray)

    # Info boxes
    info_y = 72
    info_w = 174
    info_h = 54
    gap = 16
    start_x = 48
    draw_info_box(c, start_x, info_y, info_w, info_h, "Course Date", COURSE_DATE_DISPLAY)
    draw_info_box(c, start_x + info_w + gap, info_y, info_w, info_h, "Assessment Score", f"{percentage:g}%")
    draw_info_box(c, start_x + 2 * (info_w + gap), info_y, 210, info_h, "Certificate No.", certificate_no)

    # Signatures / issuer
    c.setStrokeColor(colors.HexColor("#9fb2bf"))
    c.setLineWidth(0.9)
    c.line(92, 68, 260, 68)
    c.line(page_width - 260, 68, page_width - 92, 68)
    draw_centered(c, "Authorized Signature", 176, 52, "Helvetica-Bold", 9.5, dark)
    draw_centered(c, "Training Coordinator", 176, 37, "Helvetica", 8, gray)
    draw_centered(c, COMPANY_NAME, page_width - 176, 52, "Helvetica-Bold", 9.5, dark)
    draw_centered(c, "Engineering Training & Assessment", page_width - 176, 37, "Helvetica", 8, gray)
    draw_centered(c, "This certificate is issued based on the submitted assessment record and course feedback completion.", page_width / 2, 30, "Helvetica", 7.5, colors.HexColor("#8a9aa5"))

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()


# -----------------------------
# Screen rendering
# -----------------------------

def reset_all():
    for key in list(st.session_state.keys()):
        del st.session_state[key]


def reset_assessment_only():
    keys_to_delete = [
        key for key in st.session_state.keys()
        if key.startswith("q_") or key.startswith("feedback_") or key in [
            "assessment_done",
            "pending_result",
            "final_submitted",
            "final_result",
        ]
    ]
    for key in keys_to_delete:
        del st.session_state[key]


def show_assessment_form():
    st.markdown(
        """
        <div class="info-card">
            Please fill in your details and complete all 10 assessment questions.
            After submitting the exam, a course feedback form will appear. The result and certificate will be released only after feedback submission.
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

        submitted = st.form_submit_button("Submit Exam", type="primary")

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
        st.session_state["assessment_done"] = True
        st.session_state["pending_result"] = {
            "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "profile": profile,
            "answers": answers,
            "score": score,
            "total": total,
            "percentage": percentage,
            "result": result,
            "review": review_rows,
        }
        st.rerun()


def show_feedback_form():
    result_data = st.session_state.get("pending_result")
    if not result_data:
        reset_assessment_only()
        st.rerun()

    st.markdown(
        """
        <div class="step-card">
            <h3 style="margin-top:0;">Course Feedback</h3>
            Your exam answers have been submitted. Please complete the feedback below to receive your final result.
        </div>
        """,
        unsafe_allow_html=True,
    )

    rating_labels = list(RATING_OPTIONS.keys())

    with st.form("course_feedback_form", clear_on_submit=False):
        st.subheader("Rating")
        col1, col2 = st.columns(2)
        with col1:
            overall_rating = st.radio("Overall course rating *", rating_labels, index=None, key="feedback_overall")
            course_content_rating = st.radio("Course content quality *", rating_labels, index=None, key="feedback_content")
        with col2:
            trainer_rating = st.radio("Trainer / delivery rating *", rating_labels, index=None, key="feedback_trainer")
            practical_rating = st.radio("Practical usefulness *", rating_labels, index=None, key="feedback_practical")

        confidence_rating = st.radio(
            "Confidence to apply the learning at work *",
            rating_labels,
            index=None,
            key="feedback_confidence",
        )

        comments = st.text_area("What did you like most about the course?", height=90)
        improvement_suggestions = st.text_area("Suggestions for improvement", height=90)

        feedback_submitted = st.form_submit_button("Submit Feedback and View Result", type="primary")

    if feedback_submitted:
        required_ratings = [overall_rating, course_content_rating, trainer_rating, practical_rating, confidence_rating]
        if any(value is None for value in required_ratings):
            st.error("Please complete all rating fields before submitting feedback.")
            return

        feedback_data = {
            "overall_rating": rating_value(overall_rating),
            "course_content_rating": rating_value(course_content_rating),
            "trainer_rating": rating_value(trainer_rating),
            "practical_usefulness_rating": rating_value(practical_rating),
            "confidence_after_course_rating": rating_value(confidence_rating),
            "comments": comments.strip(),
            "improvement_suggestions": improvement_suggestions.strip(),
        }

        certificate_no = ""
        certificate_pdf = b""
        if result_data["result"] == "PASSED":
            certificate_no = make_certificate_no(result_data["profile"]["name"], result_data["submitted_at"])
            certificate_pdf = generate_certificate_pdf(result_data["profile"], result_data["percentage"], certificate_no)

        save_status = save_final_submission(result_data, feedback_data, certificate_no)

        st.session_state["final_submitted"] = True
        st.session_state["final_result"] = {
            **result_data,
            "feedback": feedback_data,
            "certificate_no": certificate_no,
            "certificate_pdf": certificate_pdf,
            **save_status,
        }
        st.rerun()


def show_final_result():
    result_data = st.session_state.get("final_result")
    if not result_data:
        reset_assessment_only()
        st.rerun()

    result = result_data["result"]
    score = result_data["score"]
    total = result_data["total"]
    percentage = result_data["percentage"]
    profile = result_data["profile"]

    if result == "PASSED":
        st.markdown(
            f"""
            <div class="pass-box">
                <h1 style="color:#1f7a3a;margin:0;">PASSED</h1>
                <h2 style="color:#003B73;">Score: {score} / {total} | {percentage}%</h2>
                <p>Feedback submitted successfully. Your certificate has been generated automatically.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        file_name = f"Certificate_{sanitize_certificate_name(profile['name'])}_{COURSE_DATE_CODE}.pdf"
        st.download_button(
            label="Download Course Completion Certificate",
            data=result_data["certificate_pdf"],
            file_name=file_name,
            mime="application/pdf",
            type="primary",
        )
        st.caption(f"Certificate No.: {result_data.get('certificate_no', '')}")
    else:
        st.markdown(
            f"""
            <div class="fail-box">
                <h1 style="color:#b42318;margin:0;">RETAKE</h1>
                <h2 style="color:#003B73;">Score: {score} / {total} | {percentage}%</h2>
                <p>Feedback submitted successfully. Your score is below {PASS_MARK}%, so certificate generation is not enabled.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button("Retake Assessment", type="primary"):
            reset_assessment_only()
            st.rerun()
    with col2:
        if st.button("New Participant"):
            reset_all()
            st.rerun()

    st.divider()
    if result_data.get("assessment_saved") and result_data.get("feedback_saved"):
        st.success("Assessment result and course feedback saved to GitHub CSV successfully.")
    else:
        st.warning(result_data.get("assessment_message", "Assessment result was not saved to GitHub."))
        st.warning(result_data.get("feedback_message", "Course feedback was not saved to GitHub."))

    st.subheader("Answer Review")
    review_df = pd.DataFrame(result_data["review"])
    st.dataframe(review_df, use_container_width=True, hide_index=True)

    st.subheader("Submitted Course Feedback")
    feedback_df = pd.DataFrame([result_data["feedback"]])
    st.dataframe(feedback_df, use_container_width=True, hide_index=True)


def show_results_download():
    st.sidebar.header("Admin / Records")
    st.sidebar.caption("Submitted assessment records and course feedback are saved to GitHub CSV when configured.")

    admin_password = st.sidebar.text_input("Admin Password", type="password")
    expected_password = st.secrets.get("app", {}).get("admin_password", "admin123")

    if admin_password != expected_password:
        st.sidebar.info("Enter admin password to download records.")
        return

    st.sidebar.success("Admin access granted.")
    config = get_github_config()

    github_assessment_df, github_assessment_message = read_github_csv(config["results_path"], ASSESSMENT_FIELDNAMES)
    if github_assessment_df is not None:
        st.sidebar.download_button(
            label="Download GitHub Assessment CSV",
            data=github_assessment_df.to_csv(index=False).encode("utf-8"),
            file_name="assessment_results_github.csv",
            mime="text/csv",
        )
        st.sidebar.success(github_assessment_message)
    else:
        st.sidebar.warning(github_assessment_message)

    github_feedback_df, github_feedback_message = read_github_csv(config["feedback_path"], FEEDBACK_FIELDNAMES)
    if github_feedback_df is not None:
        st.sidebar.download_button(
            label="Download GitHub Feedback CSV",
            data=github_feedback_df.to_csv(index=False).encode("utf-8"),
            file_name="course_feedback_github.csv",
            mime="text/csv",
        )
        st.sidebar.success(github_feedback_message)
    else:
        st.sidebar.warning(github_feedback_message)

    local_assessment_df = read_local_csv(ASSESSMENT_RESULTS_FILE, ASSESSMENT_FIELDNAMES)
    st.sidebar.download_button(
        label="Download Local Assessment Backup CSV",
        data=local_assessment_df.to_csv(index=False).encode("utf-8"),
        file_name="assessment_results_local_backup.csv",
        mime="text/csv",
    )

    local_feedback_df = read_local_csv(FEEDBACK_RESULTS_FILE, FEEDBACK_FIELDNAMES)
    st.sidebar.download_button(
        label="Download Local Feedback Backup CSV",
        data=local_feedback_df.to_csv(index=False).encode("utf-8"),
        file_name="course_feedback_local_backup.csv",
        mime="text/csv",
    )


def main():
    setup_page()
    show_results_download()

    if st.session_state.get("final_submitted") and st.session_state.get("final_result"):
        show_final_result()
        return

    if st.session_state.get("assessment_done") and st.session_state.get("pending_result"):
        show_feedback_form()
        return

    show_assessment_form()


if __name__ == "__main__":
    main()

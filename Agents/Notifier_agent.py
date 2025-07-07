import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from fpdf import FPDF
from Utilities.notifier import send_email_with_attachment

# Load environment variables
load_dotenv()
STUDENT_EMAIL = os.getenv("STUDENT_EMAIL")
PARENT_EMAIL = os.getenv("PARENT_EMAIL")

# Paths
PLAN_PATH = "Data/Output/study_plan.xlsx"
PROGRESS_CSV = "Data/Output/Progress_Report.csv"
PROGRESS_CHART = "Data/Output/Progress_Chart_Line.png"
REPORT_PDF = "Data/Output/Parent_Report.pdf"


# --- Helpers ---
def safe_text(text):
    return text.encode("latin-1", "replace").decode("latin-1")


def get_study_plan_df():
    if not os.path.exists(PLAN_PATH):
        print("study_plan.xlsx not found.")
        return pd.DataFrame()

    df = pd.read_excel(PLAN_PATH)
    df.columns = [str(c).strip() for c in df.columns]

    if "Week" not in df.columns or "Key Topics/Concepts" not in df.columns:
        print("Required columns missing from study plan.")
        return pd.DataFrame()

    df = df.dropna(subset=["Week"])
    try:
        df["Week"] = df["Week"].astype(int)
    except:
        print("Could not convert 'Week' column to integers. Defaulting to 1.")
        df["Week"] = 1

    return df


def get_plan_start_date():
    file_time = os.path.getctime(PLAN_PATH)
    return datetime.fromtimestamp(file_time)


def get_current_week_number(df: pd.DataFrame):
    all_weeks = sorted(df["Week"].unique())
    if not all_weeks:
        return 1

    plan_start = get_plan_start_date()
    weeks_passed = (datetime.now() - plan_start).days // 7
    return all_weeks[min(weeks_passed, len(all_weeks) - 1)]


def get_week_topics(df, week_number):
    rows = df[df["Week"] == week_number]
    topics = []

    for _, row in rows.iterrows():
        topic = f"{row['Chapter']}: {row['Key Topics/Concepts']}"
        if "Description" in row and not pd.isna(row["Description"]):
            topic += f" — {row['Description']}"
        topics.append(topic.strip())

    return topics


def summarize_progress():
    if not os.path.exists(PROGRESS_CSV):
        return "No quizzes graded yet.", {}

    df = pd.read_csv(PROGRESS_CSV)
    valid = df.dropna().iloc[:-2]

    if valid.empty:
        return "No quiz performance data yet.", {}

    latest = valid.iloc[-1]
    summary = {
        "Max Score": valid["Score"].max(),
        "Min Score": valid["Score"].min(),
        "Average Score": round(valid["Score"].mean(), 2),
        "Average %": round(valid["Percentage"].mean(), 2)
    }

    latest_summary = f"{latest['Filename']} - {latest['Score']} / {latest['Out Of']} ({latest['Percentage']}%)"
    return latest_summary, summary


def generate_parent_pdf(topics, week_number, quiz_summary, stats):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(0, 10, txt="Weekly Progress Report", ln=True)
    pdf.ln(8)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, txt=f"Completed Topics (Week {week_number}):", ln=True)
    pdf.set_font("Arial", "", 12)
    for t in topics:
        pdf.multi_cell(0, 8, safe_text(f"- {t}"))

    pdf.ln(6)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, txt="Recent Quiz Performance:", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8, safe_text(quiz_summary))

    pdf.ln(6)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, txt="Progress Stats:", ln=True)
    pdf.set_font("Arial", "", 12)
    for k, v in stats.items():
        pdf.cell(0, 8, txt=f"{k}: {v}", ln=True)

    if os.path.exists(PROGRESS_CHART):
        pdf.add_page()
        pdf.cell(0, 10, txt="Progress Chart", ln=True)
        pdf.image(PROGRESS_CHART, w=180)

    pdf.output(REPORT_PDF)
    print(f"Parent report saved to: {REPORT_PDF}")


# --- Main Agent ---
def run_parent_notifier():
    global STUDENT_EMAIL, PARENT_EMAIL

    if not STUDENT_EMAIL:
        STUDENT_EMAIL = input("Enter student email: ").strip()
    if not PARENT_EMAIL:
        PARENT_EMAIL = input("Enter parent email: ").strip()

    df = get_study_plan_df()
    if df.empty:
        return

    current_week = get_current_week_number(df)
    week_topics = get_week_topics(df, current_week)

    # 1. Send to Student
    if week_topics:
        body = f"Your study plan for Week {current_week}:\n\n" + "\n".join(f"- {t}" for t in week_topics)
    else:
        body = f"No topics found for Week {current_week}."

    send_email_with_attachment(
        subject=f"Weekly Study Reminder – Week {current_week}",
        body=body,
        to_email=STUDENT_EMAIL
    )

    # 2. Send to Parent
    quiz_summary, stats = summarize_progress()
    generate_parent_pdf(week_topics, current_week, quiz_summary, stats)

    send_email_with_attachment(
    subject="Weekly Student Report + Study Plan",
    body="Dear Parent,\n\nAttached are this week's progress report and the full study plan.\n\nRegards,\nE-Learning Assistant",
    to_email=PARENT_EMAIL,
    attachment_path=[REPORT_PDF, PLAN_PATH]
    )


if __name__ == "__main__":
    run_parent_notifier()

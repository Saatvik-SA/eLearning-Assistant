# --- Agents/Progress_tracker.py ---

import os
import fitz
import re
import pandas as pd
import matplotlib.pyplot as plt

def extract_score_components(text):
    """
    Extracts earned and total score from lines like:
    '**3. Total Score:**' followed by '18.5 / 20'
    Returns (earned: float, total: float) or (None, None) if not found
    """
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if "total score" in line.lower():
            # Check same line
            match = re.search(r"(\d+(\.\d+)?)\s*/\s*(\d+(\.\d+)?)", line)
            # Check next line if needed
            if not match and i + 1 < len(lines):
                match = re.search(r"(\d+(\.\d+)?)\s*/\s*(\d+(\.\d+)?)", lines[i + 1])
            if match:
                earned = float(match.group(1))
                total = float(match.group(3))
                return earned, total
    return None, None


def track_progress(folder="Data/Output"):
    """
    Generates progress.csv and progress line chart showing scores over time.
    Includes all graded papers (even with missing scores), and appends analytics summary.
    """
    graded_files = sorted(
        [f for f in os.listdir(folder) if "_graded" in f.lower() and f.lower().endswith(".pdf")]
    )
    if not graded_files:
        return

    records = []

    for file in graded_files:
        path = os.path.join(folder, file)
        with fitz.open(path) as doc:
            full_text = "\n".join([page.get_text() for page in doc])
        earned, total = extract_score_components(full_text)
        if earned is not None and total is not None:
            percent = round((earned / total) * 100, 2)
        else:
            earned = total = percent = None

        records.append({
            "Filename": file,
            "Score": earned,
            "Out Of": total,
            "Percentage": percent
        })

    df = pd.DataFrame(records)

    # === Analytics ===
    analytics = []
    valid_df = df.dropna()
    if not valid_df.empty:
        analytics.append({"Filename": "Max Score", "Score": valid_df["Score"].max(),
                          "Out Of": valid_df.loc[valid_df["Score"].idxmax(), "Out Of"],
                          "Percentage": valid_df["Percentage"].max()})
        analytics.append({"Filename": "Min Score", "Score": valid_df["Score"].min(),
                          "Out Of": valid_df.loc[valid_df["Score"].idxmin(), "Out Of"],
                          "Percentage": valid_df["Percentage"].min()})
        analytics.append({"Filename": "Average Score", "Score": round(valid_df["Score"].mean(), 2),
                          "Out Of": "", "Percentage": round(valid_df["Percentage"].mean(), 2)})

    summary_df = pd.DataFrame(analytics)

    # === Save CSV ===
    csv_path = os.path.join(folder, "Progress_Report.csv")
    final_df = pd.concat([df, pd.DataFrame([{}]), summary_df], ignore_index=True)
    final_df.to_csv(csv_path, index=False)

    # === Line Chart ===
    plt.figure(figsize=(10, 5))
    plt.plot(df["Filename"], df["Score"], marker='o', linestyle='-', color='green')

    for i, row in df.iterrows():
        if pd.notnull(row["Score"]) and pd.notnull(row["Out Of"]):
            label = f"{row['Score']} / {row['Out Of']}"
            plt.text(i, row["Score"] + 0.3, label, ha='center', fontsize=8)

    plt.xticks(rotation=45, ha="right")
    plt.title("Student Progress Over Graded Papers")
    plt.xlabel("Graded File")
    plt.ylabel("Score")
    plt.grid(True)
    plt.tight_layout()

    chart_path = os.path.join(folder, "Progress_Chart_Line.png")
    plt.savefig(chart_path)
    plt.close()

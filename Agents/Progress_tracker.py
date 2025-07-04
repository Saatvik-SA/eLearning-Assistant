# --- File: Agents/Progress_tracker.py ---

import os
import fitz
import pandas as pd
import matplotlib.pyplot as plt

def extract_score_from_text(text):
    for line in text.split("\n"):
        if "Total Score" in line:
            try:
                score = int(''.join(filter(str.isdigit, line)))
                return score
            except:
                return None
    return None

def track_progress():
    folder = "Data/Output"
    graded_files = [f for f in os.listdir(folder) if "_graded" in f.lower() and f.lower().endswith(".pdf")]

    if not graded_files:
        print("No graded reports found in Data/Output.")
        return

    records = []

    for file in graded_files:
        path = os.path.join(folder, file)
        with fitz.open(path) as doc:
            full_text = "\n".join([page.get_text() for page in doc])

        score = extract_score_from_text(full_text)
        if score is not None:
            records.append({"Filename": file, "Score": score})

    if not records:
        print("No scores could be extracted from graded files.")
        return

    df = pd.DataFrame(records)
    csv_path = os.path.join(folder, "Progress_Report.csv")
    df.to_csv(csv_path, index=False)

    print(f"Progress saved to {csv_path}")

    # Plot
    plt.figure(figsize=(8, 4))
    plt.plot(df["Filename"], df["Score"], marker='o', linestyle='-', color='green')
    plt.xticks(rotation=45, ha="right")
    plt.title("Student Progress Over Graded Papers")
    plt.xlabel("Graded File")
    plt.ylabel("Score")
    plt.tight_layout()
    plt.grid(True)

    chart_path = os.path.join(folder, "Progress_Chart.png")
    plt.savefig(chart_path)
    plt.close()

    print(f"Progress chart saved to {chart_path}")

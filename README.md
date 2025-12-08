🏭 AHU Filters Dashboard

A Streamlit application for analyzing AHU filter life cycle, RENSA DP loading trends, and RPM-normalized performance.

<p align="left"> <a href="https://ahufiltersdashboard-sat.streamlit.app/"><img src="https://img.shields.io/badge/Live%20Dashboard-Streamlit-brightgreen?logo=streamlit" /></a> <a href="https://github.com/wes88314/AHU_Filters_Dashboard"><img src="https://img.shields.io/badge/GitHub-Repository-blue?logo=github" /></a> <img src="https://img.shields.io/badge/Version-1.0-orange" /> <img src="https://img.shields.io/badge/Status-Production-green" /> </p>
🌐 Live Dashboard

👉 https://ahufiltersdashboard-sat.streamlit.app/

Upload an Excel file and instantly visualize AHU filter performance.

📘 Overview

The AHU Filters Dashboard automates engineering analysis of AHU filter performance using RENSA methodology:

✔ Normalized DP using RPM baseline 1030

✔ Warning (0.63") & EOL (0.84") classifications

✔ DP progression analysis

✔ RPM change detection

✔ Abnormal behavior flagging

✔ Visualizations for easy management review

It compares the latest two measurement dates automatically.

📥 Excel Formatting Requirements

Your Excel file must use a multi-row header with structure:

| AHU Tag | ← Date 1 →|--------|--------| ← Date 2 →|--------|--------|
|---------|---------|--------|--------|---------|--------|--------|
|         | RPM_1   | Hz_1   | Dp_1   | RPM_2   | Hz_2   | Dp_2   |
| AHU_01  | 525     | 27.5   | 0.15   | 554     | 29     | 0.16   |
| AHU_02  | 472     | 25.5   | 0.10   | 498     | 26     | 0.10   |

Column Rules
Column	Requirement
First column	AHU tags
Groups of 3	RPM / Hz / Dp
Minimum dates	2
Allowed missing values	N/A or blank

Additional future dates (RPM_3, Dp_3, etc.) are supported for ingestion but not visualized (reserved for v2.0).

🔧 Core Engineering Logic
RENSA Normalization Formula
DP_normalized = DP_measured × (1030 / RPM_measured)²

Status Classification
Status	Threshold
🟢 Normal	DP < 0.63
🟧 Warning – Replace Soon	0.63 – 0.84
🔴 EOL – Replace Now	≥ 0.84
⚪ No Data	Missing DP or RPM
Abnormal Behavior Detection

Normalized DP drop > 0.15

Normalized DP rise > 0.15

Latest status is Warning/EOL

📊 Dashboard Pages Explained
1️⃣ Bar Chart – Normalized DP Comparison

Visualizes filter loading from Date 1 → Date 2.

Sky Blue → Oldest DP

Orange → Latest DP

Orange dashed line → Warning threshold

Red dashed line → EOL threshold

2️⃣ Bubble Chart – ΔDP vs ΔRPM Quadrants

Bubble = AHU
Size = DP severity
Color = Status
Quadrants detect airflow restrictions, abnormal DP drops, and unusual RPM behavior.

Only abnormal AHUs are labeled to reduce clutter.

3️⃣ Summary Table

Shows:

Column	Description
RPM_old / RPM_new	Raw RPM values
DP_norm_1 / DP_norm_2	Normalized DP
DPnorm_change	Trend severity
RPM_change	Fan speed behavior
Status	Engineering classification
🚀 Try It Locally (Developers Only)

Clone repository:

git clone https://github.com/wes88314/AHU_Filters_Dashboard
cd AHU_Filters_Dashboard


Install dependencies:

pip install -r requirements.txt


Run App:

streamlit run app.py

🗂 Repository Structure
AHU_Filters_Dashboard
│   app.py
│   README.md
│   requirements.txt
│
└── sample_data/
        example.xlsx

☁️ Deployment Notes (Streamlit Cloud)

The dashboard auto-updates whenever you push changes to GitHub.

Deployment URL:
👉 https://ahufiltersdashboard-sat.streamlit.app/

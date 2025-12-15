import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import openpyxl

# ============================================================
# STREAMLIT CONFIG
# ============================================================
st.set_page_config(layout="wide", page_title="AHU Filter Life Cycle Dashboard")
st.title("AHU Filter Life Cycle Dashboard")

# ============================================================
# FILE UPLOAD
# ============================================================
uploaded = st.sidebar.file_uploader("Upload Excel File (.xlsx)", type=["xlsx"])

if uploaded is None:
    st.info("Please upload an Excel (.xlsx) file to begin.")
    st.stop()

# Reject old XLS files
if uploaded.name.lower().endswith(".xls"):
    st.error("This file is XLS (legacy). Please re-save as XLSX and upload again.")
    st.stop()

# ============================================================
# READ EXCEL EXACTLY ONCE (correct fix)
# ============================================================
try:
    df_raw = pd.read_excel(uploaded, header=[0, 1], engine="openpyxl")
except Exception as e:
    st.error(f"Failed to read Excel file: {e}")
    st.stop()

# ============================================================
# FLATTEN MULTI-LEVEL HEADERS
# ============================================================
flat_cols = []
measurement_index = 1

for col in df_raw.columns:
    label1, label2 = col

    # AHU Tag column
    if "Unnamed" in str(label1) or str(label1).strip() == "":
        flat_cols.append("AHU_Tag")
        continue

    # Valid metrics
    if label2 in ["RPM", "Hz", "Dp", "DP"]:
        flat_cols.append(f"{label2}_{measurement_index}")
    else:
        flat_cols.append(f"Col_{measurement_index}")

    # Move to next measurement set after DP
    if label2 in ["Dp", "DP"]:
        measurement_index += 1

df_raw.columns = flat_cols

# ============================================================
# SAFE NUMERIC CONVERSION (AFTER flattening!)
# ============================================================
for c in df_raw.columns:
    if c != "AHU_Tag":
        df_raw[c] = pd.to_numeric(df_raw[c], errors="coerce")

# ============================================================
# DETECT MEASUREMENT SETS
# ============================================================
rpm_cols = sorted([c for c in df_raw.columns if c.startswith("RPM_")], key=lambda x: int(x.split("_")[1]))
dp_cols = sorted([c for c in df_raw.columns if c.startswith("Dp_")], key=lambda x: int(x.split("_")[1]))

if len(rpm_cols) < 2 or len(dp_cols) < 2:
    st.error("Not enough data — need at least 2 dates (RPM + DP).")
    st.stop()

latest = len(rpm_cols)
previous = latest - 1

# ============================================================
# BUILD COMPARISON DF
# ============================================================
df = pd.DataFrame()
df["AHU_Tag"] = df_raw["AHU_Tag"]

df["RPM_old"] = df_raw[f"RPM_{previous}"]
df["DP_old"]  = df_raw[f"Dp_{previous}"]

df["RPM_new"] = df_raw[f"RPM_{latest}"]
df["DP_new"]  = df_raw[f"Dp_{latest}"]

# ============================================================
# NORMALIZATION (RENSA LOGIC)
# ============================================================
RPM_BASELINE = 1030
WARNING_DP = 0.63
EOL_DP = 0.84

def normalize(dp, rpm):
    if rpm == 0 or pd.isna(rpm) or pd.isna(dp):
        return None
    return dp * (RPM_BASELINE / rpm)**2

df["DPnorm_1"] = df.apply(lambda r: normalize(r["DP_old"], r["RPM_old"]), axis=1)
df["DPnorm_2"] = df.apply(lambda r: normalize(r["DP_new"], r["RPM_new"]), axis=1)
df["DPnorm_change"] = df["DPnorm_2"] - df["DPnorm_1"]

df["RPM_change"] = df["RPM_new"] - df["RPM_old"]

# ============================================================
# CLASSIFICATION
# ============================================================
def classify(dp):
    if pd.isna(dp):
        return "No Data"
    if dp >= EOL_DP:
        return "EOL – Replace Now"
    elif dp >= WARNING_DP:
        return "Warning – Replace Soon"
    else:
        return "Normal"

df["Status_old"] = df["DPnorm_1"].apply(classify)
df["Status_new"] = df["DPnorm_2"].apply(classify)

df["Abnormal"] = False
df.loc[df["DPnorm_change"] > 0.15, "Abnormal"] = True
df.loc[df["DPnorm_change"] < -0.15, "Abnormal"] = True
df.loc[df["Status_new"] != "Normal", "Abnormal"] = True

# ============================================================
# PAGE NAVIGATION
# ============================================================
page = st.sidebar.radio("Navigate Pages",
                        ["Page 1 – Bar Chart",
                         "Page 2 – Bubble Diagnostics",
                         "Page 3 – Summary Table"])

# ============================================================
# PAGE 1 — BAR CHART
# ============================================================
if page == "Page 1 – Bar Chart":
    st.header("📊 Normalized DP (Previous vs Latest)")

    fig, ax = plt.subplots(figsize=(22, 7))

    x = np.arange(len(df))

    ax.bar(x - 0.2, df["DPnorm_1"], width=0.4, label="Previous", color="skyblue")
    ax.bar(x + 0.2, df["DPnorm_2"], width=0.4, label="Latest", color="orange")

    ax.axhline(WARNING_DP, color="orange", linestyle="--", linewidth=2, label="Warning (0.63)")
    ax.axhline(EOL_DP, color="red", linestyle="--", linewidth=2, label="EOL (0.84)")

    ax.set_xticks(x)
    ax.set_xticklabels(df["AHU_Tag"], rotation=90)

    ax.set_ylabel("Normalized DP (1030 RPM Baseline)")
    ax.set_title("DP Normalized Comparison")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    st.pyplot(fig)

# ============================================================
# PAGE 2 — BUBBLE CHART
# ============================================================
elif page == "Page 2 – Bubble Diagnostics":

    st.header("🫧 Quadrant Bubble Chart — Δ Normalized DP vs Δ RPM")

    fig, ax = plt.subplots(figsize=(22, 10))

    bubble_size = (df["DPnorm_change"].abs() * 5000) + 200

    bubble_colors = []
    for _, r in df.iterrows():
        if r["Status_new"] == "EOL – Replace Now":
            bubble_colors.append("red")
        elif r["Status_new"] == "Warning – Replace Soon":
            bubble_colors.append("orange")
        elif r["Abnormal"]:
            bubble_colors.append("yellow")
        else:
            bubble_colors.append("green")

    ax.scatter(
        df["RPM_change"], df["DPnorm_change"],
        s=bubble_size, c=bubble_colors, alpha=0.65, edgecolor="black"
    )

    abnormal_df = df[df["Abnormal"] == True]
    for _, r in abnormal_df.iterrows():
        ax.text(r["RPM_change"], r["DPnorm_change"], r["AHU_Tag"],
                fontsize=9, weight="bold", ha="center", va="bottom")

    ax.axhline(0, color="black", linewidth=1)
    ax.axvline(df["RPM_change"].median(), color="black", linewidth=1)

    ax.set_xlabel("RPM Change (Latest - Previous)")
    ax.set_ylabel("Δ Normalized DP")
    ax.set_title("Quadrant Bubble Diagnostic Plot")
    ax.grid(True, alpha=0.3)

    import matplotlib.patches as Patch
    legend_elements = [
        Patch.Patch(facecolor="green", edgecolor="black", label="Normal"),
        Patch.Patch(facecolor="orange", edgecolor="black", label="Warning – Replace Soon"),
        Patch.Patch(facecolor="red", edgecolor="black", label="EOL – Replace Now"),
        Patch.Patch(facecolor="yellow", edgecolor="black", label="Abnormal"),
    ]
    ax.legend(handles=legend_elements, loc="upper left")

    st.pyplot(fig)

# ============================================================
# PAGE 3 — TABLE
# ============================================================
else:
    st.header("📄 Summary Table")
    st.dataframe(df)

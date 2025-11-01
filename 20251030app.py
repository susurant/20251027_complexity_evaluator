import streamlit as st
import yaml
import pandas as pd
from PIL import Image

# --- Page setup ---
st.set_page_config(page_title="Aerodrome Risk Assessment", layout="wide")

st.markdown("""
# 🛫 Aerodrome Risk Assessment Tool
Select the most appropriate condition for each category. 
Your total risk score and level will update automatically.
""")

# --- Custom CSS ---
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background-color: #f4f6f8;
    padding: 2rem;
}
.column-panel {
    border: 1px solid #d1d5db;
    padding: 1rem;
    border-radius: 12px;
    background-color: #ffffff;
}
h2 {
    color: #1f77b4;
}
.stMetric {
    background-color: #e9f7ef;
    border-radius: 10px;
    padding: 0.5rem;
    margin-bottom: 1rem;
}
.stApp {
    background-color: white;
    color: black;
}
.css-1d391kg, .css-10trblm, .css-1d391kg span {
    color: black !important;
}
</style>
""", unsafe_allow_html=True)


# --- CSS for cell styling ---
st.markdown("""
<style>
.yellow-cell {
    background-color: #ffff99;
    font-weight: bold;
    border: 1px solid black;
    padding: 6px 12px;
    text-align: center;
    vertical-align: middle;
}

.blue-cell {
    background-color: #b3e5fc;
    border: 1px solid black;
    padding: 0;
    text-align: center;
    vertical-align: middle;
}

.cell-container > div {
    padding: 6px 12px;
}

/* Make text inputs fill their cell */
.css-1offfwp input[type="text"] {
    background-color: #b3e5fc !important;
    border: none !important;
    text-align: center !important;
    font-weight: bold !important;
    font-size: 1rem !important;
    padding: 6px !important;
    width: 100% !important;
    box-sizing: border-box !important;
}
</style>
""", unsafe_allow_html=True)

# --- Row 1 ---
col1, col2, col3, col4 = st.columns([1, 2, 0.2, 2])

with col1:
    st.markdown('<div class="yellow-cell">AERODROME</div>', unsafe_allow_html=True)
with col2:
    aerodrome_name = st.text_input("", "TAUPO", key="aerodrome_name")
with col3:
    st.write("")  # small empty spacer column
with col4:
    st.write("")  # empty cell to match your image

# --- Row 2: Full width single blue cell ---
st.markdown(f'<div class="blue-cell" style="padding:10px; font-weight:bold;">{aerodrome_name.upper()}</div>', unsafe_allow_html=True)

# --- Row 3: Annual IFR movements ---
col1, col2, col3, col4 = st.columns([1, 2, 1, 2])

with col1:
    st.markdown('<div class="yellow-cell">Annual IFR movements</div>', unsafe_allow_html=True)
with col2:
    annual_ifr_movements = st.text_input("", "10000", key="annual_ifr_movements")
with col3:
    st.markdown('<div style="border:1px solid black; text-align:center; padding:6px;">Annual VFR movements</div>', unsafe_allow_html=True)
with col4:
    annual_vfr_movements = st.text_input("", "30000", key="annual_vfr_movements")

# --- Load scoring YAML ---
@st.cache_data
def load_scores(path="scores.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

SCORES = load_scores()
categories = list(SCORES.keys())
midpoint = len(categories) // 2
left_cats = categories[:midpoint]
right_cats = categories[midpoint:]

# --- Create columns for category selections ---
col1, col2 = st.columns(2)
answers = {}

#st.markdown("<h2 style='text-align: center;'>Aerodrome Risk Assessment Tool</h2>", unsafe_allow_html=True)
#st.markdown("Select the most appropriate condition for each category. Your total risk score and level will update automatically.")

left_cats = list(SCORES.keys())[:7]
right_cats = list(SCORES.keys())[7:]

# with col1:
#     for category in left_cats:
#         st.markdown(f"**{category}**")
#         answers[category] = st.selectbox("", list(SCORES[category].keys()), key=category)

# with col2:
#     for category in right_cats:
#         st.markdown(f"**{category}**")
#         answers[category] = st.selectbox("", list(SCORES[category].keys()), key=category)

# st.divider()
# --- CSS to style selectboxes in compact panels ---
st.markdown("""
<style>
.select-panel {
    border: 1px solid #ccc;
    background-color: #ffffff;
    border-radius: 8px;
    padding: 8px 12px;
    margin-bottom: 15px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

/* Style category labels */
.select-panel strong {
    color: #1f77b4;
    font-size: 1rem;
}

/* Tighten spacing around selectboxes */
div[data-baseweb="select"] {
    margin-top: 4px;
    margin-bottom: 4px;
}

/* Make selectbox text smaller and compact */
span[data-baseweb="tag"] {
    font-size: 0.9rem !important;
}

/* Adjust dropdown look */
div[data-baseweb="popover"] {
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

left_cats = list(SCORES.keys())[:7]
right_cats = list(SCORES.keys())[7:]

# --- Left column ---
with col1:
    for category in left_cats:
        st.markdown(f"<div class='select-panel'><strong>{category}</strong>", unsafe_allow_html=True)
        answers[category] = st.selectbox(
            "",
            list(SCORES[category].keys()),
            key=category
        )
        st.markdown("</div>", unsafe_allow_html=True)

# --- Right column ---
with col2:
    for category in right_cats:
        st.markdown(f"<div class='select-panel'><strong>{category}</strong>", unsafe_allow_html=True)
        answers[category] = st.selectbox(
            "",
            list(SCORES[category].keys()),
            key=category
        )
        st.markdown("</div>", unsafe_allow_html=True)

#st.divider()

# --- Calculate total score ---
total_score = sum(SCORES[c][answers[c]] for c in answers)

# --- Risk level thresholds ---
if total_score <= 20:
    level, color = "Low", "🟢"
elif total_score <= 40:
    level, color = "Moderate", "🟡"
elif total_score <= 55:
    level, color = "High", "🟠"
else:
    level, color = "Very High", "🔴"
# # --- Display results ---
# st.markdown(f"""
# <div class="column-panel">
# <h2>{color} {level} Risk Level</h2>
# <p><b>Total Score:</b> {total_score}</p>
# </div>
# """, unsafe_allow_html=True)

# --- Visualization ---
# df = pd.DataFrame({
#     "Category": list(SCORES.keys()),
#     "Score": [SCORES[c][answers[c]] for c in answers]
# })
# st.bar_chart(df.set_index("Category"))

# # --- Optional download ---
# st.download_button(
#     "Download Assessment Results",
#     df.to_csv(index=False),
#     file_name="risk_assessment.csv",
#     mime="text/csv"
# )

# -----------------------------------------------------------------
# 📊 ADDITIONAL SECTION: Weighted Normalised Aerodrome Index Table
# -----------------------------------------------------------------
st.divider()
st.subheader("Weighted Normalised Aerodrome Index")

# Example fixed data (can later come from logic)
aero_data = {
    "Unattended": 45,
    "UNICOM/AWIB": 44,
    "AFIS": 42,
    "ATC": 40
}

# --- Radio buttons to choose ---
selected = st.radio(
    "Select Aerodrome Type:",
    list(aero_data.keys()),
    horizontal=True
)

# --- Custom HTML Table (styled like your image) ---
highlight_color = "#d1e7dd"  # light green highlight
html_table = f"""
<style>
.custom-table {{
    border-collapse: collapse;
    width: 100%;
    margin-top: 10px;
    text-align: center;
    font-family: Arial, sans-serif;
}}
.custom-table th {{
    border: 2px solid black;
    padding: 8px;
    background-color: #f8f9fa;
    font-weight: bold;
}}
.custom-table td {{
    border: 2px solid black;
    padding: 10px;
    font-size: 16px;
}}
.highlight {{
    background-color: {highlight_color};
    font-weight: bold;
}}
.index-col {{
    font-weight: bold;
    border: 2px solid black;
    background-color: #f8f9fa;
    text-align: left;
    padding-left: 10px;
}}
</style>

<table class="custom-table">
    <tr>
        <th></th>
        <th>Unattended</th>
        <th>UNICOM/AWIB</th>
        <th>AFIS</th>
        <th>ATC</th>
    </tr>
    <tr>
        <td class="index-col">Weighted Normalised<br>Aerodrome Index</td>
        <td class="{ 'highlight' if selected == 'Unattended' else '' }">{aero_data['Unattended']}</td>
        <td class="{ 'highlight' if selected == 'UNICOM/AWIB' else '' }">{aero_data['UNICOM/AWIB']}</td>
        <td class="{ 'highlight' if selected == 'AFIS' else '' }">{aero_data['AFIS']}</td>
        <td class="{ 'highlight' if selected == 'ATC' else '' }">{aero_data['ATC']}</td>
    </tr>
</table>
"""

st.markdown(html_table, unsafe_allow_html=True)

st.markdown(f"**Selected Aerodrome Type:** {selected} — **Index:** {aero_data[selected]}")


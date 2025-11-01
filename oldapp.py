import streamlit as st
import pandas as pd

# --- Page setup ---
st.set_page_config(page_title="Aerodrome Risk Comparison", layout="wide")
st.title("🛫 Aerodrome Risk Assessment Comparison")
st.title("Mike Haines Aviation")

# --- Custom CSS for borders ---
# st.markdown("""
# <style>
# .box {
#     border: 2px solid #4a90e2;
#     border-radius: 10px;
#     padding: 20px;
#     margin-bottom: 20px;
#     background-color: #f9f9f9;
# }
# </style>
# """, unsafe_allow_html=True)

# --- Scoring dictionary (shortened example) ---
import yaml
@st.cache_data
def load_scores_yaml(path="scores.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

SCORES = load_scores_yaml()

# --- Two columns for side-by-side forms ---
#col1, col2 = st.columns(2)

def assessment_form(label):
    """Reusable form block"""
    with st.container():
        st.markdown(f"<div class='box'><h4>{label}</h4>", unsafe_allow_html=True)
        answers = {}
        for cat, opts in SCORES.items():
            st.subheader(cat)
            answers[cat] = st.radio("", list(opts.keys()), key=f"{label}_{cat}", horizontal=True)
        total = sum(SCORES[c][answers[c]] for c in answers)
        if total <= 5:
            lvl, emoji = "Low", "🟢"
        elif total <= 8:
            lvl, emoji = "Moderate", "🟡"
        else:
            lvl, emoji = "High", "🔴"
        st.success(f"**{label} Total:** {total} → {emoji} {lvl}")
        st.markdown("</div>", unsafe_allow_html=True)
        df = pd.DataFrame({"Category": SCORES.keys(), "Score": [SCORES[c][answers[c]] for c in answers]})
        st.bar_chart(df.set_index("Category"))
    return total, lvl

# --- Split into two halves ---
categories = list(SCORES.keys())
midpoint = len(categories) // 2
left_cats = categories[:midpoint]
right_cats = categories[midpoint:]

# --- Create two columns ---
col1, col2 = st.columns(2)
answers = {}

# --- Left column form ---
with col1:
    for category in left_cats:
        st.subheader(category)
        options = list(SCORES[category].keys())
        answers[category] = st.radio(
            "Select one:",
            list(SCORES[category].keys()),
            key=category,
            horizontal=True,  # options appear in one row
        )


# --- Right column form ---
with col2:
    for category in right_cats:
        st.subheader(category)
        options = list(SCORES[category].keys())
        answers[category] = st.radio(
            "Select one:",
            list(SCORES[category].keys()),
            key=category,
            horizontal=True,  # options appear in one row
        )


st.divider()

# --- Render both side-by-side ---
#assessment_form("Aerodrome A")
#with col1:
#    total1, lvl1 = assessment_form("Aerodrome A")

#with col2:
#    total2, lvl2 = assessment_form("Aerodrome B")


# import streamlit as st

# # --- Page setup ---
# st.set_page_config(page_title="Aerodrome Risk Assessment", layout="wide")
# st.title("🛫 Aerodrome Risk Assessment Tool")
# st.write(
#     "Select the most appropriate condition for each category. "
#     "Your total risk score and level will update automatically."
# )

# # --- Scoring matrix ---
# SCORES = {
#     "1. Presence of animals or people on aerodrome": {
#         "Rare": 1,
#         "Common bird hazard": 2,
#         "Livestock, dogs, etc present at times": 3,
#         "People frequently on the manoeuvring area": 4,
#         "Vehicles frequently on the manoeuvring area": 5,
#     },
#     "2. External hazards affecting aerodrome": {
#         "Rare": 1,
#         "Search lights or lasers common": 2,
#         "Pyrotechnics or permanent jet efflux": 3,
#         "Structures": 4,
#         "Wires": 5,
#     },
#     "3. Aeronautical objects affecting aerodrome": {
#         "Rare, small balloons (<1m3)": 1,
#         "Parasaails or gyrogliders": 2,
#         "Rocket activity": 3,
#         "Kites or tethered balloons": 4,
#         "Model aircraft or pilotless aircraft": 5,
#     },
#     "4. Terrain and vegetation": {
#         "Terrain relatively unobstructed and flat": 1,
#         "Adjacent terrain flat but affects aerodrome": 2,
#         "High altitude aerodrome affects performance": 3,
#         "Terrain or trees affect approaches": 4,
#         "Terrain or trees affect circuits or runway": 5,
#     },
#     "5. Common meteorological phenomena": {
#         "Rarely adverse": 1,
#         "Fog or low cloud common": 2,
#         "Common poor visibility": 3,
#         "Moderate turbulence or crosswind common": 4,
#         "Thunderstorms or windshear common": 5,
#     },
#     "6. Aerodrome layout": {
#         "Simple layout": 1,
#         "Rail, marine, road conflict": 2,
#         "Construction or maintenance works common": 3,
#         "Few or no approach and landing aids": 4,
#         "Taxiing across or along runways common": 5,
#     },
#     "7. Runway configuration": {
#         "Single runway": 1,
#         "Parallel separated runways": 2,
#         "Parallel runways (not separated)": 3,
#         "Crossing runways (2 runways)": 4,
#         "Crossing runways (3 or more)": 5,
#     },
#     "8. Aerodrome traffic circuit": {
#         "Single circuit": 1,
#         "Integrated circuits (same direction)": 2,
#         "Opposite direction circuits or noise abatement": 3,
#         "Conflicting circuits": 4,
#         "Conflicting abnormal circuit ops or adjacent aerodrome": 5,
#     },
#     "9. Airspace and procedures": {
#         "Uncontrolled airspace": 1,
#         "Airspace requiring radio use": 2,
#         "Airspace with specified flight procedures": 3,
#         "Special use airspace affecting circuit": 4,
#         "Airspace requiring multiple frequencies": 5,
#     },
#     "10. Common aircraft speed differential": {
#         "<30kt (C172–C206)": 1,
#         "30–49kt (C172–PA34)": 2,
#         "50–69kt (C172–BE1900D)": 3,
#         "70–89kt (C172–B737)": 4,
#         "≥90kt (C172–B747)": 5,
#     },
#     "11. Regular diverse operation types": {
#         "Military aircraft": 1,
#         "Microlight aircraft / hang gliders / helicopters": 2,
#         "Training aircraft or two other types": 3,
#         "Gliding or three other diverse types": 4,
#         "Parachuting or four other diverse types": 5,
#     },
#     "12. Presence of other aircraft - traffic volume": {
#         "Light (<20,000 annual)": 1,
#         "Low (20,000–39,999)": 2,
#         "Moderate (40,000–59,999)": 3,
#         "High (60,000–79,999)": 4,
#         "Very high (80,000+)": 5,
#     },
#     "13. Presence of other aircraft - traffic peaks": {
#         "Daily peaks 5–9 per hour": 1,
#         "Daily peaks 10–19 per hour": 2,
#         "Daily peaks 20–29 per hour": 3,
#         "Daily peaks 30–39 per hour": 4,
#         "Daily peaks 40+ per hour": 5,
#     },
# }

# # --- Collect inputs ---
# st.divider()
# answers = {}

# for category, options in SCORES.items():
#     st.subheader(category)
#     answers[category] = st.radio(
#         "Select one:",
#         list(options.keys()),
#         key=category,
#         horizontal=True,
#     )

# st.divider()

# # --- Calculate total score ---
# total_score = sum(SCORES[cat][answers[cat]] for cat in answers)

# # --- Determine risk level ---
# if total_score <= 20:
#     level, color = "Low", "🟢"
# elif total_score <= 40:
#     level, color = "Moderate", "🟡"
# elif total_score <= 55:
#     level, color = "High", "🟠"
# else:
#     level, color = "Very High", "🔴"

# # --- Sidebar summary ---
# st.sidebar.header("Summary")
# st.sidebar.metric("Total Risk Score", total_score)
# st.sidebar.markdown(f"### {color} {level} Risk Level")

# # --- Main summary ---
# st.success(f"**Total Score:** {total_score} → {color} **{level} Risk**")

# # Optional: Bar chart showing contribution
# import pandas as pd

# df = pd.DataFrame({
#     "Category": list(SCORES.keys()),
#     "Score": [SCORES[c][answers[c]] for c in answers]
# })
# st.bar_chart(df.set_index("Category"))

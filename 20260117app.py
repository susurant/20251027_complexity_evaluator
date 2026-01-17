import streamlit as st
import yaml

# --- Page setup ---
st.set_page_config(page_title="Aerodrome Risk Assessment", layout="wide")

st.markdown("""
# Aerodrome Risk Assessment Tool
Select the most appropriate condition for each category. 
Your total risk score and level will update dynamically.
""")

# Create multiple tabs
tab1, tab2 = st.tabs(["Main Inputs", "Scores"])

with tab1:
    st.write("This is your main input tab.")
    # You can put other inputs or charts here

    # 1️⃣ String input (placed above)
    user_name = st.text_input(
        "",
        placeholder="Enter name..."
    )

    # 2️⃣ Two numeric inputs side by side
    col1, col2 = st.columns(2)

    with col1:
        ifr_value = st.number_input(
            "Annual IFR movements",
            min_value=0.0,
            value=10000.0,
            step=100.0,
            format="%.2f",
            help="Numeric value used to calculate IFR proportion"
        )

    with col2:
        vfr_value = st.number_input(
            "Annual VFR movements",
            min_value=0.0,
            value=20000.0,
            step=100.0,
            format="%.2f",
            help="Numeric value used to calculate VFR proportion"
        )

    st.markdown("""
    # Complexity indicators (leading to pilot workload)				
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

    # --- Load YAML data ---
    @st.cache_data
    def load_yaml(path):
        with open(path, "r") as f:
            return yaml.safe_load(f)

    # IFR scores (numeric values for ATC-I)
    SCORES_IFR = load_yaml("adjusted_ifr.yaml")

    # Text labels mapping to numeric keys
    SCORES_LABELS = load_yaml("scores.yaml")

    SCORES_VFR = load_yaml("adjusted_vfr.yaml")

    # --- Inputs ---

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

    col1, spacer, col2 = st.columns([1, 0.1, 1])

    answers = {}
    categories = list(SCORES_LABELS.keys())
    midpoint = len(categories) // 2
    left_cats = categories[:midpoint]
    right_cats = categories[midpoint:]

    def get_percentage_str(question, selected_text):
        numeric_key = SCORES_LABELS.get(question, {}).get(selected_text)
        if numeric_key is not None:
            value_dict = SCORES_IFR.get(question, {}).get(numeric_key)
            if value_dict is not None:
                percentage = value_dict.get("percentage", 0)
                if percentage != 0:
                    return f" ({percentage:+.0f}%)"
        return ""

    #with col1:
    #    for category in left_cats:
    #        st.markdown(f"<div class='select-panel'><strong>{category}</strong>", unsafe_allow_html=True)
    #        answers[category] = st.selectbox("", list(SCORES_LABELS[category].keys()), key=category)
    with col1:
        for category in left_cats:
            # 1️⃣ Markdown label at the top
            st.markdown(f"**{category}**", unsafe_allow_html=True)

            # 2️⃣ Compute feedback (colored_html) based on previous selection
            prev_selection = st.session_state.get(category, None)
            percentage_labels = []

            if prev_selection:
                numeric_key = SCORES_LABELS.get(category, {}).get(prev_selection)
                groups = ["UNICOM-I", "AFIS-I", "ATC-I"]

                for group in groups:
                    group_questions = SCORES_IFR.get(group, {}).get(category, {})
                    if numeric_key in group_questions:
                        pct = group_questions[numeric_key]["percentage"]
                        percentage_labels.append((group[:-2], pct))

            if percentage_labels:
                colored_html = " | ".join(
                    f"<span style='color:{'red' if pct < 0 else 'green' if pct > 0 else 'black'};"
                    f" font-weight:bold;'>{group}: {pct:+.0f}%</span>"
                    for group, pct in percentage_labels
                )
                # 3️⃣ Show it *below the label, above the selectbox*
                st.markdown(
                    f"<div style='font-size:0.9rem; margin-bottom:4px;'> {colored_html}</div>",
                    unsafe_allow_html=True
                )

            # 4️⃣ Then render the interactive selectbox
            selected_answer = st.selectbox(
                label=category,
                options=list(SCORES_LABELS[category].keys()),
                key=category,
                label_visibility="collapsed"
            )

            answers[category] = selected_answer


    #with col2:
    #    for category in right_cats:
    #        st.markdown(f"<div class='select-panel'><strong>{category}</strong>", unsafe_allow_html=True)
    #        answers[category] = st.selectbox("", list(SCORES_LABELS[category].keys()), key=category)


    with col2:
        for category in right_cats:
            # 1️⃣ Markdown label at the top
            st.markdown(f"**{category}**", unsafe_allow_html=True)

            # 2️⃣ Compute feedback (colored_html) based on previous selection
            prev_selection = st.session_state.get(category, None)
            percentage_labels = []

            if prev_selection:
                numeric_key = SCORES_LABELS.get(category, {}).get(prev_selection)
                groups = ["UNICOM-I", "AFIS-I", "ATC-I"]

                for group in groups:
                    group_questions = SCORES_IFR.get(group, {}).get(category, {})
                    if numeric_key in group_questions:
                        pct = group_questions[numeric_key]["percentage"]
                        percentage_labels.append((group[:-2], pct))

            if percentage_labels:
                colored_html = " | ".join(
                    f"<span style='color:{'red' if pct < 0 else 'green' if pct > 0 else 'black'};"
                    f" font-weight:bold;'>{group}: {pct:+.0f}%</span>"
                    for group, pct in percentage_labels
                )
                # 3️⃣ Show it *below the label, above the selectbox*
                st.markdown(
                    f"<div style='font-size:0.9rem; margin-bottom:4px;'> {colored_html}</div>",
                    unsafe_allow_html=True
                )

            # 4️⃣ Then render the interactive selectbox
            selected_answer = st.selectbox(
                label=category,
                options=list(SCORES_LABELS[category].keys()),
                key=category,
                label_visibility="collapsed"
            )

            answers[category] = selected_answer


                #st.markdown("IFR: " + f", ".join(percentage_labels),unsafe_allow_html=True)

    # --- Calculate total score ---
    total_score = 0
    for category, selected_text in answers.items():
        numeric_key = SCORES_LABELS.get(category, {}).get(selected_text)
        if numeric_key is not None:
            total_score += numeric_key  # total "risk" score (based on label mapping)

    groups = ["IFR", "UNICOM-I", "AFIS-I","ATC-I"]
    ifr_totals = {}

    #for group in groups:
    #    total_ifr = 0.0
    #    group_questions = SCORES_IFR.get(group, {})
        
    #    for question, selected_text in answers.items():
    #        if question in group_questions:
    #            numeric_key = SCORES_LABELS.get(question, {}).get(selected_text)
    #            if numeric_key is not None:
    #                total_ifr += float(group_questions[question].get(numeric_key, 0))
    #    ifr_totals[group] = total_ifr
    for group in groups:
        total_ifr = 0.0
        group_questions = SCORES_IFR.get(group, {})
        
        for question, selected_text in answers.items():
            if question in group_questions:
                # Map the answer text to numeric key
                numeric_key = SCORES_LABELS.get(question, {}).get(selected_text)
                if numeric_key is not None:
                    # Grab the "value" from the YAML/dict structure
                    value_dict = group_questions[question].get(numeric_key, {'value': 0, 'percentage': 0})
                    value_dict = group_questions[question].get(numeric_key)  # this should be {'value': ..., 'percentage': ...}
                    if isinstance(value_dict, dict):
                        val = value_dict.get("value", 0)
                        total_ifr += float(val)
                    else:
                        total_ifr += 0  # fallback if something went wrong
                    #total_ifr += float(value_dict.get("value", 0))
        
        ifr_totals[group] = total_ifr

        
    groups = ["VFR", "UNICOM-V", "AFIS-V","ATC-V"]
    vfr_totals = {}

    # for group in groups:
    #     total_vfr = 0.0
    #     group_questions = SCORES_VFR.get(group, {})
    #     for question, selected_text in answers.items():
    #         if question in group_questions:
    #             numeric_key = SCORES_LABELS.get(question, {}).get(selected_text)
    #             if numeric_key is not None:
    #                 total_vfr += float(group_questions[question].get(numeric_key, 0))
    #     vfr_totals[group] = total_vfr

    for group in groups:
        total_vfr = 0.0
        group_questions = SCORES_VFR.get(group, {})
        
        for question, selected_text in answers.items():
            if question in group_questions:
                # Map the answer text to numeric key
                numeric_key = SCORES_LABELS.get(question, {}).get(selected_text)
                if numeric_key is not None:
                    # Grab the "value" from the YAML/dict structure
                    value_dict = group_questions[question].get(numeric_key, {'value': 0, 'percentage': 0})
                    value_dict = group_questions[question].get(numeric_key)  # this should be {'value': ..., 'percentage': ...}
                    if isinstance(value_dict, dict):
                        val = value_dict.get("value", 0)
                        total_vfr += float(val)
                    else:
                        total_vfr += 0  # fallback if something went wrong
                    #total_ifr += float(value_dict.get("value", 0))
        
        vfr_totals[group] = total_vfr

    # --- Calculate proportional weights ---
    total_value = ifr_value + vfr_value
    ifr_ratio = ifr_value / total_value if total_value > 0 else 0.25
    vfr_ratio = vfr_value / total_value if total_value > 0 else 0.75

    #total_ifr = total_ifr * 0.145
    #ifr_totals = [group * 0.145 for group in ifr_totals]
    # Multiply all IFR totals by 0.145 and round to nearest integer
    num = 0.145455 #200/(vfr_totals["VFR"] + ifr_totals["IFR"])
    ifr_totals = {group: round(total) for group, total in ifr_totals.items()}
    vfr_totals = {group: round(total) for group, total in vfr_totals.items()}
    #result = {k: ((ifr_totals[k] *0.25) + (vfr_totals[k] * 0.75)) * num for k in ifr_totals}

    new_keys = ['Unattended', 'ATC', 'AFIS','UNICOM/AWIB']


    #result = {
    #f'key{i}': ((v1 * 0.25) + (v2 * 0.75))
    #    for i, (v1, v2) in enumerate(zip(ifr_totals.values(), vfr_totals.values()), 1)
    #}
    from decimal import Decimal, ROUND_HALF_UP

    result = {
            new_key: int(Decimal(((v1 * ifr_ratio) + (v2 * vfr_ratio)) * num ).quantize(Decimal('1'), rounding=ROUND_HALF_UP))  #new_key: round(((v1 * 0.25) + (v2 * 0.75)))
        for new_key, (v1, v2) in zip(new_keys, zip(ifr_totals.values(), vfr_totals.values()))
    }

    # --- Optional: Weighted Aerodrome Index ---
    aero_data = result

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
        color: black;  /* ensures header text is black */
    }}
    .custom-table td {{
        border: 2px solid black;
        padding: 10px;
        font-size: 16px;
        color: black;  /* ensures header text is black */
    }}
    .highlight {{
        background-color: {highlight_color};
        font-weight: bold;
        color: black;  /* ensures header text is black */

    }}
    .index-col {{
        font-weight: bold;
        border: 2px solid black;
        background-color: #f8f9fa;
        text-align: left;
        padding-left: 10px;
        color: black;  /* ensures header text is black */
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
            <td class="{ 'highlight' if selected == 'ATC' else '' }">{aero_data['ATC']}</td>
            <td class="{ 'highlight' if selected == 'AFIS' else '' }">{aero_data['AFIS']}</td>
            <td class="{ 'highlight' if selected == 'UNICOM/AWIB' else '' }">{aero_data['UNICOM/AWIB']}</td>
        </tr>
    </table>
    """

    st.markdown(html_table, unsafe_allow_html=True)

    import pandas as pd
    from io import BytesIO

    # --- Prepare DataFrames for export ---
    # 1️⃣ Questions and selected answers
    questions_df = pd.DataFrame(list(answers.items()), columns=["Question", "Selected Answer"])

    # 2️⃣ IFR and VFR totals
    ifr_df = pd.DataFrame(list(ifr_totals.items()), columns=["IFR Group", "IFR Total"])
    vfr_df = pd.DataFrame(list(vfr_totals.items()), columns=["VFR Group", "VFR Total"])

    # 3️⃣ Final weighted results
    results_df = pd.DataFrame(list(result.items()), columns=["Aerodrome Type", "Weighted Index"])

    # 4️⃣ Metadata (inputs and ratios)
    meta_df = pd.DataFrame({
        "Identifier": [user_name],
        "IFR Value": [ifr_value],
        "VFR Value": [vfr_value],
        "IFR Ratio": [ifr_ratio],
        "VFR Ratio": [vfr_ratio],
        "Selected Aerodrome": [selected],
        "Selected Index": [aero_data[selected]]
    })

    # --- Combine all data into an Excel file ---
    output = BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        meta_df.to_excel(writer, index=False, sheet_name="Summary")
        questions_df.to_excel(writer, index=False, sheet_name="Questions")
        ifr_df.to_excel(writer, index=False, sheet_name="IFR Totals")
        vfr_df.to_excel(writer, index=False, sheet_name="VFR Totals")
        results_df.to_excel(writer, index=False, sheet_name="Weighted Results")

    # Move to start of the BytesIO buffer
    output.seek(0)

    # --- Streamlit download button ---
    st.download_button(
        label="📥 Download Results as Excel",
        data=output,
        file_name=f"aerodrome_assessment_{user_name or 'entry'}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
with tab2:

    ifr = ifr_totals
    vfr = vfr_totals
    # Map section names to sheet prefixes
    section_to_prefix = {
        "With ATC": "ATC",
        "With AFIS": "AFIS",
        "With UNICOM": "UNICOM",
    }

    sections = {
        "AERODROME INDEX": ["IFR", "VFR"],
        "No ATS": ["IFR Score", "VFR Score", "Weighted Score"],
        "With ATC": ["IFR Score", "VFR Score", "Weighted Score"],
        "With AFIS": ["IFR Score", "VFR Score", "Weighted Score"],
        "With UNICOM": ["IFR Score", "VFR Score", "Weighted Score"],
    }

    def get_raw_score(section, row):
        if section == "AERODROME INDEX":
            if row == "IFR":
                return f"{round(float(ifr_ratio) * 100, 0)}%"
            if row == "VFR":
                return f"{round(float(vfr_ratio) * 100, 0)}%"

        if section == "No ATS":
            if row == "IFR Score":
                return ifr_totals.get("IFR", "")
            elif row == "VFR Score":
                return vfr_totals.get("VFR", "")
            elif row == "Weighted Score":
                i_val = ifr_totals.get("IFR", "")
                v_val = vfr_totals.get("VFR", "")
                return int(Decimal((i_val * ifr_ratio) + (v_val * vfr_ratio)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
            else:
                return ""

        # For With ATC, With AFIS, With UNICOM
        prefix = section_to_prefix.get(section)
        if not prefix:
            return ""

        if row == "IFR Score":
            return ifr_totals.get(f"{prefix}-I", "")
        elif row == "VFR Score":
            return vfr_totals.get(f"{prefix}-V", "")
        elif row == "Weighted Score":
            i_val = ifr_totals.get(f"{prefix}-I")
            v_val = vfr_totals.get(f"{prefix}-V")
            if i_val is not None and v_val is not None:
                return int(Decimal((i_val * ifr_ratio) + (v_val * vfr_ratio)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
            else:
                return ""
        else:
            return ""


    # ---- Build DataFrame ----
    rows = []
    raw_vals = []

    for section, row_names in sections.items():
        rows.append(section)  # Section header
        raw_vals.append("")
        for row in row_names:
            rows.append(row)
            raw_vals.append(get_raw_score(section, row))

    df = pd.DataFrame({"Raw": raw_vals}, index=rows)

    # ---- Normalised column ----
    def normalise(value):
        try:
            return int(Decimal(float(value) * 0.145).quantize(Decimal('1'), rounding=ROUND_HALF_UP)) #round(float(value) * 0.145, 2)
        except (ValueError, TypeError):
            return ""

    df["Normalised"] = df["Raw"].apply(normalise)


    # Streamlit display
    #st.set_page_config(page_title="Aerodrome Scores Table", layout="centered")
    st.title("✈️ Aerodrome Scoring Table")
    st.table(df)
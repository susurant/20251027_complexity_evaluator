import pandas as pd
import yaml

# --- File and sheet names ---
excel_file = "C:\\Users\\User\\Downloads\\Aerodrome Complexity Taupo TEST.xlsm"
ifrs_sheet = "IFR"
atc_sheets = ["ATC-I", "ATC-V", "AFIS-I", "AFIS-V", "UNICOM-I", "UNICOM-V","IFR"]

# --- Read IFR sheet ---
ifrs_df = pd.read_excel(excel_file, sheet_name=ifrs_sheet,    usecols="A:F",nrows=13)
ifrs_df.columns = [str(c).strip() for c in ifrs_df.columns]
ifrs_df.set_index(ifrs_df.columns[0], inplace=True)
ifrs_df.columns = range(1, len(ifrs_df.columns) + 1)

print(ifrs_df)
# Clean question names
def clean_questions(s):
    return str(s).strip().replace("\n", " ").replace("\r", " ")

ifrs_df.index = ifrs_df.index.map(clean_questions)

# --- Ensure IFR values are numeric ---
ifrs_df = ifrs_df.apply(pd.to_numeric, errors='coerce').fillna(0)

# --- Function to read ATC sheet and convert factors ---
def read_atc_sheet(sheet_name):
    df = pd.read_excel(excel_file, sheet_name=sheet_name,    usecols="A:F",nrows=13)
    df.columns = [str(c).strip() for c in df.columns]
    df.set_index(df.columns[0], inplace=True)
    df.index = df.index.map(clean_questions)

    # Convert percentages to multipliers
    if sheet_name not in ("IFR","VFR"):
        def pct_to_mult(x):
            if pd.isna(x):
                return 1.0
            try:
                val = float(str(x).replace("%",""))
                return 1 + (val*100) / 100.0
            except:
                return 1.0

        df_mult = df.applymap(pct_to_mult)
        df_mult.columns = range(1, len(df.columns) + 1)
        return df_mult
    else:
        def pct_to_mult(x):
            if pd.isna(x):
                return 1.0
            try:
                val = float(str(x).replace("%",""))
                return 1.0 * (val*100) / 100.0
            except:
                return 1.0

        df_mult = df.applymap(pct_to_mult)
        df_mult.columns = range(1, len(df.columns) + 1)
        return df_mult

# --- Process all ATC sheets ---
adjusted_ifr = {}

for sheet in atc_sheets:
    print(sheet)
    atc_mult_df = read_atc_sheet(sheet)
    if (sheet == "IFR" or sheet ==  "VFR"):
        #adjusted_ifr_dict = atc_mult_df
        print('aa')
        adjusted_ifr[sheet] = atc_mult_df

        adjusted_ifr_dict = {sheet: df.to_dict(orient='index') for sheet, df in adjusted_ifr.items()}
    else:
    # Align with IFR questions
        common_questions = ifrs_df.index.intersection(atc_mult_df.index)
        aligned_ifr = ifrs_df.loc[common_questions].fillna(0)
        aligned_atc = atc_mult_df.loc[common_questions].reindex(columns=aligned_ifr.columns).fillna(1.0)

        # --- Ensure numeric multiplication ---
        aligned_ifr = aligned_ifr.apply(pd.to_numeric, errors='coerce').fillna(0)
        aligned_atc = aligned_atc.apply(pd.to_numeric, errors='coerce').fillna(1.0)
        # Multiply IFR × ATC factor
        final_df = aligned_ifr * aligned_atc
        adjusted_ifr[sheet] = final_df

        adjusted_ifr_dict = {sheet: df.to_dict(orient='index') for sheet, df in adjusted_ifr.items()}
# --- Save to YAML ---
with open("adjusted_ifr.yaml", "w") as f:
    yaml.dump(adjusted_ifr_dict, f, sort_keys=False)

# --- Example ---
# adjusted_ifr["AFIS-I"]

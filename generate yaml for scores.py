import pandas as pd
import yaml

# --- Configuration ---
excel_file = "C:\\Users\\User\\Downloads\\Aerodrome Complexity Taupo TEST.xlsm" #"ATC_Factors.xlsx"
ifrs_sheet = "IFR"        # Sheet with IFR values
atc_sheets = ["ATC-I", "ATC-V", "AFIS-I", "AFIS-V", "UNICOM-I", "UNICOM-V"]  # Sheets with ATC factor adjustments

# --- Read IFR values ---
ifrs_df = pd.read_excel(excel_file, sheet_name=ifrs_sheet, usecols="A:F")
IFR_MAP_FULL = {}
for _, row in ifrs_df.iterrows():
    category = row.iloc[0]
    IFR_MAP_FULL[category] = {i: row.iloc[i] for i in range(1, 6)}

# --- Read ATC factors and convert percentages to multipliers ---
ATC_FACTORS_FULL = {}
for sheet in atc_sheets:
    df = pd.read_excel(excel_file, sheet_name=sheet, usecols="A:F")
    atc_dict = {}
    for _, row in df.iterrows():
        category = row.iloc[0]
        atc_dict[category] = {}
        for i in range(1, 6):
            cell = row.iloc[i]
            if pd.isna(cell):
                continue
            # Convert percent to factor: -10 -> 0.9
            factor = 1 + float(cell) / 100
            atc_dict[category][i] = factor
    ATC_FACTORS_FULL[sheet] = atc_dict

# --- Calculate Adjusted IFR ---
ADJUSTED_IFR = {}
for atc_level, categories in ATC_FACTORS_FULL.items():
    adjusted_dict = {}
    for category, scores in IFR_MAP_FULL.items():
        adjusted_dict[category] = {}
        for score, ifr_value in scores.items():
            factor = categories.get(category, {}).get(score, 1)  # default factor = 1
            adjusted_dict[category][score] = ifr_value * factor
    ADJUSTED_IFR[atc_level] = adjusted_dict

# --- Optional: Convert to DataFrame ---
adjusted_dfs = {}
for atc_level, data in ADJUSTED_IFR.items():
    df = pd.DataFrame(data).T
    df.index.name = "Category"
    df.columns = [f"Score {i}" for i in df.columns]
    adjusted_dfs[atc_level] = df

# --- Save YAML ---
with open("adjusted_ifr.yaml", "w") as f:
    yaml.dump(ADJUSTED_IFR, f)

print("✅ Adjusted IFR calculated correctly using percent adjustments.")
import pandas as pd
import yaml

# --- File and sheet names ---
#excel_file = "C:\\Users\\User\\Downloads\\Aerodrome Complexity Taupo TEST.xlsm"
excel_file = "C:\\Users\\User\\Downloads\\ACE Word Pictures.xlsx"

ifrs_sheet = "VFR"
atc_sheets = ["ATC-I", "ATC-V", "AFIS-I", "AFIS-V", "UNICOM-I", "UNICOM-V", "IFR"]

# --- Read IFR sheet ---
#ifrs_df = pd.read_excel(excel_file, sheet_name=ifrs_sheet, usecols="A:F", nrows=13)
ifrs_df = pd.read_excel(excel_file, sheet_name=ifrs_sheet, usecols="A:F", nrows=20)

ifrs_df.columns = [str(c).strip() for c in ifrs_df.columns]
ifrs_df.set_index(ifrs_df.columns[0], inplace=True)
ifrs_df.columns = range(1, len(ifrs_df.columns) + 1)

# Clean question names
def clean_questions(s):
    return str(s).strip().replace("\n", " ").replace("\r", " ")

ifrs_df.index = ifrs_df.index.map(clean_questions)
ifrs_df = ifrs_df.apply(pd.to_numeric, errors='coerce').fillna(0)

# --- Function to read ATC sheets and convert to (multiplier, raw percentage) ---
def read_atc_sheet(sheet_name):
    df = pd.read_excel(excel_file, sheet_name=sheet_name, usecols="A:F", nrows=20)
    df.columns = [str(c).strip() for c in df.columns]
    df.set_index(df.columns[0], inplace=True)
    df.index = df.index.map(clean_questions)

    if sheet_name in ("IFR","VFR"):
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
    # Convert each value to (multiplier, raw_percentage)
    else:
        def pct_to_mult_and_raw(x):
            if pd.isna(x):
                return (1.0, 0.0)
            try:
                if isinstance(x, str):
                    val = float(x.replace("%", "").strip())
                    raw = val
                    mult = 1 + (raw / 100.0)
                else:
                    # If already numeric (0.1 = 10%)
                    raw = x * 100.0
                    mult = 1 + x
                return (mult, raw)
            except:
                return (1.0, 0.0)

        df = df.applymap(pct_to_mult_and_raw)
        df.columns = range(1, len(df.columns) + 1)
        return df

# --- Process all ATC sheets ---
adjusted_ifr = {}

for sheet in atc_sheets:
    print(sheet)
    atc_mult_df = read_atc_sheet(sheet)

    if sheet in ("IFR", "VFR"):
        #def unpack_if_tuple(x):
        #    if isinstance(x, tuple):
        #        return float(x[0])  # take the value
        #    elif pd.notnull(x):
        #        return float(x)
        #    else:
        #        return 0.0
        #print(atc_mult_df)
        #adjusted_ifr[sheet] = atc_mult_df.applymap(unpack_if_tuple).to_dict(orient='index')
        # Convert IFR DataFrame to dict-of-dict-of-dict
        sheet_dict = {}
        for question in atc_mult_df.index:
            sheet_dict[question] = {}
            for col in atc_mult_df.columns:
                val = atc_mult_df.loc[question, col]
                sheet_dict[question][col] = {"value": float(val), "percentage": 0.0}
        adjusted_ifr[sheet] = sheet_dict
    else:
        # Align questions with IFR
        common_questions = ifrs_df.index.intersection(atc_mult_df.index)
        aligned_ifr = ifrs_df.loc[common_questions].fillna(0)
        aligned_atc_mult = atc_mult_df.loc[common_questions]

        # Separate multiplier and raw percentage
        aligned_atc_values = aligned_atc_mult.applymap(lambda t: t[0])  # multiplier
        aligned_atc_raws = aligned_atc_mult.applymap(lambda t: t[1])    # raw %

        # Multiply IFR × ATC multiplier
        final_df = aligned_ifr * aligned_atc_values

        # Build the YAML structure with value + percentage
        sheet_dict = {}
        for question in final_df.index:
            sheet_dict[question] = {}
            for col in final_df.columns:
                mult, raw = aligned_atc_mult.loc[question, col]  # unpack tuple
                sheet_dict[question][col] = {
                    "value": int(round(aligned_ifr.loc[question, col] * mult)),
                    "percentage": int(round(raw, 3))
                }

                #sheet_dict[question][col] = {
                #    "value": int(round(final_df.loc[question, col], 3)),
                #    "percentage": int(round(aligned_atc_raws.loc[question, col], 3))
                #}

        adjusted_ifr[sheet] = sheet_dict

# --- Save to YAML ---
with open("adjusted_vfr.yaml", "w") as f:
    #yaml.dump(adjusted_ifr, f, sort_keys=False, allow_unicode=True, default_flow_style=False)
    yaml.dump(adjusted_ifr, f, sort_keys=False)
print("YAML file saved as 'adjusted_ifr_2.yaml'")

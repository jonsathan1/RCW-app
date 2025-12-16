import streamlit as st
import pandas as pd

# ------------------------------------------------------------
# 1. GOOGLE SHEETS CONFIG
# ------------------------------------------------------------
SHEET_ID = "1zyRj8Idn6SE0wd3iBBefz8Bk6-U2Cce98AdxGVDbox0"
CRIMES_SHEET_NAME = "crimes"
ELEMENTS_SHEET_NAME = "elements"

def make_csv_export_url(sheet_name: str) -> str:
    return (
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
        f"/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    )

def load_sheet_as_df(url: str) -> pd.DataFrame:
    return pd.read_csv(url)

# ------------------------------------------------------------
# 2. LOAD DATA ONCE PER SESSION
# ------------------------------------------------------------
crimes_filename = "Crimes and Their Elements - Crimes"
elements_filename = "Crimes and Their Elements - Elements"

if "dataframes" not in st.session_state:
    crimes_url = make_csv_export_url(CRIMES_SHEET_NAME)
    elements_url = make_csv_export_url(ELEMENTS_SHEET_NAME)

    crimes_df = load_sheet_as_df(crimes_url)
    elements_df = load_sheet_as_df(elements_url)

    # Optional: save locally if you still want the CSVs
    crimes_df.to_csv(f"{crimes_filename}.csv", index=False)
    elements_df.to_csv(f"{elements_filename}.csv", index=False)

    st.session_state["dataframes"] = {
        crimes_filename: crimes_df,
        elements_filename: elements_df
    }

dataframes = st.session_state["dataframes"]

# ------------------------------------------------------------
# 3. SELECT CRIME
# ------------------------------------------------------------
if crimes_filename in dataframes:
    crimes_df = dataframes[crimes_filename]

    option_list = crimes_df["Title"].dropna().tolist()
    selected_crime = st.selectbox("Select a crime:", option_list)

# ------------------------------------------------------------
# 4. SHOW AVENUES AS BUTTONS
# ------------------------------------------------------------
if elements_filename in dataframes and "selected_crime" in locals():
    elements_df = dataframes[elements_filename]

    avenue_rows = elements_df[elements_df["Title"] == selected_crime]
    avenues = avenue_rows["group_text"].dropna().tolist()

    if avenues:
        st.markdown("### Select an avenue of commission:")

        for avenue in avenues:
            if st.button(avenue, key=f"avenue_{avenue}"):
                selected_avenue = avenue

                group_number_row = elements_df[
                    elements_df["group_text"] == selected_avenue
                ]

                if not group_number_row.empty:
                    group_id = group_number_row["group_id"].iloc[0]

                    element_rows = elements_df[
                        (elements_df["group_id"] == group_id) &
                        (elements_df["Title"] == selected_crime)
                    ]

                    elements_list = (
                        element_rows["element_text"]
                        .dropna()
                        .tolist()
                    )

                    st.markdown("### Elements of the crime (copyable):")
                    checkbox_text = "\n".join(
                        f"[ ] {elem}" for elem in elements_list
                    )
                    st.markdown(f"```\n{checkbox_text}\n```")

    else:
        st.info("No avenues found for this crime.")
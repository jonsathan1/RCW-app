import streamlit as st
import pandas as pd

# ------------------------------------------------------------
# 1. AUTOMATIC GOOGLE SHEETS IMPORT
# ------------------------------------------------------------
SHEET_ID = "1zyRj8Idn6SE0wd3iBBefz8Bk6-U2Cce98AdxGVDbox0"
CRIMES_SHEET_NAME = "crimes"
ELEMENTS_SHEET_NAME = "elements"

def make_csv_export_url(sheet_name):
    return f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

@st.cache_data
def load_sheet_as_df(url: str) -> pd.DataFrame:
    return pd.read_csv(url)

# Load Google Sheets tabs
crimes_url = make_csv_export_url(CRIMES_SHEET_NAME)
elements_url = make_csv_export_url(ELEMENTS_SHEET_NAME)

crimes_df = load_sheet_as_df(crimes_url)
elements_df = load_sheet_as_df(elements_url)

# Save as exact filenames your program expects
crimes_filename = "Crimes and Their Elements - Crimes"
elements_filename = "Crimes and Their Elements - Elements"

crimes_df.to_csv(f"{crimes_filename}.csv", index=False)
elements_df.to_csv(f"{elements_filename}.csv", index=False)

# Store in expected dictionary format
dataframes = {
    crimes_filename: crimes_df,
    elements_filename: elements_df
}

st.success("Google Sheets loaded successfully! The program is ready.")

# ------------------------------------------------------------
# 2. MOBILE-FRIENDLY CRIME SELECTION
# ------------------------------------------------------------
if crimes_filename in dataframes:
    crimes_df = dataframes[crimes_filename]
    all_crimes = crimes_df["Title"].dropna().tolist()

    # Search box for mobile-friendly crime filtering
    search_query = st.text_input("Search for a crime:")

    if search_query:
        filtered_crimes = [c for c in all_crimes if search_query.lower() in c.lower()]
        if not filtered_crimes:
            st.warning("No crimes match your search.")
    else:
        filtered_crimes = all_crimes

    selected_crime = st.selectbox("Select a crime:", filtered_crimes)

# ------------------------------------------------------------
# 3. SHOW AVENUES AND ELEMENTS
# ------------------------------------------------------------
if elements_filename in dataframes and 'selected_crime' in locals():
    elements_df = dataframes[elements_filename]

    # Filter element groups for the selected crime
    avenue_rows = elements_df[elements_df["Title"] == selected_crime]
    avenues = avenue_rows["group_text"].dropna().tolist()

    if avenues:
        st.markdown("### Select an avenue of commission:")
        for avenue in avenues:
            if st.button(avenue):
                selected_avenue = avenue

                # Retrieve group_id for the clicked avenue
                group_number_row = elements_df[elements_df["group_text"] == selected_avenue]
                if not group_number_row.empty:
                    group_id = group_number_row["group_id"].iloc[0]

                    # Get all elements matching this group_id + crime
                    element_rows = elements_df[
                        (elements_df["group_id"] == group_id) &
                        (elements_df["Title"] == selected_crime)
                    ]
                    elements_list = element_rows["element_text"].dropna().tolist()

                    # Display elements in copy-friendly format
                    st.markdown("### Elements of the crime
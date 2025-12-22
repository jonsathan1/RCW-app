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


def load_sheet_as_df(sheet_name: str) -> pd.DataFrame:
    url = make_csv_export_url(sheet_name)
    return pd.read_csv(url)


# ------------------------------------------------------------
# 2. RENDER-SAFE TEXT HELPERS
# ------------------------------------------------------------
def escape_markdown(text: str) -> str:
    """
    Escapes characters that Streamlit/Markdown interpret specially.
    Currently escapes '$' to prevent LaTeX rendering.
    """
    if not isinstance(text, str):
        return text
    return text.replace("$", r"\$")


# ------------------------------------------------------------
# 3. LOAD DATA ONCE PER SESSION
# ------------------------------------------------------------
if "dataframes" not in st.session_state:
    st.session_state["dataframes"] = {
        "crimes": load_sheet_as_df(CRIMES_SHEET_NAME),
        "elements": load_sheet_as_df(ELEMENTS_SHEET_NAME),
    }

crimes_df = st.session_state["dataframes"]["crimes"]
elements_df = st.session_state["dataframes"]["elements"]

# ------------------------------------------------------------
# 4. SELECT CRIME
# ------------------------------------------------------------
crime_titles = (
    crimes_df["Title"]
    .dropna()
    .unique()
    .tolist()
)

selected_crime = st.selectbox("Select a crime:", crime_titles)

# Reset selected avenue if crime changes
if selected_crime != st.session_state.get("last_crime"):
    st.session_state.pop("selected_avenue", None)
    st.session_state["last_crime"] = selected_crime

# ------------------------------------------------------------
# 5. SHOW AVENUES OF COMMISSION
# ------------------------------------------------------------
avenue_rows = elements_df[
    elements_df["Title"] == selected_crime
]

avenues = (
    avenue_rows["group_text"]
    .dropna()
    .unique()
    .tolist()
)

if not avenues:
    st.info("No avenues found for this crime.")
    st.stop()

st.markdown("### Select an avenue of commission:")

for avenue in avenues:
    display_avenue = escape_markdown(avenue)

    if st.button(
        display_avenue,
        key=f"avenue_{selected_crime}_{avenue}"
    ):
        st.session_state["selected_avenue"] = avenue

# ------------------------------------------------------------
# 6. DISPLAY ELEMENTS FOR SELECTED AVENUE
# ------------------------------------------------------------
if "selected_avenue" in st.session_state:
    selected_avenue = st.session_state["selected_avenue"]

    # 🔑 group_id MUST be scoped to both crime AND avenue
    group_row = elements_df[
        (elements_df["Title"] == selected_crime) &
        (elements_df["group_text"] == selected_avenue)
    ]

    if group_row.empty:
        st.error("No matching elements found for this avenue.")
        st.stop()

    group_id = group_row["group_id"].iloc[0]

    element_rows = elements_df[
        (elements_df["Title"] == selected_crime) &
        (elements_df["group_id"] == group_id)
    ]

    elements_list = (
        element_rows["element_text"]
        .dropna()
        .tolist()
    )

    if not elements_list:
        st.warning("This avenue has no listed elements.")
        st.stop()

    st.markdown("### Elements of the crime (copyable):")

    checklist_text = "\n".join(
        f"- [ ] {escape_markdown(elem)}"
        for elem in elements_list
    )

    st.markdown(checklist_text)

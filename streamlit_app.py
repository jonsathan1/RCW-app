# Import necessary libraries
import streamlit as st  # Streamlit for web app interface
import pandas as pd      # Pandas for working with tables (CSV files)

# Step 1: File uploader for multiple CSV files
uploaded_files = st.file_uploader(
    "Upload TWO CSV files",
    type="csv",
    accept_multiple_files=True
)

# Step 2: Store uploaded CSVs in a dictionary
dataframes = {}  # Keys = filenames, Values = pandas DataFrames
if uploaded_files:
    for f in uploaded_files:
        filename = f.name.rsplit(".", 1)[0]  # Remove .csv extension
        df = pd.read_csv(f)
        dataframes[filename] = df
        #st.write(f"Loaded: {filename}")
        #st.write(df)

# Step 3: Select crime from dropdown
crimes_key = "Crimes and Their Elements - Crimes"
if crimes_key in dataframes:
    crimes_df = dataframes[crimes_key]
    option_list = crimes_df["Title"].dropna().tolist()
    selected_crime = st.selectbox("Select a crime:", option_list)

# Step 4: Show avenues as buttons based on selected crime
elements_key = "Crimes and Their Elements - Elements"
if elements_key in dataframes and 'selected_crime' in locals():
    elements_df = dataframes[elements_key]

    # Filter for the selected crime
    avenue_rows = elements_df[elements_df["Title"] == selected_crime]
    avenues = avenue_rows["group_text"].dropna().tolist()

    st.markdown("### Select an avenue of commission:")
    for avenue in avenues:
        if st.button(avenue):
            selected_avenue = avenue
            #st.write(f"You clicked: {selected_avenue}")

            # Find group_id for this avenue
            group_number_row = elements_df[elements_df["group_text"] == selected_avenue]
            group_id = group_number_row["group_id"].iloc[0]
            #st.write(group_id)
    
            if not group_number_row.empty:

                # Get all element_texts for this group_id
                element_rows = elements_df[(elements_df["group_id"] == group_id) & (elements_df["Title"] == selected_crime)]
                elements_list = element_rows["element_text"].dropna().tolist()

                # Display as copyable checkbox-style code block
                st.markdown("### Elements of the crime (copyable):")
                checkbox_text = "\n".join([f"[ ] {elem}" for elem in elements_list])
                st.markdown(f"```\n{checkbox_text}\n```")




import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from dotenv import load_dotenv
import os
import time

if "firstload" not in st.session_state:
    st.session_state["firstload"] = True

st.title("📦 Category & Item Manager")


def firs_load():

    with st.spinner("Loading google credentials"):
        time.sleep(3)

        if "creds" not in st.session_state:
            # Load environment variables
            load_dotenv()
            credentials = os.getenv('CREDENTIALS')

            st.session_state["scope"] = ["https://www.googleapis.com/auth/spreadsheets"]
            st.session_state["creds"] = ServiceAccountCredentials.from_json_keyfile_name(credentials, st.session_state["scope"])
            st.session_state["client"] = gspread.authorize(st.session_state["creds"])

        if "sheetID" not in st.session_state:
            st.session_state["sheetID"] = "1Iw23vgFJqgrmVFBJWG10fb5ZltFjchU12X3OgcfeonY"
    
    with st.spinner("Fetching data"):
        time.sleep(2)

        st.session_state["spreadsheet"] = st.session_state["client"].open_by_key(st.session_state["sheetID"]) 
        st.session_state["sheetslist"] = [sheet.title for sheet in st.session_state["spreadsheet"].worksheets()] # List of all sheets names
        st.session_state["CATEGORIE"] = st.session_state["client"].open_by_key(st.session_state["sheetID"]).sheet1
        
        # Fetch all data from Google Sheets
        st.session_state["categoriesdata"] = st.session_state["CATEGORIE"].get_all_records()
        st.session_state["df"] = pd.DataFrame(st.session_state["categoriesdata"])
    
    with st.spinner("Creating interface"):
        time.sleep(2)

        # Extract unique categories
        st.session_state["categorieslist"] = st.session_state["df"]["Category"].unique().tolist() if not st.session_state["df"].empty else []
        st.session_state["categorieslist"].insert(0, "➕ Add New Category")  # Default option
            
    
    
    st.session_state["firstload"] = False


if st.session_state["firstload"] == True:
    firs_load()



# Category Selection
selected_category = st.selectbox("Select a category:", st.session_state["categorieslist"])

# Handle new category input
if selected_category == "➕ Add New Category":
    new_category = st.text_input("Enter new category:")
else:
    new_category = selected_category  # Use existing category

# Input for new item
item = st.text_input("Enter item name:")

# Save data to Google Sheets
if st.button("Save Item"):


    if new_category and item:
        if new_category not in st.session_state["sheetslist"]:
            new_sheet = st.session_state["spreadsheet"].add_worksheet(f'{new_category}',1000,26)
            new_sheet.append_row([item]) # Append item to its category sheet

        else:
            sheet_to_append = st.session_state["spreadsheet"].worksheet(new_category)
            sheet_to_append.append_row([item])

        if new_category not in st.session_state["categorieslist"]:
            st.session_state["CATEGORIE"].append_row([new_category])  # Append category to first sheet(list of categories)
            st.session_state["categorieslist"].append(new_category) 

        with st.spinner("Loading new data"):
            time.sleep(3)

            st.session_state["spreadsheet"] = st.session_state["client"].open_by_key(st.session_state["sheetID"]) 
            st.session_state["sheetslist"] = [sheet.title for sheet in st.session_state["spreadsheet"].worksheets()] # List of all sheets names
            st.session_state["CATEGORIE"] = st.session_state["client"].open_by_key(st.session_state["sheetID"]).sheet1

            # Fetch all data from Google Sheets
            st.session_state["categoriesdata"] = st.session_state["CATEGORIE"].get_all_records()
            st.session_state["df"] = pd.DataFrame(st.session_state["categoriesdata"])


        st.success(f"Added '{item}' to category '{new_category}'!")

        st.rerun()  # Refresh page to show updated data
    else:
        st.warning("Please enter both category and item.")

# Display stored data
st.subheader("📋 Stored Categories")
st.dataframe(st.session_state["df"])

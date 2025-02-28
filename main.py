import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()
credentials = os.getenv('CREDENTIALS')

# Google Sheets Authentication
scope = ["https://www.googleapis.com/auth/spreadsheets"]
creds = ServiceAccountCredentials.from_json_keyfile_name(credentials, scope)
client = gspread.authorize(creds)

# Open the Google Sheet
SHEET_ID = "1Iw23vgFJqgrmVFBJWG10fb5ZltFjchU12X3OgcfeonY"  # Change this to your Google Sheet name
spreadsheet = client.open_by_key(SHEET_ID) 
sheets_list = [sheet.title for sheet in spreadsheet.worksheets()] # List of all sheets names
print(sheets_list)
CATEGORIE = client.open_by_key(SHEET_ID).sheet1

st.title("📦 Category & Item Manager")

# Fetch all data from Google Sheets
data = CATEGORIE.get_all_records()
df = pd.DataFrame(data)

# Extract unique categories
list_of_categories = df["Category"].unique().tolist() if not df.empty else []
list_of_categories.insert(0, "➕ Add New Category")  # Default option

# Category Selection
selected_category = st.selectbox("Select a category:", list_of_categories)

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
        if new_category not in sheets_list:
            new_sheet = spreadsheet.add_worksheet(f'{new_category}',1000,26)
            new_sheet.append_row([item]) # Append item to its category sheet
        else:
            sheet_to_append = spreadsheet.worksheet(new_category)
            sheet_to_append.append_row([item])

        if new_category not in list_of_categories:
            CATEGORIE.append_row([new_category])  # Append category to first sheet(list of categories)
        
        st.success(f"Added '{item}' to category '{new_category}'!")
        st.rerun()  # Refresh page to show updated data
    else:
        st.warning("Please enter both category and item.")

# Display stored data
st.subheader("📋 Stored Categories")
st.dataframe(df)

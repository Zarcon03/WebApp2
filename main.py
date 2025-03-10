import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from dotenv import load_dotenv
import os
import time

if "firstload" not in st.session_state:
    st.session_state["firstload"] = True

if "currentcategorydf" not in st.session_state:
    st.session_state["currentcategorydf"] = pd.DataFrame()

if "objectinstance" not in st.session_state:
    st.session_state["objectinstance"] = []

if "index" not in st.session_state:
    st.session_state["index"] = 0

st.title("📦 Category & Item Manager")


def first_load():

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
        st.session_state["CATEGORIE"] = st.session_state["spreadsheet"].worksheet("CATEGORIE")
        
        # Fetch all data from Google Sheets
        categories_data = st.session_state["CATEGORIE"].get_all_records()
        st.session_state["df"] = pd.DataFrame(categories_data)
    
    with st.spinner("Creating interface"):
        time.sleep(2)

        # Extract unique categories
        st.session_state["categorieslist"] = st.session_state["df"]["Category"].unique().tolist() if not st.session_state["df"].empty else []
        st.session_state["categorieslist"].insert(0, "➕ Add New Category")  # Default option
            
    
    
    st.session_state["firstload"] = False

def add_row_to_existing_category(category):

    current_category = f"{category}"
    st.session_state[current_category] = st.session_state["spreadsheet"].worksheet(current_category)
    values = st.session_state[current_category].get_all_values()
    st.session_state["currentcategorydf"] = pd.DataFrame(values[1:], columns=values[0])

    columns = st.session_state["currentcategorydf"].columns.tolist()

    ## STORE THE INSTANCES OF THE OBJECT INTO A LIST
    if st.session_state["index"] < len(columns):
        value = st.text_input(f"Insert the value for '{st.session_state["currentcategorydf"].columns[st.session_state["index"]]}' instance")
        if st.button("Next"):
            if value:
                st.session_state["objectinstance"].append(value)
                st.session_state["index"] += 1
                
                st.success("The instance has been succesfully added")
                st.rerun()
            else:
                st.warning("Enter value")
        

    ## THE LIST IS FULL LOAD AND RESET
    elif st.session_state["index"] == len(columns):
        st.toast("All values entered", icon="✅") ## Cool gadget, top right corner appears message for 4 seconds

        ## TIME TO LOAD THE DATA TO THE RIGHT SHEET

        # show saved instances before loading
        st.subheader("📦 Object to Store")
        st.table(st.session_state["objectinstance"])

        # define the two cols
        col1, col2 = st.columns(2)
        
        # button to load
        with col1:
            if st.button("Save Object"):
                st.session_state[current_category].append_row(st.session_state["objectinstance"])

                ## RESET THE VALUES OF OBJECTINSTANCE AND INDEX
                st.session_state["objectinstance"] = []
                st.session_state["index"] = 0

                with st.spinner("Loading object"):
                    time.sleep(1)
                st.rerun()
        
        # button to reset
        with col2:
            if st.button("Reset Object"):
                st.session_state["index"] = 0
                st.session_state["objectinstance"] = []

                st.rerun()

def create_new_category(category):
    if category:
        if category in st.session_state["categorieslist"]:
            st.warning("The category already exists")
        
        if "items" not in st.session_state:
            st.session_state["items"] = []

        item = st.text_input(f"Enter item associated with category: {category}", key="input_item")

        # Check if Enter was pressed (input changed)
        if item and st.session_state.get("last_item") != item:
            st.session_state["last_item"] = item
            if item in st.session_state["items"]:
                st.warning(f"The item: {item} has already been added")
            else:
                st.session_state["items"].append(item)
                st.success(f"Item: {item} has been added")
                time.sleep(1)
                st.rerun()  # Refresh app to clear input field

        ## DIVIDE IN COLUMNS THE TWO BUTTONS
        col1, col2 = st.columns(2)
        with col1:
            add_button = st.button("Add Item")
        with col2:
            complete_button = st.button("Complete")
            
        ## CREATE THE ACTION CALLS FOR THE TWO BUTTONS
        if add_button:
            if item:
                if item in st.session_state["items"]:
                    st.warning(f"The item: {item} has already been added")
                else:
                    st.session_state["items"].append(item)

                    st.success(f"item: {item} has been added")
                    st.rerun()
            else:
                st.warning("Please enter an item")

        if complete_button:
            if st.session_state["items"] == []:
                st.warning("You have not entered any item")
            elif category in st.session_state["categorieslist"]:
                st.warning("The category is already in the system")
            else:
                with st.spinner("Loading your new category into the system"):

                    ## CREATE THE CATEGORY SHEET AND INSERT THE ITEM ROW
                    if category not in st.session_state["categorieslist"]:
                        new_sheet = st.session_state["spreadsheet"].add_worksheet(f'{category}',1000,len(st.session_state["items"]))
                        new_sheet.append_row(st.session_state["items"])

                        st.session_state["CATEGORIE"].append_row([category])  # Append category to first sheet(list of categories)
                        st.session_state["categorieslist"].append(category)
                    

                        placeholder = st.empty()  # Create a placeholder for text

                        # Display entered items inside the placeholder
                        with placeholder.container():
                            st.write("### Items entered:")
                            for i in st.session_state["items"]:
                                st.write(f"{i}")

                        time.sleep(3)  # Simulate loading time

                        # Clear the placeholder content after spinner ends
                        placeholder.empty()

                        st.session_state["items"] = []

                with st.spinner("Updating new data"):
                    time.sleep(3)

                    st.session_state["spreadsheet"] = st.session_state["client"].open_by_key(st.session_state["sheetID"]) 
                    st.session_state["CATEGORIE"] = st.session_state["spreadsheet"].worksheet("CATEGORIE")

                    # Fetch all data from Google Sheets
                    categories_data = st.session_state["CATEGORIE"].get_all_records()
                    st.session_state["df"] = pd.DataFrame(categories_data)
                
                st.rerun()
                    

    else:
        st.warning("Enter the category")


if st.session_state["firstload"] == True:
    first_load()

# Category Selection
selected_category = st.selectbox("Select a category:", st.session_state["categorieslist"])

# Handle new category input
if selected_category == "➕ Add New Category":
    new_category = st.text_input("Enter new category:")
    create_new_category(new_category)

    # Display stored data
    st.subheader("📋 Stored Categories")
    st.dataframe(st.session_state["df"])
else:
    add_row_to_existing_category(selected_category)
    # Display stored data
    st.subheader("📋 Stored Objects")
    st.dataframe(st.session_state["currentcategorydf"])
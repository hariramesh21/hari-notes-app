import streamlit as st
import gspread
import pandas as pd
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import time

try:
    # Authenticate with Google Sheets using secrets
    gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
    # Open the specific Google Sheet by its name
    sh = gc.open("Streamlit_Notes_App") 
except Exception as e:
    # Display an error message if connection fails and stop the app
    st.error(f"Failed to connect to Google Sheets. Please check your secrets and sheet name. Error: {e}")
    st.stop() # Stop the app execution if connection fails

# Assuming notes are in the first worksheet (index 0)
worksheet = sh.get_worksheet(0)

# --- Functions for Google Sheets operations ---

def load_notes():
    """
    Loads notes from the Google Sheet into a dictionary.
    Handles cases where the sheet might be empty or lack 'title'/'content' columns.
    """
    try:
        # Get all data from the worksheet as a Pandas DataFrame
        df = get_as_dataframe(worksheet)
        
        # Check if the DataFrame is empty or if required columns are missing
        if df.empty or 'title' not in df.columns or 'content' not in df.columns:
            # If empty or columns are missing, return an empty dictionary
            # This ensures the app starts fresh if the sheet is new or malformed
            return {}
        
        # Convert DataFrame rows into a dictionary format {title: content}
        notes = {}
        for index, row in df.iterrows():
            # Ensure both title and content are strings to avoid potential issues
            title = str(row['title'])
            content = str(row['content'])
            notes[title] = content
        return notes
    except Exception as e:
        st.error(f"Error loading notes from Google Sheets: {e}")
        return {} # Return empty notes on error

def save_notes(notes):
    """
    Saves notes from the dictionary to the Google Sheet.
    Clears the existing sheet and rewrites all notes.
    """
    try:
        # Convert the notes dictionary back into a Pandas DataFrame
        # Ensure column order for consistency
        df = pd.DataFrame(notes.items(), columns=['title', 'content'])
        
        # Clear the entire worksheet before writing to ensure no old data remains
        worksheet.clear()
        # Write the DataFrame to the worksheet, including the header
        set_with_dataframe(worksheet, df, include_column_header=True)
    except Exception as e:
        st.error(f"Error saving notes to Google Sheets: {e}")

# --- Streamlit app setup ---

st.title("My Permanent Notes App")

# Initialize session state variables only if they don't exist
# This is crucial for Streamlit's rerun model
if "notes" not in st.session_state:
    st.session_state.notes = load_notes()
if "current_note_key" not in st.session_state:
    st.session_state.current_note_key = ""
if "current_note_content" not in st.session_state:
    st.session_state.current_note_content = ""

# --- Sidebar for note selection and management ---

st.sidebar.header("Notes List")

# "New Note" button with a unique key to prevent re-initialization issues
if st.sidebar.button("➕ New Note", key="new_note_button"):
    timestamp = int(time.time())
    st.session_state.current_note_key = f"Untitled Note ({timestamp})"
    st.session_state.current_note_content = ""
    st.rerun() # Rerun to immediately show the new empty note in the main area

note_keys = list(st.session_state.notes.keys())
# Sort notes alphabetically for better user experience
note_keys.sort() 

for key in note_keys:
    # Dynamically create buttons for each note, ensuring unique keys
    if st.sidebar.button(key, key=f"select_note_{key}"):
        st.session_state.current_note_key = key
        st.session_state.current_note_content = st.session_state.notes[key]
        st.rerun() # Rerun to immediately show the selected note in the main area

# --- Main area for viewing and editing notes ---

if st.session_state.current_note_key:
    st.header(f"Editing: {st.session_state.current_note_key}")

    # Text inputs for title and content
    new_title = st.text_input("Note Title", st.session_state.current_note_key, key="note_title_input")
    new_content = st.text_area("Note Content", st.session_state.current_note_content, height=300, key="note_content_input")

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("💾 Save Note", key="save_note_button"):
            # If the title has changed, remove the old entry from notes
            if new_title != st.session_state.current_note_key:
                if st.session_state.current_note_key in st.session_state.notes:
                    del st.session_state.notes[st.session_state.current_note_key]
                st.session_state.current_note_key = new_title # Update the current key

            # Save the new/updated note content
            st.session_state.notes[st.session_state.current_note_key] = new_content
            save_notes(st.session_state.notes)
            st.success(f"Note '{st.session_state.current_note_key}' saved to Google Sheets!")
            st.rerun() # Rerun to refresh the sidebar and main area

    with col2:
        if st.button("🗑️ Delete Note", key="delete_note_button"):
            if st.session_state.current_note_key in st.session_state.notes:
                del st.session_state.notes[st.session_state.current_note_key]
                save_notes(st.session_state.notes)
                
                # Clear the current note selection after deletion
                st.session_state.current_note_key = ""
                st.session_state.current_note_content = ""
                st.success("Note deleted!")
                st.rerun() # Rerun to refresh the sidebar and clear the main area
else:
    st.info("Select a note from the sidebar or click '➕ New Note' to get started.")


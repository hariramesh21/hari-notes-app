import streamlit as st
import gspread
import pandas as pd
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import time

# --- Google Sheets Setup ---
try:
    gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
    sh = gc.open("Streamlit_Notes_App") # Use the name of your Google Sheet
except Exception as e:
    st.error(f"Failed to connect to Google Sheets: {e}")
    st.stop()

worksheet = sh.get_worksheet(0) # Assuming notes are in the first sheet

# --- Functions for Google Sheets operations ---

def load_notes():
    """Loads notes from the Google Sheet."""
    df = get_as_dataframe(worksheet)
    if df.empty or 'title' not in df.columns:
        return {}
    # Convert DataFrame to a dictionary
    notes = {}
    for index, row in df.iterrows():
        notes[row['title']] = row['content']
    return notes

def save_notes(notes):
    """Saves notes to the Google Sheet."""
    df = pd.DataFrame(notes.items(), columns=['title', 'content'])
    # Clear and rewrite the entire sheet to simplify updates and deletes
    worksheet.clear()
    set_with_dataframe(worksheet, df)

# --- Streamlit app setup ---

st.title("My Permanent Notes App")

if "notes" not in st.session_state:
    st.session_state.notes = load_notes()
if "current_note_key" not in st.session_state:
    st.session_state.current_note_key = ""
if "current_note_content" not in st.session_state:
    st.session_state.current_note_content = ""

# --- Sidebar for note selection and management ---

st.sidebar.header("Notes List")

if st.sidebar.button("➕ New Note"):
    timestamp = int(time.time())
    st.session_state.current_note_key = f"Untitled Note ({timestamp})"
    st.session_state.current_note_content = ""

note_keys = list(st.session_state.notes.keys())
for key in note_keys:
    if st.sidebar.button(key, key=f"select_{key}"):
        st.session_state.current_note_key = key
        st.session_state.current_note_content = st.session_state.notes[key]

# --- Main area for viewing and editing notes ---

if st.session_state.current_note_key:
    st.header(f"Editing: {st.session_state.current_note_key}")

    new_title = st.text_input("Note Title", st.session_state.current_note_key)
    new_content = st.text_area("Note Content", st.session_state.current_note_content, height=300)

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("💾 Save Note"):
            # If title changed, update the key
            if new_title != st.session_state.current_note_key:
                if st.session_state.current_note_key in st.session_state.notes:
                    del st.session_state.notes[st.session_state.current_note_key]
                st.session_state.current_note_key = new_title

            st.session_state.notes[st.session_state.current_note_key] = new_content
            save_notes(st.session_state.notes)
            st.success(f"Note '{st.session_state.current_note_key}' saved to Google Sheets!")

    with col2:
        if st.button("🗑️ Delete Note"):
            if st.session_state.current_note_key in st.session_state.notes:
                del st.session_state.notes[st.session_state.current_note_key]
                save_notes(st.session_state.notes)
                st.session_state.current_note_key = ""
                st.session_state.current_note_content = ""
                st.success("Note deleted!")
else:
    st.info("Select a note from the sidebar or click 'New Note' to get started.")

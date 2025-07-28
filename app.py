import streamlit as st
import json
import os

# Define the file path for saving notes
NOTES_FILE = "notes.json"

# --- Functions for file operations ---

def load_notes():
    """Loads notes from a JSON file."""
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r") as f:
            return json.load(f)
    return {}

def save_notes(notes):
    """Saves notes to a JSON file."""
    with open(NOTES_FILE, "w") as f:
        json.dump(notes, f, indent=4)

# --- Streamlit app setup ---

st.title("My Permanent Notes App")

# Load notes on first run and store in session state
if "notes" not in st.session_state:
    st.session_state.notes = load_notes()
if "current_note_key" not in st.session_state:
    st.session_state.current_note_key = ""
if "current_note_content" not in st.session_state:
    st.session_state.current_note_content = ""

# --- Sidebar for note selection and management ---

st.sidebar.header("Notes List")

# Create a "New Note" button
if st.sidebar.button("➕ New Note"):
    st.session_state.current_note_key = f"Untitled Note {len(st.session_state.notes) + 1}"
    st.session_state.current_note_content = ""

# Display the list of notes
note_keys = list(st.session_state.notes.keys())
for key in note_keys:
    if st.sidebar.button(key, key=f"select_{key}"):
        st.session_state.current_note_key = key
        st.session_state.current_note_content = st.session_state.notes[key]

# --- Main area for viewing and editing notes ---

if st.session_state.current_note_key:
    st.header(f"Editing: {st.session_state.current_note_key}")

    # Text input for the note title
    new_title = st.text_input("Note Title", st.session_state.current_note_key)

    # Text area for the note content
    new_content = st.text_area(
        "Note Content",
        st.session_state.current_note_content,
        height=300
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("💾 Save Note"):
            # Update the note and save to file
            if new_title != st.session_state.current_note_key:
                # If title changed, create a new entry and delete the old one
                del st.session_state.notes[st.session_state.current_note_key]
                st.session_state.current_note_key = new_title

            st.session_state.notes[st.session_state.current_note_key] = new_content
            save_notes(st.session_state.notes)
            st.success(f"Note '{st.session_state.current_note_key}' saved!")

    with col2:
        if st.button("🗑️ Delete Note"):
            # Delete the note and save to file
            if st.session_state.current_note_key in st.session_state.notes:
                del st.session_state.notes[st.session_state.current_note_key]
                save_notes(st.session_state.notes)
                st.session_state.current_note_key = "" # Clear the current note view
                st.session_state.current_note_content = ""
                st.success("Note deleted!")
    
else:
    st.info("Select a note from the sidebar or click 'New Note' to get started.")
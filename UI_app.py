import streamlit as st
import os
import sys
import logging
from dotenv import load_dotenv
import shutil

# --- Page configuration ---
st.set_page_config(
    page_title="eLearning Assistant",
    page_icon="static/EY-logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Load custom CSS ---
def load_css():
    try:
        with open("static/style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("CSS file not found. Using default styling.")
load_css()

# --- Initialize session state ---
def init_session_state():
    defaults = {
        "uploaded_files": [],
        "chat_history": [],
        "processing": False,
        "input_key": 0,
        "graph": None,
        "files_processed": False,
        "uploaded_file_names": [],
        "current_status": "Ready to upload files"
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session_state()

# --- Logging and environment setup ---
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('logs/elearning.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# --- Import backend utilities ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from Utilities.Core import upload_study_pdfs, upload_answer_pdfs, list_pdfs_in_directory, prepare_academic_context

# --- Utility: Get uploaded files ---
def get_uploaded_files():
    """Lists all PDF files currently in Data/Upload directory."""
    upload_dir = "Data/Upload"
    if not os.path.exists(upload_dir):
        logging.warning(f"Upload directory {upload_dir} does not exist")
        return []
    
    files = [
        os.path.join(upload_dir, f)
        for f in os.listdir(upload_dir)
        if f.lower().endswith(".pdf")
    ]
    logging.info(f"Found uploaded files: {files}")
    return files

# --- Process uploaded files with backend ---
def process_uploaded_files():
    """Process uploaded files using the backend utilities."""
    try:
        # Prepare academic context (embeddings, etc.)
        collection, embedder, total_chunks = prepare_academic_context()
        st.session_state.files_processed = True
        st.session_state.current_status = f"Files processed successfully! {total_chunks} text chunks extracted and embedded."
        return f"Files processed successfully! {total_chunks} text chunks extracted and embedded."
    except Exception as e:
        st.session_state.current_status = f"Error processing files: {str(e)}"
        st.error(f"Error processing files: {str(e)}")
        return f"Error processing files: {str(e)}"

# --- Universal process_user_input ---
def process_user_input(user_input):
    if not user_input.strip():
        return "Please enter a question."
    
    if not st.session_state.files_processed:
        return "Please upload and process files first before asking questions."
    
    try:
        st.session_state.processing = True
        
        # Build graph if not exists
        if st.session_state.graph is None:
            from agentic_graph import build_agentic_graph
            st.session_state.graph = build_agentic_graph()
        
        uploaded_files = get_uploaded_files()
        logging.info(f"Processing user input: '{user_input}' with files: {uploaded_files}")
        
        data = {
            "input": user_input,
            "query": user_input,
            "uploaded_files": uploaded_files
        }
        
        # Process the request
        result = st.session_state.graph.invoke(data)
        
        if result.get("error"):
            return f"Error: {result.get('error')}"
        
        # Extract the response
        response = result.get("response", "Done.")
        if result.get("files"):
            files_list = "\n".join([f"→ {f}" for f in result["files"]])
            response += f"\n\nGenerated Files:\n{files_list}"
        
        return response
        
    except Exception as e:
        logging.error(f"Error in process_user_input: {e}")
        return f"Error processing request: {str(e)}"
    finally:
        st.session_state.processing = False

# --- Sidebar ---
with st.sidebar:
    st.image("static/EY-logo.png", width=150)
    st.markdown("---")
    
    # Status display
    st.markdown("### Status")
    if st.session_state.files_processed:
        st.success("Files Processed")
    else:
        st.warning("Files Not Processed")
    
    st.markdown(f"**Current Status:** {st.session_state.current_status}")
    
    # Clear conversation button
    if st.button("Clear Conversation", key="clear_chat"):
        st.session_state.chat_history = []
        st.session_state.input_key += 1
        st.rerun()
    
    st.markdown("---")
    st.markdown("## Upload File")
    uploaded_files = st.file_uploader(
        "Upload files",
        type=['pdf'],
        accept_multiple_files=True,
        label_visibility="collapsed",
        help="Upload your study materials"
    )
    
    if uploaded_files:
        st.info(f"{len(uploaded_files)} file(s) selected")
        
    if st.button("Submit File", key="submit_file"):
        if not uploaded_files:
            st.warning("Please upload at least one file before clicking Submit.")
        else:
            with st.spinner("Processing files..."):
                os.makedirs("Data/Upload", exist_ok=True)
                st.session_state.uploaded_file_names = []
                
                for uploaded_file in uploaded_files:
                    file_path = os.path.join("Data/Upload", uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    st.session_state.uploaded_file_names.append(uploaded_file.name)
                
                # Process files with backend
                result = process_uploaded_files()
                st.success(result)
                st.rerun()
    
    st.markdown("---")
    st.markdown("## Uploaded Files")
    if st.session_state.uploaded_file_names:
        for file in st.session_state.uploaded_file_names:
            st.markdown(f"- {file}")
    else:
        st.markdown("*No files uploaded yet.*")
    
    st.markdown("---")
    st.markdown("## Generated Files")
    if os.path.exists("Data/Output"):
        output_files = os.listdir("Data/Output")
        if output_files:
            for file in output_files:
                file_path = os.path.join("Data/Output", file)
                if os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        st.download_button(
                            label=f"Download {file}",
                            data=f.read(),
                            file_name=file,
                            mime="application/octet-stream"
                        )
        else:
            st.markdown("*No files generated yet.*")
    else:
        st.markdown("*No files generated yet.*")
    
    st.markdown("---")
    st.markdown("## History")
    if st.session_state.chat_history:
        for i, chat in enumerate(st.session_state.chat_history):
            st.markdown(f"**Q{i+1}:** {chat['user']}")
    else:
        st.markdown("*No history yet.*")

# --- Main area ---
st.markdown("# eLearning Assistant")

# --- Status indicator ---
if st.session_state.files_processed:
    st.success("Files processed successfully. You can now ask questions.")
else:
    st.warning("Please upload and process files first.")

# --- Conversation history ---
if st.session_state.chat_history:
    st.markdown("### Recent Conversation")
    for i, chat in enumerate(st.session_state.chat_history[-5:]):  # Show last 5 conversations
        with st.chat_message("user"):
            st.markdown(f"**Question:** {chat['user']}")
        with st.chat_message("assistant"):
            st.markdown(chat['bot'])
        st.markdown("---")
else:
    st.info("Welcome! Upload a file and ask questions to get started.")

# --- Processing indicator ---
if st.session_state.processing:
    with st.spinner("Processing your request..."):
        st.info("Please wait while I process your question...")

# --- Chat input form at bottom ---
st.markdown("### Ask a Question")
st.markdown("Please submit a file then ask your question")

# Display current processing status
if st.session_state.processing:
    with st.spinner("Processing your request..."):
        st.info("Please wait while I process your question...")

# Fix: Use columns to put text input and button side by side
col1, col2 = st.columns([4, 1])
with col1:
    user_input = st.text_input(
        "Ask your query here",
        placeholder="e.g., 'create a study plan for 4 weeks', 'generate a hard quiz', 'ask a question about history'",
        label_visibility="collapsed",
        key=f"user_input_{st.session_state.input_key}"
    )
with col2:
    ask_button = st.button("Ask", key=f"ask_button_{st.session_state.input_key}")

# Use button instead of form submit
if ask_button:
    if user_input and user_input.strip():
        if not st.session_state.files_processed:
            st.warning("Please submit files before asking a question.")
        else:
            # Process the user input
            with st.spinner("Processing your question..."):
                response = process_user_input(user_input.strip())
            
            # Add to chat history
            st.session_state.chat_history.append({"user": user_input.strip(), "bot": response})
            st.session_state.input_key += 1
            
            # Force a rerun to display the response
            st.rerun()
    else:
        st.warning("Please enter a question.")

# --- Footer ---
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #888; font-size: 12px;">
        Powered by LangGraph & Streamlit | eLearning Assistant v1.0
    </div>
    """,
    unsafe_allow_html=True
) 
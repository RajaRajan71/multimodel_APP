import os
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv

# 1. Setup
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

st.set_page_config(page_title="Palludagam AI", layout="wide", page_icon="💐")

# 2. Initialize Session State
if "document_content" not in st.session_state: st.session_state.document_content = ""
if "last_response" not in st.session_state: st.session_state.last_response = ""
if "permanent_payload" not in st.session_state: st.session_state.permanent_payload = []

# --- UI Styling ---
st.markdown("""
    <style>
    .upload-success { padding: 10px; background-color: #064E3B; border-radius: 5px; color: #10B981; font-weight: bold; margin-top: 10px; }
    .file-badge { background-color: #1E293B; padding: 4px 10px; border-radius: 6px; margin-right: 8px; font-size: 0.9em; border: 1px solid #38BDF8; color: white; display: inline-block; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

st.title("🚀 Palludagam Multi-Media Hub")

# --- STEP 1: MULTI-UPLOADER ---
st.subheader("📁 1. Uploading Section")
tabs = st.tabs(["📄 Multi-File Upload", "📸 Camera", "🎙️ Voice"])

with tabs[0]:
    files = st.file_uploader("Upload as many files as you need", accept_multiple_files=True)
    if files:
        st.session_state.permanent_payload = files 
        st.markdown("<div class='upload-success'>✅ Uploading Finished!</div>", unsafe_allow_html=True)

with tabs[1]:
    if st.toggle("Enable Camera"):
        p = st.camera_input("Take Snapshot")
        if p: 
            st.session_state.permanent_payload = [p]
            st.success("✅ Photo Ready!")

with tabs[2]:
    if st.toggle("Enable Mic"):
        v = st.audio_input("Record Audio")
        if v: 
            st.session_state.permanent_payload = [v]
            st.success("✅ Voice Ready!")

# --- DISPLAY ATTACHED FILES ---
if st.session_state.permanent_payload:
    st.write("### 📎 Attached for Analysis:")
    for f in st.session_state.permanent_payload:
        st.markdown(f"<span class='file-badge'>📄 {f.name}</span>", unsafe_allow_html=True)

st.markdown("---")

# --- STEP 2: RESULTS & EDITOR ---
if st.session_state.last_response:
    st.subheader("✨ Latest Analysis Result")
    st.info(st.session_state.last_response)

st.subheader("📝 Live Document Editor")
st.session_state.document_content = st.text_area("Compiled Report:", value=st.session_state.document_content, height=250)

# --- ACTION BUTTONS (Download & Clear) ---
col_down, col_clear, col_empty = st.columns([0.2, 0.2, 0.6])

with col_down:
    if st.session_state.document_content:
        st.download_button(
            label="📥 Download Report",
            data=st.session_state.document_content,
            file_name="palludagam_report.txt",
            mime="text/plain",
            use_container_width=True
        )

with col_clear:
    if st.button("🗑️ Clear All", use_container_width=True):
        st.session_state.document_content = ""
        st.session_state.last_response = ""
        st.session_state.permanent_payload = []
        st.rerun()

st.markdown("---")

# --- STEP 3: CHAT INPUT ---
if prompt := st.chat_input("Ask about your uploaded items..."):
    with st.spinner("🤖 Analyzing..."):
        try:
            gemini_parts = []
            if st.session_state.permanent_payload:
                for f in st.session_state.permanent_payload:
                    m_type = getattr(f, 'type', 'application/octet-stream')
                    gemini_parts.append(types.Part.from_bytes(data=f.getvalue(), mime_type=m_type))
            
            gemini_parts.append(prompt)
            
            # --- MODEL UPDATED HERE TO 1.5 FLASH ---
            response = client.models.generate_content(model="gemini-1.5-flash", contents=gemini_parts)
            
            st.session_state.last_response = response.text
            st.session_state.document_content += f"\n\n--- Analysis ---\n{response.text}"
            st.rerun()
            
        except Exception as e:
            st.error(f"Error: {e}")

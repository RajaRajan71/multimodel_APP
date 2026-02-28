import os
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv

# 1. Setup
load_dotenv()
# The SDK automatically finds GEMINI_API_KEY from environment/Docker
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

st.set_page_config(page_title="Palludagam AI 2026", layout="wide", page_icon="🚀")

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

st.title("🚀 Palludagam Multi-Media Hub (v2026)")

# --- STEP 1: UPLOADING ---
st.subheader("📁 1. Uploading Section")
files = st.file_uploader("Upload Images, PDFs, Audio, or Video", accept_multiple_files=True)
if files:
    st.session_state.permanent_payload = files 
    st.markdown("<div class='upload-success'>✅ Files Ready for Analysis!</div>", unsafe_allow_html=True)

# --- DISPLAY ATTACHED FILES ---
if st.session_state.permanent_payload:
    st.write("### 📎 Attached Items:")
    for f in st.session_state.permanent_payload:
        st.markdown(f"<span class='file-badge'>📄 {f.name}</span>", unsafe_allow_html=True)

st.markdown("---")

# --- STEP 2: RESULTS & EDITOR ---
if st.session_state.last_response:
    st.subheader("✨ Latest AI Insight")
    st.info(st.session_state.last_response)

st.subheader("📝 Live Report Editor")
st.session_state.document_content = st.text_area("Final Compiled Document:", value=st.session_state.document_content, height=300)

# --- ACTION BUTTONS ---
col_down, col_clear, _ = st.columns([0.2, 0.2, 0.6])
with col_down:
    if st.session_state.document_content:
        st.download_button("📥 Download .txt", st.session_state.document_content, file_name="ai_report.txt")

with col_clear:
    if st.button("🗑️ Reset Workspace"):
        st.session_state.document_content = ""
        st.session_state.last_response = ""
        st.session_state.permanent_payload = []
        st.rerun()

st.markdown("---")

# --- STEP 3: ANALYSIS LOGIC ---
if prompt := st.chat_input("Ask about your files..."):
    with st.spinner("🤖 Analyzing with Gemini 2.5 Flash..."):
        try:
            gemini_parts = []
            if st.session_state.permanent_payload:
                for f in st.session_state.permanent_payload:
                    m_type = getattr(f, 'type', 'application/octet-stream')
                    gemini_parts.append(types.Part.from_bytes(data=f.getvalue(), mime_type=m_type))
            
            gemini_parts.append(prompt)
            
            # --- UPDATED MODEL ID FOR 2026 STABILITY ---
            response = client.models.generate_content(
                model="gemini-2.5-flash", 
                contents=gemini_parts
            )
            
            st.session_state.last_response = response.text
            st.session_state.document_content += f"\n\n--- Analysis Result ---\n{response.text}"
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error: {e}")

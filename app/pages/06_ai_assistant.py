"""
app/pages/06_ai_assistant.py
Professional AI Assistant page powered by Gemini.
Styled with premium dark glassmorphism and clean typography.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
from app.components.theme import inject_theme, page_header, sidebar_brand
from modules.llm_integration import GeminiIntegration

st.set_page_config(page_title="AI Assistant | SkillSync", page_icon="💬", layout="wide")
inject_theme()

page_header("AI Career Assistant", "Ask our AI assistant any questions about your career, skills, or learning path.", icon="💬")

# Initialize Gemini
@st.cache_resource
def get_gemini_client():
    return GeminiIntegration()

gemini = get_gemini_client()

# Session state for chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Layout: sidebar brand and info, chat main area
with st.sidebar:
    st.markdown("---")
    st.markdown("""
    <div class="glass-card" style="padding:16px;margin-bottom:16px;">
      <h3 style="color:#FAFAFA;font-size:0.95rem;font-weight:600;margin:0 0 12px 0;">⚡ AI Capabilities</h3>
      <p style="color:rgba(255,255,255,0.7);font-size:0.8rem;margin:6px 0;"><span style="color:#6C63FF;font-weight:bold;">•</span> Career Guidance</p>
      <p style="color:rgba(255,255,255,0.7);font-size:0.8rem;margin:6px 0;"><span style="color:#6C63FF;font-weight:bold;">•</span> Resume Enhancement</p>
      <p style="color:rgba(255,255,255,0.7);font-size:0.8rem;margin:6px 0;"><span style="color:#6C63FF;font-weight:bold;">•</span> Mock Interview prep</p>
      <p style="color:rgba(255,255,255,0.7);font-size:0.8rem;margin:6px 0;"><span style="color:#6C63FF;font-weight:bold;">•</span> Skill Gap Advice</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("How can I help you with your career today?"):
    # User message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = gemini.answer_question(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Error: {e}")

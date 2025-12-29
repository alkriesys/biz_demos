import streamlit as st
from google import genai
from google.genai import types
import os
import json
import pandas as pd
from pypdf import PdfReader

# --- CONFIG & SETUP ---
st.set_page_config(page_title="Enterprise AI Suite", layout="wide")

# Hybrid Secret Loading (Cloud + Local)
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
else:
    api_key = os.environ.get("GOOGLE_API_KEY")

if not api_key:
    st.error("🚨 API Key missing.")
    st.stop()

client = genai.Client(api_key=api_key)

# --- DEMO 1: THE LEGAL RISK ANALYST ---
def render_legal_demo():
    st.header("⚖️ AI Contract Auditor")
    with st.expander("💡 About this Demo:"):
        st.markdown("""
        This tool demonstrates **Agentic AI** for legal process automation.
        It doesn't just summarize; it acts as a **Legal Analyst**, extracting critical risks from contract clauses and suggesting fairer rewrites, all in a structured format.
        
        **Role:** Architected the prompt engineering and JSON schema to ensure accurate risk detection and specific clause redlining, transforming unstructured legal text into actionable data for legal teams.
        """)
    
    st.markdown("Paste a legal clause. The AI will extract risks and **rewrite every single one**.")

    default_contract = """
    The Provider shall not be liable for any direct, indirect, or consequential damages. 
    The Client agrees to indemnify the Provider against all claims. 
    This agreement may be terminated by the Provider at any time without notice.
    Payment terms are Net 90 days.
    """
    
    contract_text = st.text_area("Contract Text", value=default_contract, height=150)

    if st.button("Analyze Risk"):
        with st.spinner("Reviewing with Legal Team..."):
            # UPGRADED PROMPT: We ask for a list of 'fixes' objects
            prompt = """
            You are a Senior Corporate Counsel. Review this contract text.
            Output a JSON object with this exact schema:
            {
                "risk_score": (integer 1-100),
                "risk_level": (string "Low", "Medium", "High", "Critical"),
                "analysis": [
                    {
                        "flag": "string (Describe the specific risk)", 
                        "rewrite": "string (Draft a fairer version of this specific clause)"
                    }
                ]
            }
            """
            
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=contract_text + "\n\n" + prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            
            try:
                data = json.loads(response.text)
                
                # VISUALIZATION
                c1, c2 = st.columns(2)
                with c1:
                    st.metric("Risk Score", f"{data['risk_score']}/100")
                with c2:
                    color = "red" if data['risk_score'] > 50 else "green"
                    st.markdown(f"### Level: :{color}[{data['risk_level']}]")
                
                st.divider()
                st.subheader("🚩 Redlines & Rewrites")
                
                # Loop through the list of fixes
                for item in data['analysis']:
                    with st.expander(f"⚠️ Issue: {item['flag']}", expanded=True):
                        st.markdown("**Suggested Rewrite:**")
                        st.code(item['rewrite'], language="text")
                    
            except Exception as e:
                st.error(f"Analysis failed: {e}")

# --- DEMO 2: THE COMPETITIVE BATTLECARD ---
def render_strategy_demo():
    st.header("⚔️ Competitive Battlecard Generator")
    with st.expander("💡 About this Demo:"):
        st.markdown("""
        This Agent demonstrates **Dynamic Market Intelligence**.
        It acts like a **VP of Sales Strategy**, synthesizing competitive analysis into concise "battlecards" for sales teams. This moves beyond simple data retrieval to generating actionable, context-aware sales tactics.
        
        **Role:** Designed the AI's persona and JSON output schema to ensure immediate utility for sales teams, enabling rapid response to competitor dynamics.
        """)
    
    st.markdown("Select a competitor to generate a sales strategy cheat-sheet.")
    
    competitor = st.selectbox("Select Competitor", ["Salesforce", "HubSpot", "Zendesk", "Custom..."])
    
    if competitor == "Custom...":
        competitor = st.text_input("Enter Competitor Name")

    if st.button("Generate Battlecard"):
        if not competitor:
            st.warning("Please enter a competitor name.")
            st.stop()
            
        with st.spinner(f"Researching {competitor}..."):
            prompt = f"""
            You are a VP of Sales. Create a 'Battlecard' to help our team sell against {competitor}.
            Assume we are selling a modern, AI-first CRM called 'AlkrieCRM'.
            
            Output a JSON object (NOT a list) with this exact schema:
            {{
                "their_weakness": "string",
                "our_strength": "string",
                "kill_points": ["point 1", "point 2", "point 3"],
                "pricing_comparison": "string"
            }}
            """
            
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                
                data = json.loads(response.text)
                
                # --- ROBUSTNESS FIX: Handle List vs Dict ---
                if isinstance(data, list):
                    data = data[0] # Grab the first item if it returned a list
                
                # DISPLAY AS A BATTLECARD
                st.markdown(f"### 🥊 Strategy: Beating {competitor}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.error(f"**Their Weakness:**\n\n{data.get('their_weakness', 'N/A')}")
                with col2:
                    st.success(f"**Alkrie Advantage:**\n\n{data.get('our_strength', 'N/A')}")
                
                st.markdown("---")
                st.markdown("#### 💬 Talking Points (Kill Points)")
                
                # Safe loop for kill points
                if "kill_points" in data and isinstance(data['kill_points'], list):
                    for kp in data['kill_points']:
                        st.markdown(f"- 🎯 {kp}")
                    
                st.info(f"**Pricing Angle:** {data.get('pricing_comparison', 'N/A')}")
            
            except Exception as e:
                st.error(f"Error generating battlecard: {e}")
                # Debugging aid: Show what the AI actually sent if it fails
                if 'response' in locals():
                    with st.expander("See raw AI output"):
                        st.text(response.text)

# --- DEMO 3: THE SMART RECRUITER (Resume Matcher) ---
def render_recruiter_demo():
    st.header("🕵️ Smart Resume Screener")
    
    with st.expander("💡 About this Demo:"):
        st.markdown("""
        This tool showcases **Top-of-Funnel HR Automation**.
        It acts as a **24/7 Junior Recruiter**, automatically scoring candidate resumes against job descriptions, identifying missing skills, and critically, checking for **Notice Periods**. If vital information is missing, it drafts immediate outreach messages.
        
        **Role:** Engineered the multi-step AI logic for resume parsing (RAG), JD comparison, and conditional message drafting (Agentic Tool Use), specifically targeting efficiency bottlenecks in high-volume recruitment markets like Bengaluru.
        """)
    
    st.markdown("Upload a Resume and paste the JD. The AI will score the candidate and check for **Notice Period**.")

    # Input 1: The Job Description
    default_jd = """
    We are looking for a Senior AI Engineer.
    Must have: Python, RAG experience, Vector Databases (Chroma/Pinecone).
    Good to have: Streamlit, FastAPI.
    Experience: 5+ years.
    Notice Period: Immediate to 30 days max.
    """
    jd_text = st.text_area("Job Description (JD)", value=default_jd, height=150)

    # Input 2: The Resume PDF
    uploaded_file = st.file_uploader("Candidate Resume (PDF)", type="pdf")

    if st.button("Screen Candidate"):
        if not uploaded_file:
            st.error("Please upload a resume first.")
            st.stop()
            
        with st.spinner("Analyzing profile against JD..."):
            # 1. Extract Text from PDF
            try:
                reader = PdfReader(uploaded_file)
                resume_text = ""
                for page in reader.pages:
                    resume_text += page.extract_text()
            except Exception as e:
                st.error("Could not read PDF. Ensure it is text-based.")
                st.stop()

            # 2. The Recruiter Prompt
            prompt = """
            You are a Senior Technical Recruiter. Compare the Candidate Resume against the Job Description.
            
            CRITICAL: Check for 'Notice Period'. If not mentioned, flag as "Unknown".
            
            Output JSON schema:
            {
                "match_score": (integer 0-100),
                "summary": "1 sentence verdict",
                "key_missing_skills": ["skill 1", "skill 2"],
                "notice_period_detected": "string",
                "recommendation": "string (Shortlist / Reject / Hold)",
                "outreach_draft": "string (Write a polite, professional WhatsApp message to the candidate. If Notice Period is unknown, ask for it. If skills are missing, ask about them. Keep it under 50 words.)"
            }
            """
            try:
                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=f"JOB DESCRIPTION:\n{jd_text}\n\nRESUME CONTENT:\n{resume_text}\n\n{prompt}",
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                
                data = json.loads(response.text)
                
                # VISUALIZATION
                
                # 1. Scorecard
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("Match Score", f"{data['match_score']}%")
                with c2:
                    # Color logic for Recommendation
                    color = "green" if data['recommendation'] == "Shortlist" else "red"
                    st.markdown(f"### Verdict: :{color}[{data['recommendation']}]")
                with c3:
                    # Notice Period Alert
                    np = data['notice_period_detected']
                    if "Unknown" in np or "Missing" in np:
                        st.warning("⚠️ Notice Period Missing")
                        st.markdown("**🚀 AI-Generated Outreach (WhatsApp):**")
                        st.text_area("Copy this message:", value=data['outreach_draft'], height=100)
                    else:
                        st.success(f"✅ Notice Period Found: {np}")
                        with st.expander("View Outreach Message"):
                            st.code(data['outreach_draft'], language="text")
                
                    st.info(f"**Summary:** {data['summary']}")
                
                # 2. Missing Skills
                if data['key_missing_skills']:
                    st.write("❌ **Missing / Weak Skills:**")
                    for skill in data['key_missing_skills']:
                        st.markdown(f"- {skill}")
                else:
                    st.balloons()
                    st.success("Perfect Skill Match!")
                    
            except Exception as e:
                st.error(f"AI Error: {e}")
                
# --- MAIN APP ROUTER ---
st.sidebar.title("🚀 C-Suite Demos")
demo_choice = st.sidebar.radio("Select Tool", ["Legal Risk Auditor", "Sales Battlecard Agent", "Smart Resume Screener"])

if demo_choice == "Legal Risk Auditor":
    render_legal_demo()
elif demo_choice == "Sales Battlecard Agent":
    render_strategy_demo()
elif demo_choice == "Smart Resume Screener":
    render_recruiter_demo()

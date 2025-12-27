import streamlit as st
from google import genai
from google.genai import types
import os
import json
import pandas as pd

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
# --- MAIN APP ROUTER ---
st.sidebar.title("🚀 C-Suite Demos")
demo_choice = st.sidebar.radio("Select Tool", ["Legal Risk Auditor", "Sales Battlecard Agent"])

if demo_choice == "Legal Risk Auditor":
    render_legal_demo()
elif demo_choice == "Sales Battlecard Agent":
    render_strategy_demo()

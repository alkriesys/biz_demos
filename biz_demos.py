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
    st.markdown("Paste a legal clause or contract snippet. The AI will extract risks.")

    default_contract = """
    The Provider shall not be liable for any direct, indirect, or consequential damages. 
    The Client agrees to indemnify the Provider against all claims. 
    This agreement may be terminated by the Provider at any time without notice.
    Payment terms are Net 90 days.
    """
    
    contract_text = st.text_area("Contract Text", value=default_contract, height=150)

    if st.button("Analyze Risk"):
        with st.spinner("Reviewing with Legal Team..."):
            prompt = """
            You are a Senior Corporate Counsel. Review this contract text.
            Output a JSON object with this exact schema:
            {
                "risk_score": (integer 1-100),
                "risk_level": (string "Low", "Medium", "High", "Critical"),
                "red_flags": [list of strings describing specific risks],
                "improved_clause": (string, rewrite the worst clause to be fair to the Client)
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
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.metric("Risk Score", f"{data['risk_score']}/100")
                with c2:
                    color = "red" if data['risk_score'] > 50 else "green"
                    st.markdown(f"### Level: :{color}[{data['risk_level']}]")
                
                st.subheader("🚩 Red Flags Identified")
                for flag in data['red_flags']:
                    st.warning(flag)
                    
                with st.expander("✨ View AI-Suggested Rewrite"):
                    st.info(data['improved_clause'])
                    
            except Exception as e:
                st.error(f"Analysis failed: {e}")

# --- DEMO 2: THE COMPETITIVE BATTLECARD ---
def render_strategy_demo():
    st.header("⚔️ Competitive Battlecard Generator")
    st.markdown("Select a competitor to generate a sales strategy cheat-sheet.")

    # Simulated Internal Knowledge Base
    competitor = st.selectbox("Select Competitor", ["Salesforce", "HubSpot", "Zendesk", "Custom..."])
    
    if competitor == "Custom...":
        competitor = st.text_input("Enter Competitor Name")

    if st.button("Generate Battlecard"):
        if not competitor:
            st.stop()
            
        with st.spinner(f"Researching {competitor}..."):
            # This prompt simulates an Agent synthesizing data
            prompt = f"""
            You are a VP of Sales. Create a 'Battlecard' to help our team sell against {competitor}.
            Assume we are selling a modern, AI-first CRM called 'AlkrieCRM'.
            
            Output JSON:
            {{
                "their_weakness": "string (one major flaw of competitor)",
                "our_strength": "string (why AlkrieCRM is better)",
                "kill_points": ["point 1", "point 2", "point 3"],
                "pricing_comparison": "string (e.g. They are expensive, we are value)"
            }}
            """
            
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            
            data = json.loads(response.text)
            
            # DISPLAY AS A BATTLECARD
            st.markdown(f"### 🥊 Strategy: Beating {competitor}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.error(f"**Their Weakness:**\n\n{data['their_weakness']}")
            with col2:
                st.success(f"**Alkrie Advantage:**\n\n{data['our_strength']}")
            
            st.markdown("---")
            st.markdown("#### 💬 Talking Points (Kill Points)")
            for kp in data['kill_points']:
                st.markdown(f"- 🎯 {kp}")
                
            st.info(f"**Pricing Angle:** {data['pricing_comparison']}")

# --- MAIN APP ROUTER ---
st.sidebar.title("🚀 C-Suite Demos")
demo_choice = st.sidebar.radio("Select Tool", ["Legal Risk Auditor", "Sales Battlecard Agent"])

if demo_choice == "Legal Risk Auditor":
    render_legal_demo()
elif demo_choice == "Sales Battlecard Agent":
    render_strategy_demo()

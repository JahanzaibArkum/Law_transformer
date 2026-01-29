import streamlit as st
import os
import re
from groq import Groq
from dotenv import load_dotenv

# 1. LOAD ENVIRONMENT VARIABLES
# This looks for the .env file and loads the variables
load_dotenv()

# --- APP CONFIGURATION ---
st.set_page_config(
    page_title="LexiMind | Legal Analysis Engine",
    page_icon="⚖️",
    layout="wide"
)

# --- SIDEBAR SETTINGS ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Check for API Key securely
    api_key = os.environ.get("GROQ_API_KEY")
    if api_key:
        st.success("✅ API Key Loaded from .env")
    else:
        st.error("❌ API Key Missing! Check .env file.")
    
    st.divider()
    
    # Legal Settings
    jurisdiction = st.selectbox(
        "Jurisdiction", 
        ["New York", "California", "Delaware", "Texas", "Federal (USA)", "United Kingdom", "EU Law"]
    )
    
    practice_area = st.selectbox(
        "Practice Area",
        ["Contract Law", "Intellectual Property", "Tort Law", "Criminal Defense", "Corporate Governance"]
    )
    
    temperature = st.slider(
        "Creativity (Temperature)",
        min_value=0.0, max_value=1.0, value=0.1, step=0.1,
        help="Lower values (0.1) provide strictly factual analysis. Higher values allow for creative legal arguments."
    )
    
    st.info("Powered by Groq Llama-3.3-70b")

# --- MAIN INTERFACE ---
st.title("⚖️ LexiMind: Legal Analysis AI")
st.markdown(f"""
**Role:** Senior Associate | **Jurisdiction:** {jurisdiction} | **Focus:** {practice_area}
""")

# Input Area
fact_pattern = st.text_area(
    "Case Details / Fact Pattern", 
    height=200, 
    placeholder="Paste the case details, contract clauses, or incident report here..."
)

# Analysis Logic
if st.button("Analyze Case", type="primary"):
    if not api_key:
        st.error("Cannot proceed. API Key is missing.")
        st.stop()
        
    if not fact_pattern:
        st.warning("⚠️ Please enter a fact pattern.")
        st.stop()

    # Initialize Client
    client = Groq(api_key=api_key)
    
    with st.spinner("Reviewing statutes and case law..."):
        try:
            # 1. CONSTRUCT THE PROMPT (Prompt Engineering)
            system_prompt = f"""
            You are a Senior Litigation Associate specializing in {practice_area} within {jurisdiction}.
            
            TASK:
            Analyze the user's fact pattern using the IRAC method (Issue, Rule, Analysis, Conclusion).
            
            CRITICAL INSTRUCTION:
            You must perform a "Chain of Thought" analysis BEFORE writing the final client memo.
            1. Enclose your internal legal reasoning inside <reasoning> tags.
            2. Inside the tags, be cynical. Look for loopholes, missing facts, and counter-arguments.
            3. After the tags, write the clean, professional Client Memo.
            
            FORMAT:
            <reasoning>
            [Internal monologue, checking precedents, and raw analysis]
            </reasoning>
            
            [Final Client Memo starts here]
            """

            # 2. CALL GROQ API
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"FACT PATTERN: {fact_pattern}"}
                ],
                temperature=temperature,
                max_tokens=4096,
                stop=None
            )
            
            full_response = completion.choices[0].message.content

            # 3. PARSE RESPONSE (Separate Reasoning from Memo)
            # This Regex extracts content between the tags vs outside the tags
            reasoning_match = re.search(r"<reasoning>(.*?)</reasoning>", full_response, re.DOTALL)
            
            if reasoning_match:
                internal_thought = reasoning_match.group(1).strip()
                # Remove the reasoning block to get the final clean memo
                final_memo = re.sub(r"<reasoning>.*?</reasoning>", "", full_response, flags=re.DOTALL).strip()
            else:
                internal_thought = "Model did not output hidden reasoning tags."
                final_memo = full_response

            # 4. DISPLAY RESULTS
            
            # The "Hidden Brain" - Expandable
            with st.expander("🧠 View Internal Legal Reasoning (Chain of Thought)", expanded=False):
                st.info("This section represents the AI's internal logic, identifying potential loopholes before forming a conclusion.")
                st.markdown(f"_{internal_thought}_")

            # The Final Output
            st.subheader("📝 Legal Memorandum")
            st.markdown(final_memo)
            
            st.success("Analysis Complete.")

        except Exception as e:
            st.error(f"An error occurred: {e}")
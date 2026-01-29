import streamlit as st
import os
import re
from groq import Groq
from dotenv import load_dotenv

# 1. LOAD ENVIRONMENT VARIABLES
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
    api_key = os.environ.get("GROQ_API_KEY")
    if api_key:
        st.success("✅ API Key Loaded from .env")
    else:
        st.error("❌ API Key Missing! Check .env file.")
    
    st.divider()
    
    jurisdiction = st.selectbox("Jurisdiction", ["New York", "California", "Delaware", "Texas", "Federal (USA)"])
    practice_area = st.selectbox("Practice Area", ["Contract Law", "Intellectual Property", "Tort Law", "Criminal Defense"])
    temperature = st.slider("Creativity (Temperature)", 0.0, 1.0, 0.1)
    
    st.info("Powered by NEXUSLABS")

# --- MAIN INTERFACE ---
st.title("⚖️ LexiMind: Legal Analysis AI")
st.markdown(f"**Attorney:** Jahanzaib | **Role:** Senior Litigation Associate | **Jurisdiction:** {jurisdiction}")

# Input Area
fact_pattern = st.text_area("Case Details / Fact Pattern", height=200, placeholder="Paste the legal scenario here...")

if st.button("Analyze Case", type="primary"):
    if not api_key or not fact_pattern:
        st.warning("⚠️ Please check API Key and Input.")
        st.stop()

    client = Groq(api_key=api_key)
    
    with st.spinner("Drafting Legal Memorandum..."):
        try:
            # --- FIXED PROMPT FOR SIGNATURE & CLIENT NAME ---
            system_prompt = f"""
            You are Jahanzaib, a Senior Litigation Associate specializing in {practice_area} within {jurisdiction}.
            
            TASK:
            Analyze the fact pattern using IRAC (Issue, Rule, Analysis, Conclusion).
            
            GUIDELINES:
            1. **Relevance Check:** If the input is NOT legal (e.g. "How to play cricket"), politely decline.
            2. **Reasoning:** Use <reasoning> tags for your internal logic first.
            3. **Client Name:** If the user does not provide a specific client name, address the memo to "Valued Client". Do not use placeholders like "[Client]".
            
            SIGNATURE FORMATTING (CRITICAL):
            You must format the signature block exactly as shown below. 
            **IMPORTANT:** Put each part of the signature on its own distinct line.
            
            Best regards,
            
            Jahanzaib  
            Senior Litigation Associate  
            {practice_area} Specialist  
            {jurisdiction}
            """

            # Call API
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"FACT PATTERN: {fact_pattern}"}
                ],
                temperature=temperature,
                max_tokens=4096
            )
            
            full_response = completion.choices[0].message.content

            # Parse Output
            reasoning_match = re.search(r"<reasoning>(.*?)</reasoning>", full_response, re.DOTALL)
            if reasoning_match:
                internal_thought = reasoning_match.group(1).strip()
                final_memo = re.sub(r"<reasoning>.*?</reasoning>", "", full_response, flags=re.DOTALL).strip()
            else:
                internal_thought = "Reasoning tags missing."
                final_memo = full_response

            # Display "Brain"
            with st.expander("🧠 View Jahanzaib's Internal Reasoning"):
                st.markdown(f"_{internal_thought}_")

            # Display Final Memo
            st.subheader("📝 Legal Memorandum")
            st.markdown(final_memo)
            
            st.success("Analysis Complete.")

        except Exception as e:
            st.error(f"Error: {e}")
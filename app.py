import os
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI   # <-- using only OpenAI client

# =========================
# ENVIRONMENT
# =========================
load_dotenv()
HF_API_KEY = os.getenv("HF_API_KEY", "")

# =========================
# SAFETY
# =========================
DISCLAIMER = (
    "⚠️ This is **not a diagnosis**. It provides general health guidance. "
    "Always consult a qualified doctor for treatment. In case of severe or urgent symptoms, "
    "seek emergency care immediately."
)
RED_FLAGS = [
    "Severe chest pain",
    "Sudden difficulty breathing",
    "Confusion or fainting",
    "Seizure",
    "Very high blood pressure (≥ 180/120 mmHg)",
    "High fever with stiff neck",
]

# =========================
# STREAMLIT CONFIG
# =========================
st.set_page_config(page_title="Virtual Doctor Assistant", page_icon="🩺", layout="wide")
st.title("🩺 Virtual Doctor Assistant")
st.caption(DISCLAIMER)

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #FFA500, #ffffff); }
    textarea, select, .stTextInput>div>div>input {
        background-color: #ADD8E6 !important;
        border: 2px solid #4facfe !important;
        border-radius: 10px !important;
        color: #003366 !important;
    }
    .stMultiSelect, .stCheckbox {
        background-color: #ADD8E6 !important;
        padding: 8px !important;
        border-radius: 10px !important;
        border: 1px solid #cce7ff !important;
    }
    div.stButton > button {
        background-color: #1E90FF;
        color: white;
        font-weight: bold;
        border-radius: 12px;
        padding: 10px 20px;
        border: none;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #00c6ff;
        color: black;
    }
    .response-box {
        background: #f0fff4;
        border-left: 5px solid #38a169;
        padding: 15px;
        border-radius: 10px;
        margin-top: 15px;
        color: #2f855a;
        font-size: 16px;
    }
    .red-flag {
        background: #fffaf0;
        border-left: 5px solid #dd6b20;
        padding: 8px;
        margin: 5px 0;
        border-radius: 8px;
        color: #7b341e;
    }
    </style>
""", unsafe_allow_html=True)

# =========================
# USER INPUT
# =========================
symptoms = st.text_area("✍️ Write your symptoms", placeholder="Example: headache, dizziness, shortness of breath")

prev_conditions = st.multiselect(
    "📋 Previous conditions (if any)",
    ["Hypertension", "Diabetes", "Asthma", "Heart Disease", "Kidney Disease"]
)

# =========================
# HUGGING FACE VIA OPENAI CLIENT
# =========================
def call_hf_chat(prompt: str, model: str = "meta-llama/Llama-3.1-8B-Instruct:cerebras") -> str:
    """Call Hugging Face model through OpenAI-compatible API."""
    if not HF_API_KEY:
        return "❌ Hugging Face API Key missing. Please set HF_API_KEY in your .env file."

    try:
        client = OpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=HF_API_KEY,
        )
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a medical assistant AI. Use doctor-verified sites. "
                        "Multiple doctors each give answers: include name + qualification. "
                        "Provide prescription guidance, safe drug suggestions, and recovery tips. "
                        "Always include reliable references. Minimum 10 doctors. "
                        "Each doctor’s headline must be bold."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=700,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"[HF Chat Error] {e}"

# =========================
# ACTION
# =========================
if st.button("Get Advice"):
    if not symptoms.strip():
        st.warning("⚠️ Please enter your symptoms.")
    else:
        user_prompt = f"""
        Patient Symptoms: {symptoms}.
        Check against known diseases and specialists.
        Provide safe guidance only.
        """
        ai_response = call_hf_chat(user_prompt)
        st.markdown("### 🧑‍⚕️ Virtual Doctor Assistant Suggestion")
        st.markdown(f'<div class="response-box">{ai_response}</div>', unsafe_allow_html=True)

        st.subheader("🚨 Emergency Red Flags")
        for rf in RED_FLAGS:
            st.markdown(f'<div class="red-flag">- {rf}</div>', unsafe_allow_html=True)

        st.caption("Generated on " + datetime.now().strftime("%Y-%m-%d %H:%M"))

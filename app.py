# app.py
import os
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv
from deep_translator import GoogleTranslator
from gtts import gTTS
import requests

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
# HUGGING FACE VIA DIRECT REQUEST
# =========================
def call_hf_chat(prompt: str, model: str = "meta-llama/Llama-3.1-8B-Instruct") -> str:
    """
    Call Hugging Face model using direct HTTP POST (safe for Render deployment).
    """
    if not HF_API_KEY:
        return "❌ Hugging Face API Key missing. Please set HF_API_KEY in your .env file."

    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {
        "inputs": (
            "You are a medical assistant AI. Multiple doctors each give answers "
            "with name and qualification. Each doctor suggestion in separate box. "
            "Prescribe drugs and provide recovery guidance.\n\n"
            f"Patient query: {prompt}"
        ),
        "parameters": {
            "max_new_tokens": 700,
            "temperature": 0.3,
        }
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)

        if resp.status_code == 404:
            return (f"[HF Chat Error] 404 Not Found for model '{model}'. "
                    f"Check the model URL: https://huggingface.co/{model}")

        if resp.status_code != 200:
            return f"[HF Chat Error] {resp.status_code} - {resp.text}"

        result = resp.json()

        # Many text-generation endpoints return list of dicts with 'generated_text'
        if isinstance(result, list) and result and "generated_text" in result[0]:
            return result[0]["generated_text"].strip()

        if isinstance(result, dict) and "error" in result:
            return f"[HF Chat Error] {result['error']}"

        return str(result)

    except requests.exceptions.RequestException as e:
        return f"[HF Chat Error] Request failed: {e}"

# =========================
# AI-DRIVEN RELATED SYMPTOMS
# =========================
def get_ai_related_symptoms(symptoms, prev_conditions):
    if not symptoms.strip():
        return []
    prompt = f""" 
    The patient problem: {symptoms}. Previous conditions: {', '.join(prev_conditions) if prev_conditions else 'None'}.
    Based on the patient problem and previous conditions, suggest 5 related possible symptoms/questions the patient may consider. 
    Only related symptoms, no headlines needed. They are independent of advice output.
    """
    response = call_hf_chat(prompt)
    suggestions = [s.strip() for s in response.replace("\n", ",").split(",") if s.strip()]
    return suggestions[:5]

# =========================
# TRANSLATION UTILITIES
# =========================
def translate_text(text, target_lang):
    if not text.strip():
        return ""
    try:
        return GoogleTranslator(source="auto", target=target_lang).translate(text)
    except Exception as e:
        st.error(f"[Translation Error] {e}")
        return text

# =========================
# ADVICE FUNCTIONS
# =========================
def generate_advice(symptoms_input, prev_conditions, selected_lang):
    languages = {
        "English": "en","Hindi": "hi","Marathi": "mr","Tamil": "ta","Telugu": "te",
        "Kannada": "kn","Gujarati": "gu","Punjabi": "pa","Bengali": "bn",
        "Malayalam": "ml","Urdu": "ur"
    }
    user_prompt = f"""
    Patient Symptoms: {symptoms_input}.
    Previous Conditions: {', '.join(prev_conditions) if prev_conditions else 'None'}.
    Provide safe guidance only with correct grammar.
    """
    ai_response = call_hf_chat(user_prompt)
    translated_text = translate_text(ai_response, languages[selected_lang])
    st.session_state["advice_text"] = translated_text

def generate_audio(selected_lang):
    languages = {
        "English": "en","Hindi": "hi","Marathi": "mr","Tamil": "ta","Telugu": "te",
        "Kannada": "kn","Gujarati": "gu","Punjabi": "pa","Bengali": "bn",
        "Malayalam": "ml","Urdu": "ur"
    }
    if "advice_text" not in st.session_state:
        return
    try:
        tts = gTTS(st.session_state["advice_text"], lang=languages[selected_lang])
        audio_file = "output.mp3"
        tts.save(audio_file)
        st.session_state["advice_audio_file"] = audio_file
    except Exception as e:
        st.error(f"Audio generation failed: {e}")

# =========================
# STREAMLIT UI
# =========================
st.set_page_config(page_title="Virtual Doctor Assistant", page_icon="🩺", layout="wide")
st.markdown(
    """
    <style>
    textarea, .stMultiSelect, .stSelectbox { background-color: #f0f9ff !important; border: 2px solid #0284c7 !important; border-radius: 10px !important; padding: 8px !important; }
    .stButton>button { background-color: #0284c7; color: white; border-radius: 8px; padding: 10px 20px; border: none; font-weight: bold; }
    .stButton>button:hover { background-color: #0369a1; color: white; }
    .suggestion-box { background-color: #e0f7fa; border: 2px solid #0284c7; border-radius: 8px; padding: 10px; max-height: 500px; overflow-y: auto; display: flex; flex-wrap: wrap; gap: 8px; }
    .suggestion-item { background-color: #ffffff; padding: 6px 10px; border-radius: 20px; border: 1px solid #0284c7; font-size: 14px; flex: 0 0 auto; }
    .suggestion-item:hover { background-color: #b2ebf2; cursor: pointer; }
    .doctor-box { background-color:#f0fff4; border-left:5px solid #38a169; padding:12px; margin:10px 0; border-radius:10px; }
    .doctor-header { background-color:#38a169; color:white; padding:6px 12px; border-radius:8px; font-weight:bold; margin-bottom:8px; }
    </style>
    """, unsafe_allow_html=True
)
st.title("🩺 Virtual Doctor Assistant")
st.caption(DISCLAIMER)

# Initialize session states
if "symptoms_list" not in st.session_state:
    st.session_state["symptoms_list"] = []

# =========================
# LAYOUT
# =========================
main_col, suggestion_col = st.columns([1.5, 1.5])

# LEFT COLUMN
with main_col:
    languages = {
        "English": "en","Hindi": "hi","Marathi": "mr","Tamil": "ta","Telugu": "te",
        "Kannada": "kn","Gujarati": "gu","Punjabi": "pa","Bengali": "bn",
        "Malayalam": "ml","Urdu": "ur"
    }
    selected_lang = st.selectbox("🌐 Select output language", list(languages.keys()))

    # USER INPUT SYMPTOMS
    user_input = st.text_area(
        "✍️ Enter your symptoms",
        value=" with ".join(st.session_state["symptoms_list"]),
        height=150,
        placeholder="Example: headache, dizziness"
    )
    if user_input:
        st.session_state["symptoms_list"] = [s.strip() for s in user_input.split(" with ") if s.strip()]

    prev_conditions = st.multiselect(
        "📋 Previous conditions (if any)",
        ["Hypertension", "Diabetes", "Asthma", "Heart Disease", "Kidney Disease"]
    )

    # Buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Get Advice (Text)"):
            if not st.session_state["symptoms_list"]:
                st.warning("⚠️ Please enter your symptoms.")
            else:
                generate_advice(" with ".join(st.session_state["symptoms_list"]), prev_conditions, selected_lang)
    with col2:
        if st.button("🔊 Get Advice (Audio)"):
            if not st.session_state["symptoms_list"]:
                st.warning("⚠️ Please enter your symptoms.")
            else:
                generate_advice(" with ".join(st.session_state["symptoms_list"]), prev_conditions, selected_lang)
                generate_audio(selected_lang)

# RIGHT COLUMN: AI suggestions
with suggestion_col:
    st.markdown("### 💡 Related Symptoms (AI Suggestions)")
    suggestions = get_ai_related_symptoms(" with ".join(st.session_state["symptoms_list"]), prev_conditions)
    if suggestions:
        st.markdown('<div class="suggestion-box">', unsafe_allow_html=True)
        for s in suggestions:
            if not s.endswith("?"):
                s = s + "?"
            key = f"suggestion_{s}"
            if st.button(s, key=key):
                clean = s.replace("You have", "I have").replace("Have you", "I had").replace("Are you", "I feel").rstrip("?")
                if clean not in st.session_state["symptoms_list"]:
                    st.session_state["symptoms_list"].append(clean)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("AI will suggest related symptoms/questions as you type.")

# DISPLAY ADVICE & RED FLAGS
if "advice_text" in st.session_state or "advice_audio_file" in st.session_state:
    left, right = st.columns(2)
    with left:
        if "advice_text" in st.session_state:
            st.markdown("### 🧑‍⚕️ Virtual Doctor Assistant Suggestion")
            # Split advice per doctor if line breaks exist
            doctors = st.session_state["advice_text"].split("\n\n")
            for doc in doctors:
                if doc.strip():
                    st.markdown(
                        f'<div class="doctor-box"><div class="doctor-header">Doctor</div>{doc}</div>',
                        unsafe_allow_html=True
                    )
            st.subheader("🚨 Emergency Red Flags")
            for rf in RED_FLAGS:
                st.markdown(f'<div style="background:#fffaf0;border-left:5px solid #dd6b20;padding:8px;margin:5px 0;border-radius:8px;">- {rf}</div>', unsafe_allow_html=True)
            st.caption("Generated on " + datetime.now().strftime("%Y-%m-%d %H:%M"))
    with right:
        if "advice_audio_file" in st.session_state:
            st.markdown("### 🔊 Audio Advice")
            st.audio(st.session_state["advice_audio_file"], format="audio/mp3")
            st.subheader("🚨 Emergency Red Flags")
            for rf in RED_FLAGS:
                st.markdown(f'<div style="background:#fffaf0;border-left:5px solid #dd6b20;padding:8px;margin:5px 0;border-radius:8px;">- {rf}</div>', unsafe_allow_html=True)
            st.caption("Generated on " + datetime.now().strftime("%Y-%m-%d %H:%M"))


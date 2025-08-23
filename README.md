# doctor-assistant
virtual-doctor-assistant/
│
├── app.py
├── requirements.txt
└── README.md
# 🩺 Virtual Doctor Assistant

An AI-powered **Virtual Doctor Assistant** built with **Streamlit**, **Hugging Face Inference API**, and **Google Translator + gTTS**.  
This app allows users to:
- Enter symptoms and past medical conditions.
- Receive **doctor-style suggestions** in multiple languages.
- Get both **text advice** and **audio playback**.
- See **related AI symptom suggestions**.
- Be alerted with **emergency red flag warnings**.

---

## 🚀 Features
- Multi-language support (English, Hindi, Marathi, Tamil, Telugu, Kannada, Gujarati, Punjabi, Bengali, Malayalam, Urdu).
- Multiple **doctors’ advice** shown in **separate styled boxes** with doctor names in headers.
- AI-generated **related symptom suggestions**.
- **Text and Audio output** (via gTTS).
- Emergency **Red Flag warnings**.

---

## 📦 Installation

1. **Clone repo**
   ```bash
   git clone https://github.com/your-repo/virtual-doctor-assistant.git
   cd virtual-doctor-assistant
2. Create virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Linux/Mac
   venv\Scripts\activate      # On Windows


3. Install dependencies
   ```bash
   pip install -r requirements.txt

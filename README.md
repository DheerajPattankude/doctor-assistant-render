# Virtual Doctor Assistant

A Streamlit-based virtual doctor assistant that provides AI-generated medical guidance, multi-language support, audio output, and doctor-wise advice boxes.

## Features
- Enter symptoms and previous conditions
- AI generates advice from multiple doctors in separate colored boxes
- Related symptom suggestions
- Multi-language support
- Audio playback using gTTS
- Emergency red flags highlighted

## Setup

1. Clone the repository
2. Create `.env` file with:


## Deployment on Render
- Make sure `.env` variables are set in Render dashboard
- Set start command: `streamlit run app.py`
- The app will be live with AI doctor advice functionality
- pip install runtime.txt
## Post-Build Command
``bash
  pip install --upgrade pip setuptools wheel
  

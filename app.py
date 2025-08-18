import os
import requests

HF_TOKEN = os.environ["HF_TOKEN"]
MODEL_ID = "espnet/kan-bayashi_ljspeech_vits"

API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

data = {
    "inputs": "The answer to the universe is 42"
}

# Send request
response = requests.post(API_URL, headers=headers, json=data)

# Save audio if response is ok
if response.status_code == 200:
    with open("output.wav", "wb") as f:
        f.write(response.content)
    print("✅ Audio saved to output.wav")
else:
    print("❌ Error:", response.status_code, response.text)


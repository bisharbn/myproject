import requests
import uuid
import os
import xml.etree.ElementTree as ET


AZURE_TTS_KEY = '9puxjTqOVfvLt5nys1wx5Qr7LT9nHv3ObzLNNoWNMfPuyCDM9TyzJQQJ99BFACYeBjFXJ3w3AAAYACOGkhCL'
AZURE_REGION = "eastus"  # Replace with your region
AZURE_ENDPOINT = f"https://{AZURE_REGION}.tts.speech.microsoft.com/cognitiveservices/v1"

text = "Hello Bishar, your Azure TTS is working perfectly."

filename = f"{uuid.uuid4().hex}.mp3"
output_path = os.path.join("media/audio", filename)
os.makedirs("media/audio", exist_ok=True)

# Build basic SSML
speak = ET.Element('speak', version='1.0', xmlns='http://www.w3.org/2001/10/synthesis', attrib={'xml:lang': 'en-US'})
voice_elem = ET.SubElement(speak, 'voice', name='en-US-JennyNeural')
voice_elem.text = text
ssml = ET.tostring(speak, encoding='utf-8')

headers = {
    "Ocp-Apim-Subscription-Key": AZURE_TTS_KEY,
    "Content-Type": "application/ssml+xml",
    "X-Microsoft-OutputFormat": "audio-16khz-32kbitrate-mono-mp3",
    "User-Agent": "AzureTTS-Demo"
}

response = requests.post(AZURE_ENDPOINT, headers=headers, data=ssml)

print("[DEBUG] Status Code:", response.status_code)

if response.status_code == 200:
    with open(output_path, "wb") as f:
        f.write(response.content)
    print("✅ Audio saved:", output_path)
else:
    print("❌ Failed:", response.text)

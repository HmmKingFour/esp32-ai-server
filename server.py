from fastapi import FastAPI, UploadFile, File
import requests

app = FastAPI()

# 🔑 PUT YOUR KEYS HERE
GROQ_API_KEY = "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"
ELEVEN_API_KEY = "sk_2c01aca403df72117f90197760a29beaf9203ea50e99b3c1"
VOICE_ID = "UgBBYS2sOqTuMpoF3BR0"

@app.get("/")
def home():
    return {"status": "server running"}

@app.post("/voice")
async def voice(file: UploadFile = File(...)):
    audio_data = await file.read()

    # ---- 1. Speech-to-Text (Groq Whisper) ----
    stt_res = requests.post(
        "https://api.groq.com/openai/v1/audio/transcriptions",
        headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
        files={"file": ("audio.wav", audio_data)},
        data={"model": "whisper-large-v3"}
    )
    text = stt_res.json()["text"]

    print("User said:", text)

    # ---- 2. LLM (Groq) ----
    chat_res = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama3-70b-8192",
            "messages": [{"role": "user", "content": text}]
        }
    )
    reply = chat_res.json()["choices"][0]["message"]["content"]

    print("AI reply:", reply)

    # ---- 3. TTS (ElevenLabs) ----
    tts_res = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
        headers={
            "xi-api-key": ELEVEN_API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "text": reply,
            "model_id": "eleven_multilingual_v2"
        }
    )

    return tts_res.content

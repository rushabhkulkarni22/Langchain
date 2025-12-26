import os
import uuid
import json
import pandas as pd
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from openai import OpenAI
from dotenv import load_dotenv
from threading import Lock

# ==============================
# LOAD .env FILE
# ==============================
load_dotenv()

# ==============================
# OPENAI CLIENT
# ==============================
client = OpenAI()

UPLOAD_DIR = "temp_files"
CACHE_FILE = "translation_cache.json"

os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="Excel Translation API with Cache")

# ==============================
# CACHE SETUP
# ==============================

cache_lock = Lock()

if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        translation_cache = json.load(f)
else:
    translation_cache = {}

def save_cache():
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(translation_cache, f, ensure_ascii=False, indent=2)

# ==============================
# TRANSLATION FUNCTION (WITH CACHE)
# ==============================

def translate_text(text: str, target_language: str) -> str:
    cache_key = f"{text.strip()}||{target_language.strip()}"

    # 🔍 Check cache first
    with cache_lock:
        if cache_key in translation_cache:
            return translation_cache[cache_key]

    # ❌ Not in cache → Call LLM
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a professional translation assistant."
            },
            {
                "role": "user",
                "content": (
                    f"Translate the following English sentence into {target_language}. "
                    f"Return only the translated sentence.\n\n{text}"
                )
            }
        ],
        temperature=0
    )

    translated_text = response.choices[0].message.content.strip()

    # 💾 Save to cache
    with cache_lock:
        translation_cache[cache_key] = translated_text
        save_cache()

    return translated_text

# ==============================
# API ENDPOINT
# ==============================

@app.post("/translate-excel")
async def translate_excel(file: UploadFile = File(...)):
    input_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
    output_path = os.path.join(UPLOAD_DIR, f"translated_{file.filename}")

    with open(input_path, "wb") as f:
        f.write(await file.read())

    df = pd.read_excel(input_path, header=None)

    languages = df.iloc[0, 1:].tolist()

    for row in range(1, len(df)):
        english_text = df.iloc[row, 0]

        if pd.isna(english_text):
            continue

        for col, language in enumerate(languages, start=1):
            if pd.isna(language):
                continue

            df.iloc[row, col] = translate_text(
                text=str(english_text),
                target_language=str(language)
            )

    df.to_excel(output_path, index=False, header=False)

    return FileResponse(
        path=output_path,
        filename="translated_output.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ==============================
# HEALTH CHECK
# ==============================

@app.get("/")
def health_check():
    return {"status": "Excel Translation API with cache is running"}

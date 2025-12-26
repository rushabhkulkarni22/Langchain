import os
import uuid
import pandas as pd
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from openai import OpenAI
from dotenv import load_dotenv

# ==============================
# LOAD .env FILE
# ==============================
load_dotenv()

# ==============================
# OPENAI CLIENT
# ==============================
client = OpenAI()  # Reads OPENAI_API_KEY from .env automatically

UPLOAD_DIR = "temp_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="Excel Translation API")

# ==============================
# TRANSLATION FUNCTION
# ==============================

def translate_text(text: str, target_language: str) -> str:
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

    return response.choices[0].message.content.strip()

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

@app.get("/")
def health_check():
    return {"status": "Excel Translation API is running"}

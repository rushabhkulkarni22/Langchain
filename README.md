Excel Translation API (FastAPI + OpenAI + Docker)

This project provides a FastAPI-based REST API that accepts an Excel file, translates English sentences into multiple languages using an OpenAI LLM, and returns the translated Excel file. The application also uses a JSON-based cache to avoid repeated LLM calls for the same translation.

Features

1. Upload Excel (.xlsx) file

2. Column A contains English sentences (starting from row 2)

3. Row 1 (B1, C1, D1, etc.) contains target languages

4. Translates text using OpenAI LLM

5. JSON cache to reduce API calls

6. Dockerized application

7. Persistent storage using Docker volumes

8. Excel File Format

Column A: English sentences
Row 1 (B, C, D...): Target languages

Example:

English | Hindi | French | German
English | Hindi | French | German
How are you | | |
Good morning | | |

Project Structure

.
main_cache.py
Dockerfile
requirements.txt
.env
.gitignore
temp_files
README.md

Environment Variables

Create a .env file in the root directory:

OPENAI_API_KEY=your_openai_api_key_here

Do not commit the .env file to GitHub.

Run Locally (Without Docker)

Create virtual environment

python -m venv venv
source venv/bin/activate
Windows: venv\Scripts\activate

Install dependencies

pip install -r requirements.txt

Start the server

uvicorn main_cache:app --reload

Open API documentation

http://127.0.0.1:8000/docs

Run Using Docker

Build Docker image

docker build -t excel-translation-api .

Run Docker container with volume mapping

docker run -p 8000:8000 --env-file .env -v $(pwd)/docker_data:/app/temp_files excel-translation-api

Access API

http://localhost:8000

http://localhost:8000/docs

API Endpoint

POST /translate-excel

Request:

multipart/form-data

key: file

value: Excel file (.xlsx)

Response:

Translated Excel file download

Cache Behavior

Translations are stored in a JSON cache file

Cache is checked before calling OpenAI

If translation exists, it is reused

If not, OpenAI API is called and result is cached

Git Ignore Recommendations

.env
temp_files/
docker_data/
pycache/
*.json
venv/

Tech Stack

Python
FastAPI
OpenAI API
Pandas
Docker
Uvicorn

Future Enhancements

Redis cache

Batch translation

Authentication

Rate limiting

Cloud deployment

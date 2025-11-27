## 1. TO RUN THE BACKEND FROM ROOT FOLDER
```uv run uvicorn app.main:app --reload --app-dir src```

## 2. TOML FILE WILL BE DELETED AND EVERYTHING WILL BE MOVED TO REQUIREMENTS.txt and docker file will be updated but only in production

## 3. Another copy of this project will be made and that one will be used for production 

## 4. This is the command for setting the uv environment
0. ```pip install uv```

1. ```uv init .```

2. ```uv add fastapi "uvicorn[standard]" gunicorn python-multipart email-validator pydantic-settings python-dotenv motor dnspython opencv-python-headless pytesseract ultralytics numpy Pillow pyahocorasick requests pdfminer.six litellm httpx aiofiles```

3. ```select the interpreter and copy the path of venv and paste it```

4. ```check if imports are working```

5. ```all set```

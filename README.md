# Expense Management API

A FastAPI application for recording and filtering expenses.

## Setup

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run the application

```powershell
python -m uvicorn main:app --reload
```

Open the interactive API documentation at http://127.0.0.1:8000/docs.

The app uses SQLite and creates `expenses.db` automatically.
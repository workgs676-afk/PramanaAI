# Pramana.ai

An automated document intelligence platform that uses a React frontend and a
FastAPI backend to extract tender rules, evaluate unstructured bids, and keep
procurement checks auditable.

## Project Structure

- `src/` contains the React frontend.
- `Backend/` contains the FastAPI API and rule-evaluation logic.
- `Pipeline/` contains OCR and document-processing experiments.

## Frontend

Install dependencies and start the UI:

```bash
npm install
npm start
```

The app runs on `http://localhost:3000`.

## Backend

Install Python dependencies and run the API:

```bash
pip install -r requirements.txt
uvicorn Backend.main:app --reload
```

The backend runs on `http://127.0.0.1:8000`.

## Current Demo Flow

1. Upload a document from the React UI.
2. The frontend sends it to `POST /evaluate-bid`.
3. The backend checks for GST, PAN, and ISO evidence.
4. The UI displays a `PASS` or `FAIL` status, score, and summary.

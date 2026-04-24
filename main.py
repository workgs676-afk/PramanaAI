from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "backend working"}

@app.post("/evaluate-bid")
async def evaluate_bid(file: UploadFile = File(...)):

    content = await file.read()
    text = content.decode(errors="ignore").lower()

    # ---------------- RULE ENGINE ----------------
    score = 100
    issues = []

    if "gst" not in text:
        score -= 30
        issues.append("Missing GST")

    if "pan" not in text:
        score -= 20
        issues.append("Missing PAN")

    if "iso" not in text:
        score -= 10
        issues.append("Missing ISO certification")

    status = "PASS" if score >= 70 else "FAIL"

    return {
        "status": status,
        "score": score,
        "summary": " | ".join(issues) if issues else "All checks passed"
    }
from fastapi import FastAPI

# Create the app instance
app = FastAPI()

# This function runs when you visit the root URL ("/")
@app.get("/")
def read_root():
    return {"message": " The API is working."}

# This function runs when you visit "/health" (useful for monitoring)
@app.get("/health")
def health_check():
    return {"status": "ok"}

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI(title="KTU Result Processor API")


FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")


app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
async def serve_homepage():
    """
    Serve the main HTML page when user visits the root URL.
    This is the entry point of our web application.
    """
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    return FileResponse(index_path)

@app.get("/health")
async def health_check():
    """
    Simple health check endpoint to verify backend is running.
    Returns JSON with status message.
    """
    return {"status": "ok", "message": "Backend is running"}

# This block runs only when you execute this file directly
# Not when it's imported as a module
if __name__ == "__main__":
    import uvicorn
    # Run the server on localhost:8000
    # reload=True automatically restarts server when code changes
    print('localhost:8000')
    uvicorn.run("main:app", port=8000, reload=True)
    
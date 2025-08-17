from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create ultra-minimal FastAPI app
app = FastAPI(title="LeadNest API", version="1.0.0")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "status": "healthy",
        "service": "leadnest-api", 
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/auth/test")
async def test():
    return {"message": "Working!"}

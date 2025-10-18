from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from backend.simulation import run_repairman_simulation

app = FastAPI(title="Repairman Problem Simulation")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend files from the frontend directory
app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.get("/")
async def read_index():
    return FileResponse('frontend/index.html')


@app.post("/simulate")
async def simulate(request: Request):
    try:
        data = await request.json()
        M = int(data.get("M", 10))
        N = int(data.get("N", 6))
        mean_repair = float(data.get("mean_repair", 100))
        std_repair = float(data.get("std_repair", 50))
        mean_break = float(data.get("mean_break", 300))
        std_break = float(data.get("std_break", 80))
        num_simulations = int(data.get("num_simulations", 5))

        # Validate inputs
        if N >= M:
            return {"error": "N must be less than M"}
        if any(x <= 0 for x in [mean_repair, mean_break, num_simulations]):
            return {"error": "All means and number of runs must be positive"}

        result = run_repairman_simulation(M, N, mean_repair, std_repair, mean_break, std_break, num_simulations)
        return result

    except Exception as e:
        return {"error": f"Simulation error: {str(e)}"}
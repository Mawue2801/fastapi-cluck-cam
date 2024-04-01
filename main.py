from fastapi import FastAPI, UploadFile, File, HTTPException, Path
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware
from typing import List
import shutil
import os
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Directory to store uploaded images
UPLOAD_DIRECTORY = "uploaded_images"

LOG_DIRECTORY = "logs"

# Create the upload directory if it doesn't exist
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

# Create the logs directory if it doesn't exist
os.makedirs(LOG_DIRECTORY, exist_ok=True)

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    """
    Endpoint to upload an image.
    """
    with open(os.path.join(UPLOAD_DIRECTORY, file.filename), "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename}

@app.get("/get/{filename}")
async def get_image(filename: str):
    """
    Endpoint to retrieve an image by filename.
    """
    return FileResponse(os.path.join(UPLOAD_DIRECTORY, filename))

@app.post("/log/{channel_id}/")
async def log_message(data: dict, channel_id: int = Path(..., title="The ID of the channel to log to")):
    """
    Endpoint to append a dictionary to a log file.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp}: {data}\n"

    LOG_FILE = os.path.join(LOG_DIRECTORY, f"logs_{channel_id}.txt")
    
    # Check if the log file exists, create it if it doesn't
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as new_log_file:
            pass  # Just create an empty file
    
    # Append the log entry to the log file
    with open(LOG_FILE, "a") as log_file:
        log_file.write(log_entry)
    
    return {"message": "Log entry added successfully."}

@app.get("/last_record/{channel_id}")
async def get_last_record(channel_id: int):
    """
    Endpoint to retrieve the last recorded data and its timestamp for a given channel_id.
    """
    LOG_FILE = os.path.join(LOG_DIRECTORY, f"logs_{channel_id}.txt")

    # Check if the log file exists
    if not os.path.exists(LOG_FILE):
        raise HTTPException(status_code=404, detail="Log file not found")

    # Read the log file and retrieve the last recorded data and timestamp
    last_record = None
    with open(LOG_FILE, "r") as log_file:
        lines = log_file.readlines()
        if lines:
            last_record = lines[-1].strip()  # Get the last line (last recorded data)
    
    if last_record:
        timestamp_str, data_str = last_record.split(": ", 1)
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        return {"timestamp": timestamp, "data": data_str}
    else:
        raise HTTPException(status_code=404, detail="No records found for the specified channel_id")
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi import Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from pydantic import BaseModel
from datetime import datetime
import uuid
import os
import json
import aiofiles

from database import ImageData, UserData, ImageDatabase

# Define the directory for storing images
IMAGE_DIR = "submitted_images"
# Define the central data file for metadata
DATABASE_FILE = "database.json"

# Define the Image database
database = ImageDatabase()

# Create the image directory if it doesn't exist
os.makedirs(IMAGE_DIR, exist_ok=True)

app = FastAPI()

####################################################
# --- Security Configuration ---

# In a real application, this would be retrieved from a secure configuration,
# environment variables, or a database. DO NOT HARDCODE IN PRODUCTION!
# For demonstration purposes, we'll use a simple static token.
VALID_ACCESS_TOKEN = "nutrinails2"

# Initialize HTTPBearer for token extraction from Authorization header
oauth2_scheme = HTTPBearer()

# --- Dependency for Access Token Validation ---

async def verify_access_token(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)):
    """
    Dependency function to validate the access token.
    It expects the token in the 'Authorization: Bearer <token>' header.
    """
    if credentials.scheme != "Bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme. Must be 'Bearer'."
        )
    if credentials.credentials != VALID_ACCESS_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            #headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials # Return the token if valid (optional, but good for context)


##### ENDPOINTS


@app.get("/info/")
async def info():
    """
    Gives info about the server
    """

    try:
        return {"message": f"Server is running", "version": "1.0"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send information: {e}")


@app.post("/create_item/", status_code=status.HTTP_201_CREATED)
async def create_item(
    item: ImageData, # Expects a JSON request body conforming to the Item model
    token: str = Depends(verify_access_token) # Secure this endpoint with the token
):
    """
    This endpoint allows creation of an item but only if a valid access token
    is provided in the Authorization: Bearer header.
    """
    print(f"Received item creation request with valid token: {token[:8]}...")
    # In a real application, you would save this item to a database here
    # For demonstration, we'll just return it with a confirmation message.
    return {"message": "Metadata submitted successfully", "metadata": item}

@app.post("/upload_image/")
async def upload_image(image: UploadFile = File(...)):
    """
    Receives an image, generates a unique name with the current date and a hash,
    and stores it in the 'submitted_images' directory.
    """

    try:
        current_date = datetime.now().strftime("%Y%m%d")
        hash_key = uuid.uuid4().hex
        file_extension = image.filename.split(".")[-1]
        new_image_name = f"{current_date}_{hash_key}.{file_extension}"
        file_path = os.path.join(IMAGE_DIR, new_image_name)

        async with aiofiles.open(file_path, "wb") as out_file:
            while content := await image.read(1024):  # Read in chunks
                await out_file.write(content)

        return {"message": f"Image '{new_image_name}' uploaded successfully", "image_name": new_image_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {e}")

@app.post("/submit_metadata/")
async def submit_metadata(metadata: ImageData, token: str = Depends(verify_access_token)):
    """
    Receives image metadata as JSON and adds it to the 'database.json' file.
    """
    try:
        # Load existing data
        database.load_data_from_file()
        await database.add_image_data(metadata)

        return {"message": "Metadata submitted successfully", "metadata": metadata}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit metadata: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
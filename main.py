
from fastapi import FastAPI, UploadFile, File, HTTPException
from PIL import Image
import os
from fastapi.responses import FileResponse
from pathlib import Path
import logging
from transformers import pipeline
import uuid
import shutil
import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()
caption_generator = pipeline("image-to-text", model="Salesforce/blip-image-captioning-base")

IMAGE_FOLDER = "image"
THUMBNAIL_FOLDER = "thumbnails"

os.makedirs(IMAGE_FOLDER, exist_ok=True)
os.makedirs(THUMBNAIL_FOLDER, exist_ok=True)

@app.get("/")
def home():
    return {"message": "Digital Forensics Image API"}

@app.post("/api/images")

def upload_image(file: UploadFile = File(...)):
    start_time = datetime.datetime.now()
    supported_format = {"image/jpg", "image/png"}
    if file.content_type not in supported_format:
        logger.warning(f"Invalid file type uploaded: {file.filename}")
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    image_id = str(uuid.uuid4()) #generates unique ID for image
    logger.info(f"Processing image: {file.filename} with ID: {image_id}")

    filepath = f"{IMAGE_FOLDER}/{image_id}_{file.filename}"
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    logger.info(f"Image saved to {filepath}")

    img = Image.open(filepath)
    caption_result = caption_generator(img)
    caption = caption_result[0]['generated_text']
    logger.info(f"Caption generated: {caption}")

    
    #extract metadata
    width, height = img.size
    file_format = img.format
    file_size = os.path.getsize(filepath)
    file_datetime = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    small = img.copy()
    small.thumbnail((100, 100))
    small.save(f"{THUMBNAIL_FOLDER}/{image_id}_small.jpg")
    medium = img.copy()
    medium.thumbnail((300, 300))
    medium.save(f"{THUMBNAIL_FOLDER}/{image_id}_medium.jpg")
        
    image_info = {
        "status": "success",
        "data":{
            "image_id": image_id,
            "original_name": file.filename,
            "processed_at" : file_datetime,
            "metadata":{
                "width": width,
                "height": height,
                "format": file_format,
                "size_bytes" : file_size
                },
            "thumbnails":{
                "small":f"http://localhost:8000/api/images/{image_id}/thumbnails/small",
                "medium":f"http://localhost:8000/api/images/{image_id}/thumbnails/medium"
                }
            },
        "error": None,
        "processing_time_seconds": (datetime.datetime.now() - start_time).total_seconds()
    
    }
    images_db.append(image_info)
    logger.info(f"Image {image_id} processed successfully in {image_info['processing_time_seconds']:.2f} seconds")
    return image_info


#store image into memory
images_db = []

@app.get("/api/images")
def get_images():

    return images_db


@app.get("/api/images/{id}")
def get_image(id: str):
    for image in images_db:
        if image["data"]["image_id"] == id:
            return image
    raise HTTPException(status_code=404, detail="Image not found")



@app.get("/api/images/{id}/thumbnails/{size}")
def get_thumbnail(id: str, size: str):
    filepath = f"{THUMBNAIL_FOLDER}/{id}_{size}.jpg"
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    return FileResponse(filepath, media_type="image/jpeg")

@app.get("/api/stats")
def get_stats():
    total = len(images_db)
    failed = sum(1 for img in images_db if img["status"] == "failed")
    success_rate = f"{(total - failed) / total * 100:.2f}%"
                    
    total_time = 0
    for img in images_db:
        total_time = total_time + img["processing_time_seconds"]
    avg_time = total_time / total

    return{
        "total" : total,
        "failed" :failed,
        "success_rate": success_rate,
        "average_processing_time_seconds": avg_time    
        }
    
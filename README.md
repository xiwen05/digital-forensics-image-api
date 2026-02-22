# Digital Forensics Image Processing API

## Project Overview
This project is an image processing pipeline API that automatically processes images, generates thumbnails, extracts metadata, and provides analysis through API endpoints

## Installation steps
1. Install Python 3.12 and pip
2. clone the respository:
git clone https://github.com/xiwen05/digital-forensics-image-api.git
cd digital-forensics-image-api
3. Create and activate a virtual environment:
python3 -m venv HTX
source HTX/bin/activate
4. Install dependencies:
pip install fastapi uvicorn pillow transformers torch torchvision python-multipart
5. Run:
python3 -m uvicorn main:app --reload
6. open http://127.0.0.1:8000/docs


## API documentation
1. GET `/` - Health check
2. POST `/api/images` - Upload and process an image. supported formats: JPG, PNG
3. GET `/api/images` - List all processed images
4. GET `/api/images/{id}` - Get details of a specific image
5. GET `/api/images/{id}/thumbnails/{size}` - Get small or medium thumbnail
6. GET `/api/stats` - Get processing statistics


## Example usage (i.e. how to run the code)
Run the app and visit http://127.0.0.1:8000/docs in your browser to test all endpoints interactively using the Swagger UI.
### curl Examples
Upload an image:
curl -X POST "http://127.0.0.1:8000/api/images" -F "file=@photo.jpg"

Get all images:
curl "http://127.0.0.1:8000/api/images"

Get a specific image:
curl "http://127.0.0.1:8000/api/images/{id}"

Get a thumbnail:
curl "http://127.0.0.1:8000/api/images/{id}/thumbnails/small"
curl "http://127.0.0.1:8000/api/images/{id}/thumbnails/medium"

Get stats:
curl "http://127.0.0.1:8000/api/stats"


## Processing piepline explanation
1. Image is uploaded via POST /api/images
2. File type is validated (JPG and PNG only)
3. Image is saved to the image/ folder with a unique ID
4. AI caption is generated using the BLIP model from Hugging Face
5. Metadata is extracted (dimensions, format, file size, timestamp)
6. Two thumbnails are generated and saved to the thumbnails/ folder:
        Small: max 100x100 pixels
        Medium: max 300x300 pixels
7. All results are stored in memory and returned in the response

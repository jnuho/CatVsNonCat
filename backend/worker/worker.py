from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
import numpy as np

from cats.predict import test_image_url

app = FastAPI()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Item(BaseModel):
    cat_url: Optional[str] = None

class Response(BaseModel):
    cat_url: Optional[str] = None
    status: Optional[int] = None
    msg: Optional[str] = None

@app.get("/healthz")
async def read_root():
    return {"Hello": "World"}

@app.post("/worker/cat")
async def create_item(item: Item):
    try:
        if item.cat_url is None:
            raise HTTPException(status_code=400, detail="cat_url must be provided")

        # You can now access the cat_url with item.cat_url
        data = np.load('parameters.npz', allow_pickle=True)
        parameters = {key: data[key].item() for key in data}["parameters"]
        prediction = test_image_url(item.cat_url, parameters)

        logger.info(f"Prediction for {item.cat_url}: {prediction}")

        response = Response(cat_url=item.cat_url, status=200, msg=prediction)
        return response

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Application handling the startup and shutdown processes
# in an environment where pods are being frequently created and destroyed by the HPA.
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")

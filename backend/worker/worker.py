from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import numpy as np

from worker.cats.predict import test_image_url

app = FastAPI()

class Item(BaseModel):
    cat_url: Optional[str] = None

class Response(BaseModel):
    cat_url: Optional[str] = None
    status: Optional[int] = None
    msg: Optional[str] = None

@app.post("/worker/cat")
async def create_item(item: Item):
    # You can now access the cat_url with item.cat_url
    data = np.load('parameters.npz', allow_pickle=True)
    parameters = {key: data[key].item() for key in data}["parameters"]
    prediction = test_image_url(item.cat_url, parameters)

    # print(f"Prediction for {item.cat_url}: {prediction}")

    response = Response(cat_url=item.cat_url, status=200, msg=prediction)
    return response


"""Api views."""
from typing import Dict

from parser.convertor import Convertor
from parser.models import DataModel

from fastapi import FastAPI

app = FastAPI()


@app.post("/convert")
def read_item(data: DataModel) -> Dict:
    """View for API convert method."""
    convertor = Convertor(data)
    return {'output': convertor.get_humanized_data()}

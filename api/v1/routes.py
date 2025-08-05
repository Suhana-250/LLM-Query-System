from fastapi import APIRouter
from schemas.query import QueryRequest
from services.extractor import extract_data

router = APIRouter()

@router.post("/run")
def run_query(req: QueryRequest):
    return extract_data(req)

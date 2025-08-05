from schemas.query import QueryRequest
from models.model import answer_questions

def extract_data(req: QueryRequest):
    return {"answers": answer_questions(req.documents, req.questions)}

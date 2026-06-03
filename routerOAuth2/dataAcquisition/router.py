from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException, status
from .model import QuizResponse
from .utils import addQuizResponse, getQuizQuestions

router = APIRouter(
    prefix="/acquire"
)

@router.post("/quizResponses")
async def aggiungiRisultati(data: QuizResponse):
    addQuizResponse(data)
    return {"status": "success"}

@router.get("/quizQuestions")
async def prendiDomanda(q: int | None):
    if q is None:
        raise HTTPException(status_code=400, detail="Il parametro 'q' (ID domanda) è richiesto.")
    return getQuizQuestions(q)
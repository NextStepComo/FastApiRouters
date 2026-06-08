from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException, status
from .model import QuizResponse
from .utils import addQuizResponse, getQuizQuestions, getSchoolPositions, getSchoolPositionsNoProv, getAIResponse

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

@router.get("/scuolePosizione")
async def getPositions(provincia: str):
    if provincia is None:
        raise HTTPException(status_code=400, detail="Il parametro 'provincia' (provincia scuole da restituire) è richiesto.")
    return getSchoolPositions(provincia)

@router.post("/chat")
async def chiamataAI(messaggio: str):
    return getAIResponse(messaggio)
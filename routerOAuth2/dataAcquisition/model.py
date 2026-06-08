from pydantic import BaseModel

class QuizResponse (BaseModel):
    userID : int
    domanda : int
    risposta : int
class ChatRequest(BaseModel):
    inputText: str
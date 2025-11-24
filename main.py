from fastapi import FastAPI, HTTPException, Request
from typing import List
from database import messages_collection
from models import Message, Conversation

app = FastAPI()

# Convertir ObjectId a string xd
def mostrar_message(conv):
    return Message(**conv)

@app.get("/mensajes", response_model=List[Message])
async def get_messages():
    try:
        print("mensajes")
        docs = list(messages_collection.find())   # Trae todos los documentos
        return [mostrar_message(doc) for doc in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mensajes/{session_id}", response_model=Message)
async def get_conversation(session_id: str):
    try:
        print("mensajes de session_id")
        doc = messages_collection.find_one({"sessionId": session_id})
        if not doc:
            raise HTTPException(status_code=404, detail="Conversación no encontrada")
        return mostrar_message(doc)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/sessions", response_model=list[Conversation])
async def get_session():
    try:
        print("sessiones")
        docs = messages_collection.find({}, {"sessionId": 1, "_id": 0})
        sessions = [Conversation(sessionId=doc["sessionId"]) for doc in docs]

        if not sessions:
            raise HTTPException(status_code=404, detail="SessionId de Conversacion no encontrado")
        
        return sessions
    except Exception as a:
        raise HTTPException(status_code=500, detail=str(a))
    

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8001)

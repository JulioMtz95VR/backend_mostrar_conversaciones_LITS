from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from database import messages_collection
from models import Message, Conversation
from dotenv import load_dotenv
import os

load_dotenv()
FRONTEND_URL = os.getenv("FRONTEND_URL")

app = FastAPI()

# Configuracion de CORS para hablar con el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
async def get_sessions(
     page: int = Query(1, ge=1),
     limit: int = Query(20, le=100)
):
        try:
             print(f"Cargando Sessions... Pagina: {page}, Límite: {limit}")
             skip = (page - 1) * limit

             # Consulta optimizada a MongoDB
             cursor = messages_collection.find({}, {"sessionId": 1, "_id": 0}).skip(skip).limit(limit)

             docs = list(cursor)

             # Convertimos a lista de objetos
             sessions = [Conversation(sessionId=doc["sessionId"]) for doc in docs]

             return sessions
        
        except Exception as a:
           raise HTTPException(status_code=500, detail=str(a))
    

from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from database import messages_collection
from models import ChatSession, ConversationSummary
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

# 1. Endpoint para la lista de sesiones 
# Devolviendo: SessionId, Nombre y Contacto
@app.get("/sessions", response_model=List[ConversationSummary])
async def get_session(
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100),
    search: Optional[str] = Query(None)
):
    try:
        print(f"Cargando sessions.. Pagina: {page}, Limite, {limit}")

        skip = (page -1) * limit

        # Contruimos el fltro de Mongo
        mongo_filter = {}

        if search:
            # Busca coincidencias en sessionID o en name
            mongo_filter = {
                "$or": [
                    {"sessionId": {"$regex": search, "$options": "i"}},
                    {"name": {"$regex": search, "$options": "i"}}
                ]
            }
        # Consulta optimizada
        # 1. Proyección: Solo traemos lo necesario (sessionId, name, contact_info)
        # 2. Sort: _id -1 muestra los más recientes primero
        cursor = messages_collection.find(
            mongo_filter,
            {"sessionId": 1, "name": 1, "contact_info": 1, "_id": 0}
        ).sort("_id", -1).skip(skip).limit(limit)

        docs = list(cursor)

        # Convertimos a la lista de objetos ConversationSummary
        sessions = []
        for doc in docs:
            sessions.append(ConversationSummary(
                sessionId=doc["sessionId"],
                # Usamos .get() por si el cambio no existe en chats viejos
                name=doc.get("name", "Desconocido"),
                contact_info=doc.get("contact_info", None)
            ))
        return sessions
        
    except Exception as a:
        import traceback
        # Esta linea imprime un error y lo muestra en la terminal
        traceback.print_exc() 
        print(f"ERROR EN SESSIONS: {a}")
        raise HTTPException(status_code=500, detail=str(a))


# 2. Endppoint que detalla la conversacion (Chat Principal)
@app.get("/mensajes/{session_id}", response_model=ChatSession)
async def get_conversation(session_id: str):
    try:
        print(f"Buscando mensajes de: {session_id}")
        # Buscamos el documento completo
        doc = messages_collection.find_one({"sessionId": session_id})
        if not doc:
            raise HTTPException(status_code=404, detail="Conversación no encontrada")
        # IMPORTANTE: Convertir ObjectId de Mongo a string
        if "_id" in doc:
            doc["id"] = str(doc["_id"])
        # Pydantic se encarga de validar la estructura anidada (messages -> data -> content)
        return ChatSession(**doc)
        
    except Exception as e:
        import traceback
        traceback.print_exc() 
        print(f"ERROR CRÍTICO EN CHAT ID {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 3. Endpoint para las dev tools
@app.get("/mensajes", response_model=List[ChatSession])
async def get_all_messages():
    try:
        # Limitamos a 50 por seguridad para no explotar la memoria
        docs = list(messages_collection.find().limit(50)) 
        
        result = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            result.append(ChatSession(**doc))
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002)

    
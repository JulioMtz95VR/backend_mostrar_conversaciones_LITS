from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Any, Dict

# Este modelo es la estructura interna de 'data' donde vive el texto
# es vital para que el frontend reciba el contenido de los mensajes limpio
class MessageData(BaseModel):
    content: str
    additional_kwargs: Dict[str, Any] | None = {}

    class Config:
        extra = "ignore"

# Este modelo es para un mensaje individual
class SingleMessage(BaseModel):
    type: str
    data: MessageData # Aqui usamos el modelo estricto en vez de 'dict'

    class Config:
        extra = "ignore"

# Este modelo es la session completa (El documento de MongoDB)
# Antes se llamaba 'Message' se renombra para evitar confusion
class ChatSession(BaseModel):
    id: str | None = None # Esto es para mapear el _id de Mongo
    sessionId: str 
    messages: List[SingleMessage] = []
    created_at: datetime | None = None
    name: str | None = "Desconocido"
    contact_info: str | None = None

    class Config:
        extra = "ignore"

# Este modelo es para la lista de resumen del endpoint de /sessions
class ConversationSummary(BaseModel):
    sessionId: str
    name: str = "Desconocido"
    contact_info: str | None = None

    class Config:
        extra = "ignore"
    
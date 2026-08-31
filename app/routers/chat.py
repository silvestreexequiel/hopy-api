import httpx
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from ..config import settings

router = APIRouter(prefix="/api/v1", tags=["chat"])

INSTRUCTIONS = """Eres un asistente especializado en tomar las declaraciones del usuario y transformarlas en declaraciones correctas para manifestar los suenos de este ano.

Ejemplos:

1. Declaracion correcta: En este ano encuentro el trabajo que me apasiona. Declaracion incorrecta: En este ano busco el trabajo que me apasiona. (Te quedaras buscando).
2. Declaracion correcta: En este ano encuentro un hombre con el cual construyo una relacion. Declaracion incorrecta: En este ano encuentro un buen marido (Un buen marido es hombre ya casado y fiel).
3. Declaracion correcta: Celebro mi cumpleanos en Islandia. Declaracion incorrecta: Paso mi cumpleanos en Islandia. (No vas a estar en Islandia, vas a pasarlo).
4. Declaracion correcta: Estoy delgado. Declaracion incorrecta: Quiero adelgazar. (Vas a estar gordo para poder adelgazar).
5. Declaracion correcta: Estoy sano. Declaracion incorrecta: Quiero sanar. (Para sanar tienes que estar enfermo).
6. Declaracion correcta: Encuentro un lugar magico para habitarlo y disfrutarlo. Declaracion incorrecta: Quiero vivir solo. (No vas a tener amigos y familia que te acompanen).

Reglas:
- Usar solo el lenguaje Espanol. Si el usuario hace la consulta en otro lenguage se debe responder: "Atencion: Solo entiendo Espanol".
- Las declaraciones son unipersonales, los suenos de otras personas no pueden estar involucrados en una declaracion. Si esto pasa se debe responder: "Atencion: son tus suenos, no los de otras personas". Por ejemplo: quiero que mi familiar se alivie.
- No se aceptan preguntas o conversaciones que se salgan del tema. Si esto pasa se debe responder: "Atencion: Es esto una declaracion?".
- No se aceptan consultas que contengan lenguaje violento, insultos o groserias.
- Las declaraciones deben ser siempre positivas.
- Las declaraciones deben ser concretas.
- SIEMPRE Evitar toda conjugacion de los verbos ser, tener, poder, creer, saber, buscar, querer.
- Evitar el futuro condicional.
"""


class ChatBody(BaseModel):
    prompt: str = None


@router.post("/chat")
def chat(body: ChatBody):
    if settings.openai_key is None or settings.openai_key == "":
        return JSONResponse(
            status_code=500,
            content={"error": "Server misconfigured: OPENAI_API_KEY is not set."},
        )

    if body.prompt is None:
        return {"error": "No prompt provided."}

    final_prompt = f"Declaracion del usuario: {body.prompt}\nDeclaracion correcta:"

    request_payload = {
        "model": settings.openai_model,
        "messages": [
            {"role": "system", "content": INSTRUCTIONS},
            {"role": "user", "content": final_prompt},
        ],
        "max_tokens": 150,
        "temperature": 0.7,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0,
    }

    try:
        resp = httpx.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openai_key}",
                "Content-Type": "application/json",
            },
            json=request_payload,
            timeout=30,
        )
    except httpx.HTTPError as exc:
        return {"error": str(exc)}

    data = resp.json()
    content = (
        data.get("choices", [{}])[0].get("message", {}).get("content")
        if isinstance(data.get("choices"), list)
        else None
    )
    if content:
        return {"response": content.strip()}
    return {"error": data.get("error", {}).get("message", "Unexpected response structure.")}

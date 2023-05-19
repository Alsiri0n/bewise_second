from fastapi import APIRouter


api = APIRouter()


# User request to internal API
@api.post("/register")
async def qnt_questions() -> dict:
    
    return {"message": "Hello world"}
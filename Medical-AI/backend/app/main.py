from fastapi import FastAPI


from app.api.medical import router
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI(

    title="Medical AI",

    version="1.0"

)
app.add_middleware(

CORSMiddleware,

allow_origins=[
"http://localhost:5173"
],

allow_credentials=True,

allow_methods=["*"],

allow_headers=["*"],

)



app.include_router(
    router
)



@app.get("/")
def home():

    return {

        "message":
        "Medical AI API running"

    }
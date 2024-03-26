from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.requests import Request
from presentation import chat
from config import PORT
import json

## 
app = FastAPI(docs_url=None, redoc_url=None)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # origins, ["*"] origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# routers
api_router = APIRouter()  # prefix=f"/{API_PREFIX}")
api_router.include_router(chat.router, prefix="/chat")

app.include_router(api_router)


@app.get("/")
async def main():
    return {"message": "Hello World (SHOULD NOT SHOW)"}


from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html

# protecting docs
from fastapi.security import HTTPBasic, HTTPBasicCredentials, OAuth2PasswordBearer

security = HTTPBasic()


def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = "dev"
    correct_password = "Foxconn1234"
    if (
        credentials.username != correct_username
        or credentials.password != correct_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/docs", include_in_schema=False)
async def get_documentation(username: str = Depends(get_current_username)):
    # return app.openapi()
    return get_swagger_ui_html(openapi_url="/openapi.json", title="Streaming API")


@app.get("/redoc", include_in_schema=False)
async def custom_redoc_html(username: str = Depends(get_current_username)):
    return get_redoc_html(
        openapi_url="./openapi.json",
        title="Streaming API",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(PORT),
        log_level="info",
        workers=1,
    )

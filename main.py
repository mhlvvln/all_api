from fastapi import FastAPI, HTTPException, Request
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from users.router import user_router
from tests.router import test_router
from tests.router import alerts_router
from topics.router import topics_router


app = FastAPI(title="API E-notGPT",
              description="Получение информации о User<br><h3>Токен админа</h3> - eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1IiwiZW1haWwiOiJtaGx2dmxuQGdtYWlsLmNvbSIsInJvbGUiOiJhZG1pbiIsImV4cCI6MTcwMjIyNzczMH0.UFptttFJwxa_gSYWQdvQ3rjiDvZ6F7I4T1BcQ_L6MRw<br><br><br><h3>Токен юзера</h3> - eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0IiwiZW1haWwiOiJ1c2VyQGV4YW1wbGUuY29tIiwicm9sZSI6InVzZXIiLCJleHAiOjE3MDIyMjc5NDd9.oCvTJPmLzBsCuLSXQbblKEKaPc7bvsc_o2j_bJvip48")

app.include_router(user_router, prefix="/users")
app.include_router(test_router, prefix="/tests")
app.include_router(alerts_router, prefix="/alerts")
app.include_router(topics_router, prefix="/topics")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def unicorn_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": False, "error": exc.detail},
    )

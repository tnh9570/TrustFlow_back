from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from web import deployments, session, hospital, deployVersions, excludedDirectories
from logging_config import setup_logging
import logging

setup_logging() 

app = FastAPI()

origins = [
    "http://192.168.100.171:5173",  # 프론트엔드 IP 주소를 명확하게 설정
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # 허용할 출처 목록
    allow_credentials=True,      # 쿠키 등 인증정보 허용 여부
    allow_methods=["*"],         # 허용할 HTTP 메서드 (GET, POST 등)
    allow_headers=["*"],         # 허용할 HTTP 헤더
)

app.include_router(deployments.router)
app.include_router(session.router)
app.include_router(hospital.router)
app.include_router(deployVersions.router)
app.include_router(excludedDirectories.router)

logger = logging.getLogger("app")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True, log_config=None)

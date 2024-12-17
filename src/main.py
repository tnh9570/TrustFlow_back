from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from web import deployments, session, hospital, deployVersions, excludedDirectories
from logging_config import setup_logging
import logging

setup_logging() 

app = FastAPI()
app.include_router(deployments.router)
app.include_router(session.router)
app.include_router(hospital.router)
app.include_router(deployVersions.router)
app.include_router(excludedDirectories.router)

logger = logging.getLogger("app")

# 허용할 도메인 (origin), credentials 여부, 허용 메서드, 헤더 설정
origins = [
    "*"
    # "http://localhost:3000",  # 프론트엔드 개발 서버 도메인
    # "https://example.com",    # 실제 배포된 도메인
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # 허용할 출처 목록
    allow_credentials=True,      # 쿠키 등 인증정보 허용 여부
    allow_methods=["*"],         # 허용할 HTTP 메서드 (GET, POST 등)
    allow_headers=["*"],         # 허용할 HTTP 헤더
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True, log_config=None)

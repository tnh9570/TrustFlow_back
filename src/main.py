from fastapi import FastAPI
from web import deployments, session, hospital, deployVersions
from logging_config import setup_logging
from state import session_data
import logging

setup_logging() 

app = FastAPI()
app.include_router(deployments.router)
app.include_router(session.router)
app.include_router(hospital.router)
app.include_router(deployVersions.router)

logger = logging.getLogger("app")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True, log_config=None)

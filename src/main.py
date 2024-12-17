from fastapi import FastAPI
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True, log_config=None)

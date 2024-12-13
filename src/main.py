from fastapi import FastAPI
from web import creature, explorer, deployments, session
from logging_config import setup_logging
from state import session_data
import logging

setup_logging() 

app = FastAPI()
app.include_router(explorer.router)
app.include_router(creature.router)
app.include_router(deployments.router)
app.include_router(session.router)

logger = logging.getLogger("app")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True, log_config=None)

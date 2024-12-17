# service/deployment.py
from model.hospital import Hospital
import logging
from state import session_data

class HospitalsService:
    def __init__(self):
        self.logger = logging.getLogger("app.service.HospitalsService")

    async def list_hospitals(self) -> list[Hospital]:
        self.logger.debug("Starting list_hospitals service method")
        
        results = [Hospital(hospitalId=hospitalId, hospitalName=hospitalName) for (hospitalId, hospitalName) in session_data.items()]

        return results
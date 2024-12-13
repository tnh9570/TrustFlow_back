# service/deployment.py
from datetime import datetime
from pymysql.connections import Connection
from model.hospital import Hospital
import logging
from state import session_data

class HospitalsService:
    def __init__(self):
        self.logger = logging.getLogger("app.service.HospitalsService")

    def list_hospitals(self) -> list[Hospital]:
        self.logger.debug("Starting list_hospitals service method")
        
        results = [Hospital(hospital_id=hospitalId, hospital_name=hospitalName) for (hospitalId, hospitalName) in session_data.items()]

        return results
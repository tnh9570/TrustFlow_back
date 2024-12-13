from pydantic import BaseModel


class Hospital(BaseModel):
    hospital_id: str
    hospital_name: str

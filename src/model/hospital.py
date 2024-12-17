from pydantic import BaseModel


class Hospital(BaseModel):
    hospitalId: str
    hospitalName: str

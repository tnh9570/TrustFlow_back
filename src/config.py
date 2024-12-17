from pydantic_settings import BaseSettings

class DatabaseSettings(BaseSettings):
    host: str
    port: int
    user: str
    password: str
    name: str

class Settings(BaseSettings):
    MEDIPLOYDB: DatabaseSettings
    MMSDB: DatabaseSettings

    MMS_AUTHORIZATION: str

    TEST: bool

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "_"  # 변수 이름을 네임스페이스로 구분

# Settings 인스턴스 생성
settings = Settings()

# # 환경변수 확인
# print(settings.MEDIPLOYDB.model_dump())  
# print(settings.MMSDB.model_dump())  
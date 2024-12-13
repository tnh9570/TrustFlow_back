from config import settings, DatabaseSettings
from pymysql.connections import Connection
import pymysql
import logging

from typing import Generator
"""
config.py 안으로
"""
def get_connection(db_settings: DatabaseSettings) -> Connection:
    """
    데이터베이스 설정을 기반으로 pymysql 커넥션 생성
    """
    return pymysql.connect(
        host=db_settings.host,
        port=db_settings.port,
        user=db_settings.user,
        password=db_settings.password,
        database=db_settings.name,
        cursorclass=pymysql.cursors.DictCursor,
    )

def get_mediploy_connection() -> Generator[Connection, None, None]:
    """
    MEDIPLOYDB 커넥션 생성기
    """
    logging.debug("MEDIPLOYDB connection generate")
    print("MEDIPLOYDB connection generate")
    conn = get_connection(settings.MEDIPLOYDB)
    try:
        logging.debug("MEDIPLOYDB connection ASDFASDF")
        print("MEDIPLOYDB connection ASDFASDF")
        yield conn
    finally:
        logging.debug("MEDIPLOYDB connection close")
        print("MEDIPLOYDB connection close")
        conn.close()

def get_mms_connection() -> Generator[Connection, None, None]:
    """
    MMSDB 커넥션 생성기
    """
    conn = get_connection(settings.MMSDB)
    try:
        yield conn
    finally:
        conn.close()
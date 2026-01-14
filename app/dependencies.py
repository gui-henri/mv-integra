import oracledb
from typing import Generator
from app.core.config import settings
from app.core.logger import logger

def get_db_connection() -> Generator[oracledb.Connection, None, None]:
    connection = None
    try:
        logger.debug("Attempting to connect to Oracle DB...")
        # explicitly enabling thin mode (default in 2.0+, but good to be explicit or leave default)
        logger.info(f"Oracle Client Lib Dir: {settings.ORACLE_CLIENT_LIB_DIR}")
        oracledb.init_oracle_client(
            lib_dir=settings.ORACLE_CLIENT_LIB_DIR
        )
        
        connection = oracledb.connect(
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            dsn=settings.DB_DSN
        )
        logger.debug("Successfully connected to Oracle DB")
        yield connection
    except oracledb.Error as e:
        logger.error(f"Error connecting to Oracle DB: {e}")
        raise
    finally:
        if connection:
            try:
                connection.close()
                logger.debug("Oracle DB connection closed")
            except oracledb.Error as e:
                logger.error(f"Error closing connection: {e}")

from sqlalchemy.orm import declarative_base
from urllib.parse import quote_plus
from ..env import getEnv, getEnvBool, getEnvInt
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from .db import async_session_injector_factory,AsyncSession

# need pip install sqlalchemy["asyncio"]
# need pip install aiomysql

def newAsyncMysqlEngine(user, password, host, port, db, options="", **kwargs)->AsyncEngine:
    password = quote_plus(password)
    return create_async_engine(f"mysql+aiomysql://{user}:{password}@{host}:{port}/{db}?{options}",**kwargs)




asyncMysqlEngineEnv = newAsyncMysqlEngine(getEnv('MYSQL_USER', 'root'), getEnv('MYSQL_PASSWORD'), getEnv('MYSQL_HOST', 'localhost'), 
                       getEnv('MYSQL_PORT', '3306'), getEnv('MYSQL_DB'), options= getEnv('MYSQL_OPTIONS'), echo=getEnvBool("MYSQL_ECHO" , False), 
                       echo_pool=getEnvBool("MYSQL_ECHO_POOL" , False), pool_recycle=getEnvInt('MYSQL_POOL_RECYCLE', 3600),
                        pool_pre_ping=True, pool_size=getEnvInt('MYSQL_POOL_SIZE', 100))

Base = declarative_base()

engines  = {
    'mysql': asyncMysqlEngineEnv
}

mysql_session = async_session_injector_factory(engines)
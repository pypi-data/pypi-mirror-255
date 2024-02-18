from sqlalchemy.orm import declarative_base
from urllib.parse import quote_plus
from ..env import getEnv, getEnvBool, getEnvInt
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncEngine
from .db import async_session_injector_factory,AsyncSession

# need pip install sqlalchemy["asyncio"]
# need pip install asyncpg

def newAsyncPostgreEngine(user, password, host, port, db,options="", **kwargs)->AsyncEngine:
    password = quote_plus(password)
    return create_async_engine(f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}?{options}",**kwargs)




asyncPostgreEngineEnv = newAsyncPostgreEngine(getEnv('POSTGRE_USER', 'postgre'), getEnv('POSTGRE_PASSWORD'), getEnv('POSTGRE_HOST', 'localhost'), 
                       getEnv('POSTGRE_PORT', '5432'), getEnv('POSTGRE_DB'), options=getEnv("POSTGRE_OPTIONS"))

Base = declarative_base()

engines  = {
    'postgre': asyncPostgreEngineEnv
}

postgre_session = async_session_injector_factory(engines)
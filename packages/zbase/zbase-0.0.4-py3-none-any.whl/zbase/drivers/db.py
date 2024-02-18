import logging
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession

import functools

def session_injector_factory(engines:dict):
    def sa_injector(tx=True,expunge_all=True):
        def decorator(func):
            varnames = func.__code__.co_varnames
            engine_dict = {varname:engines[varname] for varname in varnames if varname in engines}
            @functools.wraps(func)
            def wrapper(*args, **kw):
                sessions = []
                for k in engine_dict:
                    if k in kw:
                        continue
                    s = sessionmaker(engine_dict[k])()
                    kw[k] = s
                    sessions.append(s)
                try:
                    result = func(*args, **kw)
                    
                    for s in sessions:
                        if tx:
                            s.flush()
                        if expunge_all:
                            s.expunge_all()
                        if tx:
                            s.commit()
                    return result
                except Exception as e:
                    if tx:
                        for s in sessions:
                            s.rollback()
                    raise e
                finally:
                    for s in sessions:
                        s.close()
            return wrapper
        return decorator
    return sa_injector


def async_session_injector_factory(engines:dict):
    def sa_injector(tx=True,expunge_all=True):
        def decorator(func):
            varnames = func.__code__.co_varnames
            engine_dict = {varname:engines[varname] for varname in varnames if varname in engines}
            @functools.wraps(func)
            async def wrapper(*args, **kw):
                sessions = []
                for k in engine_dict:
                    if k in kw:
                        continue
                    s = async_sessionmaker(engine_dict[k])()
                    kw[k] = s
                    sessions.append(s)
                print("sessions",sessions , kw)
                try:
                    result = await func(*args, **kw)
                    
                    for s in sessions:
                        if tx:
                            await s.flush()
                        if tx:
                            await s.commit()
                    return result
                except Exception as e:
                    if tx:
                        for s in sessions:
                            await s.rollback()
                    raise e
                finally:
                    for s in sessions:
                        await s.close()
            return wrapper
        return decorator
    return sa_injector
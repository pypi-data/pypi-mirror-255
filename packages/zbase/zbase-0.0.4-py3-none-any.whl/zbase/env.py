import sys
from dotenv import load_dotenv
import os
load_dotenv()
load_dotenv(".env_default")


def getEnv(key, dv=None):
    return os.getenv(key, dv)


def getEnvBool(key, dv=None):
    v = os.getenv(key)
    if v is None:
        return dv
    return key.lower() in ['true', 'yes', '1','y']


def getEnvInt(key, dv=None):
    return int(os.getenv(key) or dv)


def getEnvFloat(key, dv=None):
    return float(os.getenv(key) or dv)


def getenvAsList(key, dv=None):
    return [key.strip() for key in os.getenv(key, dv).split(', ') if key.strip()]

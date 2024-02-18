from dotenv import load_dotenv
import os
from dataclasses import dataclass
from typing import List,Any,Dict

_dot_env_file = os.environ.get('DOT_ENV_FILE', '.env')
load_dotenv(_dot_env_file)

class ServiceException(Exception):
    def __init__(self, message: str, fieldErrors: Dict = None,errorCode:str=None,httpStatus:int=500):
        super().__init__(message)
        self.message = message
        self.fieldErrors = fieldErrors
        self.errorCode=errorCode
        self.httpStatus=httpStatus

@dataclass
class PageData:
    items: List[Any]
    totalCount: int
    pageSize: int
    pageIndex: int
    totalPages: int

def newPageData(items:List[Any],totalCount:int,pageSize:int,pageIndex:int)->PageData:
    return PageData(items=items,totalCount=totalCount,pageSize=pageSize,pageIndex=pageIndex,totalPages=totalCount//pageSize+1 if totalCount % pageSize > 0 else totalCount//pageSize)
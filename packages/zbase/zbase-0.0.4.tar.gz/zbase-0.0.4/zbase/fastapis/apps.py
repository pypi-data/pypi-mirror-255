from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse,PlainTextResponse
from fastapi.security import  OAuth2AuthorizationCodeBearer
# from fastapi.security.api_key import APIKeyHeader
from fastapi.exceptions import HTTPException
from dataclasses import dataclass
from ..env import getEnv
from typing import List
import jwt
from pydantic import BaseModel
from .. import ServiceException
from fastapi.middleware.cors import CORSMiddleware


import logging

@dataclass
class NewAppConfig:
    Prefix :str=""
    OAuthTokenEndpoint: str=None
    OAuthClientId: str=None
    OAuthClientSecret: str=None
    OAuthRedirectUri: str=None
    JwtPublicKey: str=None
    JwtAlg:str = "ES256"
    APIKeyName: str =None



class RBAC(OAuth2AuthorizationCodeBearer):
    """
    fetch OAUTH_AUTHORIZE_ENDPOINT, OAUTH_TOKEN_ENDPOINT from env
    @app.get("/iam/admin")
    async def admin(roles=Depends(RBAC(["ADMIN"]))):
        return f"hello admin. roles:{roles}"
    """
    def __init__(self, roles: List[str] = None,authorizationUrl=getEnv('OAUTH_AUTHORIZE_ENDPOINT'), tokenUrl=getEnv('OAUTH_TOKEN_ENDPOINT')):
        super(RBAC, self).__init__(authorizationUrl=authorizationUrl,tokenUrl=tokenUrl)
        self.roles = roles

    def __call__(self, request: Request):
        token = request.state.access_token
        if not token:
            raise HTTPException(
                status_code=401,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not self.roles:
            token_roles: str = token.get('roles')
            if token_roles:
                return token_roles.split(" ")
            return []
        token_roles: str = token.get('roles')
        if not token_roles:
            raise HTTPException(
                status_code=403,
                detail="Forbidden",
            )
        roles = token_roles.split(" ")
        if len(set(roles).intersection(self.roles)) == 0:
            raise HTTPException(
                status_code=403,
                detail="Forbidden",
            )
        return roles
    

class SBAC(OAuth2AuthorizationCodeBearer):
    """
    get OAUTH_AUTHORIZE_ENDPOINT, OAUTH_TOKEN_ENDPOINT from env by default
    @app.get("/iam/admin")
    async def admin(scope=Depends(SBAC(["email","icon"]))):
        return f"hello admin. scope:{scope}"
    """
    def __init__(self, scope: List[str] = None,authorizationUrl=getEnv('OAUTH_AUTHORIZE_ENDPOINT'),tokenUrl=getEnv('OAUTH_TOKEN_ENDPOINT')):
        super(SBAC, self).__init__(authorizationUrl=authorizationUrl,tokenUrl=tokenUrl)
        self.scope = scope

    def __call__(self, request: Request):
        token = request.state.access_token
        if not token:
            raise HTTPException(
                status_code=401,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not self.scope:
            token_roles: str = token.get('scope')
            if token_roles:
                return token_roles.split(" ")
            return []
        scope: str = token.get('scope')
        if not scope:
            raise HTTPException(
                status_code=403,
                detail="Forbidden",
            )
        scopes = scope.split(" ")
        if "*" in scopes:
            return scopes
        if len(set(scopes).intersection(self.scope)) == 0:
            raise HTTPException(
                status_code=403,
                detail="Forbidden",
            )
        return scopes

class ErrorResult(BaseModel):
    state:int=1
    error:str=None
    fieldErrors:dict=None
    request_path:str=None



class AppUtil:

    def __init__(self , prefix:str="") -> None:
        if prefix:
            prefix = "/"+prefix.strip("/")
        else:
            prefix = ""
        self.prefix = prefix
        self.app = FastAPI(docs_url=f"{prefix}/docs", openapi_url=f"{prefix}/openapi.json")

        self.setDefaultHandlers()

    def setDefaultHandlers(self):
        app = self.app

        @app.get(self.prefix + "/health")
        async def health():
            return PlainTextResponse("OK")

        @app.exception_handler(ServiceException)
        async def servcieExceptionHandler(request: Request, e: ServiceException):
            return await self.servcieExceptionHandler(request, e)
        
        @app.exception_handler(Exception)
        async def exceptionHandler(request: Request, e: Exception):
            return await self.exceptionHandler(request, e)

    async def exceptionHandler(self, request: Request, e: Exception):
        logging.error(e)
        return JSONResponse(ErrorResult(state=1,error=str(e),request_path=request.url.path).__dict__, status_code=500 )

    async def servcieExceptionHandler(self, request: Request, e: ServiceException):
        logging.error(e)
        return JSONResponse(ErrorResult(state=1,error=e.message,fieldErrors=e.fieldErrors, request_path=request.url.path).__dict__, status_code=e.httpStatus if e.httpStatus else 500)

    def setJWTBearerFilter(self,jwtPublicKey:str, algorithm:str="ES256"):
        jwtPublicKey = process_jwt_key(jwtPublicKey,algorithm)
        app = self.app
        @app.middleware("http")
        async def set_access_token(request: Request, call_next):
            auth = request.headers.get("Authorization")
            if not auth or not auth.startswith("Bearer "):
                request.state.access_token = None
                return await call_next(request)
            access_token = auth[7:]
            token = jwt.decode(access_token, jwtPublicKey, algorithms=[algorithm])
            request.state.access_token = token
            response = await call_next(request)
            return response
    def setCORS(self,allowOrigins:List[str], allow_methods=["*"], allow_headers=["*"], allow_credentials = True,**kwargs):
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=allowOrigins,
            allow_methods=allow_methods,
            allow_headers=allow_headers,
            allow_credentials=allow_credentials,
            **kwargs
        )
        
        

def process_jwt_key(jwtPublicKey:str ,algorithm:str)->str:
    if not jwtPublicKey.startswith("-----") and (algorithm.startswith("ES") or algorithm.startswith("RS")) or algorithm.startswith("HS"):
        jwtPublicKey= '-----BEGIN PUBLIC KEY-----\n'+getEnv("JWT_PUBLIC_KEY")+'\n-----END PUBLIC KEY-----'
    return jwtPublicKey


# def newApp(config:NewAppConfig)->FastAPI:
#     base = config.Prefix
#     if base:
#         base = "/"+config.Prefix.strip("/")
#     app = FastAPI(docs_url=f"{base}/docs", openapi_url=f"{base}/openapi.json")
#     @app.exception_handler(ServiceException)
#     async def unicorn_service_exception_handler(request: Request, e: ServiceException):
#         logging.error(e)
#         return JSONResponse(ErrorResult(state=1,error=e.message,fieldErrors=e.fieldErrors).__dict__, status_code=e.httpStatus if e.httpStatus else 500)


#     @app.exception_handler(Exception)
#     async def unicorn_exception_handler(request: Request, e: Exception):
#         logging.error(e)
#         return JSONResponse(ErrorResult(state=1,error=str(e)).__dict__, status_code=500)
    
#     @app.get(base + "/health")
#     async def health():
#         return JSONResponse(ErrorResult(state=0,data="OK").__dict__)
    
#     if config.OAuthClientId:
#         jwtPublicKey = config.JwtPublicKey
#         if not jwtPublicKey.startswith("-----") and (config.JwtAlg.startswith("ES") or config.JwtAlg.startswith("RS")) or config.JwtAlg.startswith("HS"):
#             jwtPublicKey= '-----BEGIN PUBLIC KEY-----\n'+getEnv("JWT_PUBLIC_KEY")+'\n-----END PUBLIC KEY-----'

#         @app.middleware("http")
#         async def set_access_token(request: Request, call_next):
#             auth = request.headers.get("Authorization")
#             if not auth or not auth.startswith("Bearer "):
#                 request.state.access_token = None
#                 return await call_next(request)
#             access_token = auth[7:]
#             token = jwt.decode(access_token, jwtPublicKey, algorithms=[config.JwtAlg])
#             request.state.access_token = token
#             response = await call_next(request)
#             return response



#         @app.get(base+"/oauth/callback")
#         async def oauth_callback(code: str, state: str):
#             form = {'code': code,
#                     'client_id': config.OAuthClientId,
#                     "client_secret": config.OAuthClientSecret,
#                     "grant_type": "authorization_code",
#                     "redirect_uri": config.OAuthRedirectUri
#                     }
#             async  with httpx.AsyncClient() as client:
#                 r = await client.post(config.OAuthTokenEndpoint, data=form)
#                 print(f"status: {r.status_code} , body:{r.text}")
#                 token = r.json()
#                 return RedirectResponse(
#                     state + "#access_token=" + token['access_token'] + "&refresh_token=" + token['refresh_token'])



#     return app
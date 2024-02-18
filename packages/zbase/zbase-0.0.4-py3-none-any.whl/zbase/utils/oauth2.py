import httpx
from dataclasses import dataclass

@dataclass
class AccessTokenResult:
    access_token:str
    refresh_token:str
    token_type:str
    expires_in:int
    scope:str


async def async_exchange(tokenEndpoint:str, clientId:str,clientSecret:str,code: str, state: str , redirect_uri: str = None)->AccessTokenResult:
    form = {'code': code,
            'client_id': clientId,
            "client_secret": clientSecret,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri
            }
    async with httpx.AsyncClient() as client:
        r = await client.post(tokenEndpoint, data=form)
        token = r.json()
        return AccessTokenResult(access_token=token.get('access_token'),
                                    refresh_token=token.get('refresh_token'),
                                    token_type=token.get('token_type'),
                                    expires_in=token.get('expires_in'),
                                    scope=token.get('scope'))

def exchange(tokenEndpoint:str, clientId:str,clientSecret:str,code: str, state: str , redirect_uri: str = None)->AccessTokenResult:
    form = {'code': code,
            'client_id': clientId,
            "client_secret": clientSecret,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri
            }
    with httpx.Client() as client:
        r = client.post(tokenEndpoint, data=form)
        token = r.json()
        return AccessTokenResult(access_token=token.get('access_token'),
                                    refresh_token=token.get('refresh_token'),
                                    token_type=token.get('token_type'),
                                    expires_in=token.get('expires_in'),
                                    scope=token.get('scope'))
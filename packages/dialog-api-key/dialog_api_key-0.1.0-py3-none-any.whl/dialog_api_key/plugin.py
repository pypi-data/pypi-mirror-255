from http import HTTPStatus
from typing import Annotated
from decouple import config, Csv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import APIKeyHeader


API_KEY_HEADER = config("API_KEY_HEADER", default="X-Api-Key")
API_KEYS = config("API_KEYS", cast=Csv(post_process=set))


api_key_header = APIKeyHeader(name=API_KEY_HEADER)


def verify_api_key(api_key: Annotated[str, Depends(api_key_header)]):
    if api_key not in API_KEYS:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid or missing API key."
        )


def register_plugin(app: FastAPI):
    app.router.dependencies.append(Depends(verify_api_key))

import base64
import urllib.parse

from pydantic.main import BaseModel

from airfold_common.type import Schema


class AIRequestParams(BaseModel):
    database: str
    table: str
    spec: str
    format: Schema
    message: str


def get_endpoint(host: str, params: AIRequestParams) -> str:
    """Get the endpoint for the AI server"""

    encoded_params: str = base64.b64encode(params.json().encode()).decode("utf-8")
    return f"{host}/api/v1/ai?params={urllib.parse.quote(encoded_params)}"

from pydantic import BaseModel


class Exchange(BaseModel):
    id: str
    enabled: bool = True
    api_key: str

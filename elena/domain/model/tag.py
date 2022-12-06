from pydantic import BaseModel


class Tag(BaseModel):
    id: str
    enabled: bool = True

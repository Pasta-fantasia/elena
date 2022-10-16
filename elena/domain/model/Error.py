from pydantic import BaseModel


class Error(BaseModel):
    message: str = ""

    def is_present(self) -> bool:
        return self.message != ""

    @staticmethod
    def none():
        return Error(message="")

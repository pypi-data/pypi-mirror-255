from typing import Optional, Any

from pydantic import BaseModel


class ResponseModel(BaseModel):
    message: Optional[str] = 'success'
    error_no: Optional[int] = 0
    data: Optional[Any]

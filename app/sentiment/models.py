from pydantic import BaseModel, Field

class Comment(BaseModel):
    text: str = Field(min_length=1, max_length=4000)
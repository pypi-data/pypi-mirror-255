from pydantic import BaseModel, field_validator

from notdiamond.exceptions import MissingApiKey, InvalidApiKey

class NDApiKeyValidator(BaseModel):
    api_key: str

    @field_validator('api_key', mode='before')
    def api_key_must_be_a_string(cls, v):
        if(type(v) != str):
            raise InvalidApiKey("ND API key should be a string")

        return v

    @field_validator('api_key', mode="after")
    def string_must_not_be_empty(cls, v):
        if(len(v) == 0):
            raise MissingApiKey("ND API key should be longer than 0")

        return v
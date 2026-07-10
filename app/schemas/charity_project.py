from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, PositiveInt, field_validator


class CharityProjectBase(BaseModel):
    name: str | None = Field(None, min_length=5, max_length=100)
    description: str | None = Field(None, min_length=10)
    full_amount: PositiveInt | None = None

    model_config = ConfigDict(extra='forbid')


class CharityProjectCreate(CharityProjectBase):
    name: str = Field(..., min_length=5, max_length=100)
    description: str = Field(..., min_length=10)
    full_amount: PositiveInt


class CharityProjectUpdate(CharityProjectBase):
    @field_validator('name')
    @classmethod
    def name_cannot_be_null(cls, project_name):
        if project_name is None:
            error = 'Имя проекта не может быть пустым!'
            raise ValueError(error)
        return project_name


class CharityProjectDB(CharityProjectCreate):
    id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

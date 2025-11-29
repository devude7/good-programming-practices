from pydantic import BaseModel
from typing import Optional


class MovieBase(BaseModel):
    title: str
    genres: str


class MovieCreate(MovieBase):
    movieId: int


class MovieUpdate(MovieBase):
    pass


class MovieRead(MovieBase):
    movieId: int
    class Config:
        orm_mode = True


class LinkBase(BaseModel):
    imdbId: str
    tmdbId: str


class LinkCreate(LinkBase):
    movieId: int


class LinkUpdate(LinkBase):
    pass


class LinkRead(LinkBase):
    movieId: int
    class Config:
        orm_mode = True


class RatingBase(BaseModel):
    userId: int
    movieId: int
    rating: float
    timestamp: int


class RatingCreate(RatingBase):
    pass


class RatingUpdate(BaseModel):
    rating: float
    timestamp: int


class RatingRead(RatingBase):
    id: int
    class Config:
        orm_mode = True


class TagBase(BaseModel):
    userId: int
    movieId: int
    tag: str
    timestamp: int


class TagCreate(TagBase):
    pass


class TagUpdate(BaseModel):
    tag: str
    timestamp: int


class TagRead(TagBase):
    id: int
    class Config:
        orm_mode = True
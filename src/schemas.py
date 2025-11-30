from pydantic import BaseModel, ConfigDict


class MovieBase(BaseModel):
    title: str
    genres: str


class MovieCreate(MovieBase):
    movieId: int


class MovieUpdate(MovieBase):
    pass


class MovieRead(MovieBase):
    movieId: int
    model_config = ConfigDict(from_attributes=True)


class LinkBase(BaseModel):
    imdbId: str
    tmdbId: str


class LinkCreate(LinkBase):
    movieId: int


class LinkUpdate(LinkBase):
    pass


class LinkRead(LinkBase):
    movieId: int
    model_config = ConfigDict(from_attributes=True)


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
    model_config = ConfigDict(from_attributes=True)


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
    model_config = ConfigDict(from_attributes=True)


class UserBase(BaseModel):
    username: str
    roles: list[str]


class UserCreate(BaseModel):
    username: str
    password: str
    roles: list[str]


class UserRead(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

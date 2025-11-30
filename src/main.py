from typing import List, Dict, Any

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.models import Movie, Link, Rating, Tag, User
from src.database import SessionLocal
from src.schemas import (
    MovieCreate, MovieRead, MovieUpdate,
    LinkCreate, LinkRead, LinkUpdate,
    RatingCreate, RatingRead, RatingUpdate,
    TagCreate, TagRead, TagUpdate,
    UserCreate, UserRead,
    LoginRequest, TokenResponse,
)

from src.utils.auth import (
    get_db,
    verify_password,
    hash_password,
    create_access_token,
    get_current_user,
    require_admin
)


app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"hello": "world"}


@app.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == data.username).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    roles = user.roles.split(",") if user.roles else []
    access_token = create_access_token({"sub": user.username, "roles": roles})
    return TokenResponse(access_token=access_token, token_type="bearer")


@app.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    roles_str = ",".join(user.roles)
    db_user = User(username=user.username, password_hash=hash_password(user.password), roles=roles_str)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    roles_list = db_user.roles.split(",") if db_user.roles else []
    return UserRead(id=db_user.id, username=db_user.username, roles=roles_list)


@app.get("/user_details")
def user_details(current_user: Dict[str, Any] = Depends(get_current_user)):
    return current_user


@app.get("/movies", response_model=List[MovieRead])
def get_movies(db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)):
    return db.query(Movie).all()


@app.post("/movies", response_model=MovieRead, status_code=status.HTTP_201_CREATED)
def create_movie(movie: MovieCreate, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)):
    db_movie = Movie(**movie.model_dump())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie


@app.get("/movies/{movie_id}", response_model=MovieRead)
def get_movie(movie_id: int, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)):
    db_movie = db.query(Movie).filter(Movie.movieId == movie_id).first()
    if not db_movie:
        raise HTTPException(status_code=404)
    return db_movie


@app.put("/movies/{movie_id}", response_model=MovieRead)
def update_movie(movie_id: int, movie: MovieUpdate, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)):
    db_movie = db.query(Movie).filter(Movie.movieId == movie_id).first()
    if not db_movie:
        raise HTTPException(status_code=404)
    db_movie.title = movie.title
    db_movie.genres = movie.genres
    db.commit()
    db.refresh(db_movie)
    return db_movie


@app.delete("/movies/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(movie_id: int, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)):
    db_movie = db.query(Movie).filter(Movie.movieId == movie_id).first()
    if not db_movie:
        raise HTTPException(status_code=404)
    db.delete(db_movie)
    db.commit()
    return None


@app.get("/links", response_model=List[LinkRead])
def get_links(db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)):
    return db.query(Link).all()


@app.post("/links", response_model=LinkRead, status_code=status.HTTP_201_CREATED)
def create_link(link: LinkCreate, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)):
    db_link = Link(**link.model_dump())
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link


@app.get("/links/{movie_id}", response_model=LinkRead)
def get_link(movie_id: int, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)):
    db_link = db.query(Link).filter(Link.movieId == movie_id).first()
    if not db_link:
        raise HTTPException(status_code=404)
    return db_link


@app.put("/links/{movie_id}", response_model=LinkRead)
def update_link(movie_id: int, link: LinkUpdate, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)):
    db_link = db.query(Link).filter(Link.movieId == movie_id).first()
    if not db_link:
        raise HTTPException(status_code=404)
    db_link.imdbId = link.imdbId
    db_link.tmdbId = link.tmdbId
    db.commit()
    db.refresh(db_link)
    return db_link


@app.delete("/links/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_link(movie_id: int, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)):
    db_link = db.query(Link).filter(Link.movieId == movie_id).first()
    if not db_link:
        raise HTTPException(status_code=404)
    db.delete(db_link)
    db.commit()
    return None


@app.get("/ratings", response_model=List[RatingRead])
def get_ratings(db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)):
    return db.query(Rating).all()


@app.post("/ratings", response_model=RatingRead, status_code=status.HTTP_201_CREATED)
def create_rating(rating: RatingCreate, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)):
    db_rating = Rating(**rating.model_dump())
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating


@app.get("/ratings/{rating_id}", response_model=RatingRead)
def get_rating(rating_id: int, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)):
    db_rating = db.query(Rating).filter(Rating.id == rating_id).first()
    if not db_rating:
        raise HTTPException(status_code=404)
    return db_rating


@app.put("/ratings/{rating_id}", response_model=RatingRead)
def update_rating(rating_id: int, rating: RatingUpdate, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)):
    db_rating = db.query(Rating).filter(Rating.id == rating_id).first()
    if not db_rating:
        raise HTTPException(status_code=404)
    db_rating.rating = rating.rating
    db_rating.timestamp = rating.timestamp
    db.commit()
    db.refresh(db_rating)
    return db_rating


@app.delete("/ratings/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rating(rating_id: int, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)):
    db_rating = db.query(Rating).filter(Rating.id == rating_id).first()
    if not db_rating:
        raise HTTPException(status_code=404)
    db.delete(db_rating)
    db.commit()
    return None


@app.get("/tags", response_model=List[TagRead])
def get_tags(db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)):
    return db.query(Tag).all()


@app.post("/tags", response_model=TagRead, status_code=status.HTTP_201_CREATED)
def create_tag(tag: TagCreate, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)):
    db_tag = Tag(**tag.model_dump())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


@app.get("/tags/{tag_id}", response_model=TagRead)
def get_tag(tag_id: int, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)):
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(status_code=404)
    return db_tag


@app.put("/tags/{tag_id}", response_model=TagRead)
def update_tag(tag_id: int, tag: TagUpdate, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)):
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(status_code=404)
    db_tag.tag = tag.tag
    db_tag.timestamp = tag.timestamp
    db.commit()
    db.refresh(db_tag)
    return db_tag


@app.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)):
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(status_code=404)
    db.delete(db_tag)
    db.commit()
    return None

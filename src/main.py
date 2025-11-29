from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .models import Movie, Link, Rating, Tag
from .database import SessionLocal
from .schemas import (
    MovieCreate, MovieRead, MovieUpdate,
    LinkCreate, LinkRead, LinkUpdate,
    RatingCreate, RatingRead, RatingUpdate,
    TagCreate, TagRead, TagUpdate
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()


@app.get("/")
def read_root():
    return {"hello": "world"}


@app.get("/movies", response_model=List[MovieRead])
def get_movies(db: Session = Depends(get_db)):
    return db.query(Movie).all()


@app.post("/movies", response_model=MovieRead, status_code=status.HTTP_201_CREATED)
def create_movie(movie: MovieCreate, db: Session = Depends(get_db)):
    db_movie = Movie(**movie.dict())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie


@app.get("/movies/{movie_id}", response_model=MovieRead)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    db_movie = db.query(Movie).filter(Movie.movieId == movie_id).first()
    if not db_movie:
        raise HTTPException(status_code=404)
    return db_movie


@app.put("/movies/{movie_id}", response_model=MovieRead)
def update_movie(movie_id: int, movie: MovieUpdate, db: Session = Depends(get_db)):
    db_movie = db.query(Movie).filter(Movie.movieId == movie_id).first()
    if not db_movie:
        raise HTTPException(status_code=404)
    db_movie.title = movie.title
    db_movie.genres = movie.genres
    db.commit()
    db.refresh(db_movie)
    return db_movie


@app.delete("/movies/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    db_movie = db.query(Movie).filter(Movie.movieId == movie_id).first()
    if not db_movie:
        raise HTTPException(status_code=404)
    db.delete(db_movie)
    db.commit()
    return None


@app.get("/links", response_model=List[LinkRead])
def get_links(db: Session = Depends(get_db)):
    return db.query(Link).all()


@app.post("/links", response_model=LinkRead, status_code=status.HTTP_201_CREATED)
def create_link(link: LinkCreate, db: Session = Depends(get_db)):
    db_link = Link(**link.dict())
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link


@app.get("/links/{movie_id}", response_model=LinkRead)
def get_link(movie_id: int, db: Session = Depends(get_db)):
    db_link = db.query(Link).filter(Link.movieId == movie_id).first()
    if not db_link:
        raise HTTPException(status_code=404)
    return db_link


@app.put("/links/{movie_id}", response_model=LinkRead)
def update_link(movie_id: int, link: LinkUpdate, db: Session = Depends(get_db)):
    db_link = db.query(Link).filter(Link.movieId == movie_id).first()
    if not db_link:
        raise HTTPException(status_code=404)
    db_link.imdbId = link.imdbId
    db_link.tmdbId = link.tmdbId
    db.commit()
    db.refresh(db_link)
    return db_link


@app.delete("/links/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_link(movie_id: int, db: Session = Depends(get_db)):
    db_link = db.query(Link).filter(Link.movieId == movie_id).first()
    if not db_link:
        raise HTTPException(status_code=404)
    db.delete(db_link)
    db.commit()
    return None


@app.get("/ratings", response_model=List[RatingRead])
def get_ratings(db: Session = Depends(get_db)):
    return db.query(Rating).all()


@app.post("/ratings", response_model=RatingRead, status_code=status.HTTP_201_CREATED)
def create_rating(rating: RatingCreate, db: Session = Depends(get_db)):
    db_rating = Rating(**rating.dict())
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating


@app.get("/ratings/{rating_id}", response_model=RatingRead)
def get_rating(rating_id: int, db: Session = Depends(get_db)):
    db_rating = db.query(Rating).filter(Rating.id == rating_id).first()
    if not db_rating:
        raise HTTPException(status_code=404)
    return db_rating


@app.put("/ratings/{rating_id}", response_model=RatingRead)
def update_rating(rating_id: int, rating: RatingUpdate, db: Session = Depends(get_db)):
    db_rating = db.query(Rating).filter(Rating.id == rating_id).first()
    if not db_rating:
        raise HTTPException(status_code=404)
    db_rating.rating = rating.rating
    db_rating.timestamp = rating.timestamp
    db.commit()
    db.refresh(db_rating)
    return db_rating


@app.delete("/ratings/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rating(rating_id: int, db: Session = Depends(get_db)):
    db_rating = db.query(Rating).filter(Rating.id == rating_id).first()
    if not db_rating:
        raise HTTPException(status_code=404)
    db.delete(db_rating)
    db.commit()
    return None


@app.get("/tags", response_model=List[TagRead])
def get_tags(db: Session = Depends(get_db)):
    return db.query(Tag).all()


@app.post("/tags", response_model=TagRead, status_code=status.HTTP_201_CREATED)
def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    db_tag = Tag(**tag.dict())
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


@app.get("/tags/{tag_id}", response_model=TagRead)
def get_tag(tag_id: int, db: Session = Depends(get_db)):
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(status_code=404)
    return db_tag


@app.put("/tags/{tag_id}", response_model=TagRead)
def update_tag(tag_id: int, tag: TagUpdate, db: Session = Depends(get_db)):
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(status_code=404)
    db_tag.tag = tag.tag
    db_tag.timestamp = tag.timestamp
    db.commit()
    db.refresh(db_tag)
    return db_tag


@app.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    db_tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not db_tag:
        raise HTTPException(status_code=404)
    db.delete(db_tag)
    db.commit()
    return None
